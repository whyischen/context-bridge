from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

from core.factories import initialize_system
from core.config import get_watch_dirs, add_watch_dir, remove_watch_dir, CONFIG, save_config, PARSED_DOCS_DIR
from core.watcher import index_all
from core.utils.path_resolver import PathResolver

app = FastAPI(
    title="ContextBridge Local API",
    description="Local Knowledge Engine API for AI Agents (e.g., OpenClaw)",
    version="1.0.0"
)

# Initialize context manager lazily
_context_manager = None

def get_context_manager():
    global _context_manager
    if _context_manager is None:
        _context_manager = initialize_system()
    return _context_manager

# Models
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = None  # Use config default if not specified
    min_similarity: Optional[float] = None  # Use config default if not specified
    enable_rerank: Optional[bool] = True  # Enable advanced reranking by default
    explain: Optional[bool] = False  # Include detailed score breakdown

class SearchResult(BaseModel):
    uri: str
    filename: str
    abstract: str
    relevant_excerpts: List[str]
    score: float
    metadata: Dict[str, Any] = {}
    full_content_path: str = ""  # Path to full document content

class SearchResponse(BaseModel):
    results: List[SearchResult]

class WatchDirRequest(BaseModel):
    path: str

class WatchStatusResponse(BaseModel):
    watch_dirs: List[str]
    mode: str
    language: str

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Semantic search across all indexed documents with advanced reranking.
    
    Parameters:
    - query: Search query string
    - top_k: Number of results to return (uses config default if not specified)
    - min_similarity: Minimum similarity threshold (uses config default if not specified)
    - enable_rerank: Enable BM25 + keyword + position reranking (default: True)
    - explain: Include detailed score breakdown in metadata (default: False)
    """
    try:
        cm = get_context_manager()
        results = cm.recursive_retrieve(
            query=request.query, 
            top_k=request.top_k,
            min_similarity=request.min_similarity,
            enable_rerank=request.enable_rerank,
            explain=request.explain
        )
        
        # Initialize PathResolver
        path_resolver = PathResolver({
            'watch_dirs': get_watch_dirs(),
            'parsed_docs_dir': PARSED_DOCS_DIR
        })
        
        formatted_results = []
        for res in results:
            # Extract metadata if explain mode is enabled
            metadata = {}
            if request.explain:
                if 'score_breakdown' in res:
                    metadata['score_breakdown'] = res['score_breakdown']
                if 'matched_keywords' in res:
                    metadata['matched_keywords'] = res['matched_keywords']
                if 'query_terms' in res:
                    metadata['query_terms'] = res['query_terms']
            
            # Resolve file path
            filename = res.get('filename', 'Unknown')
            uri = res.get('uri', 'Unknown')
            full_content_path = ""
            
            try:
                full_content_path = path_resolver.resolve_path(filename, uri)
            except Exception as e:
                # Log error but continue with other results
                from core.utils.logger import get_logger
                logger = get_logger("api_server")
                logger.warning(f"Failed to resolve path for {filename}: {e}")
            
            formatted_results.append(SearchResult(
                uri=uri,
                filename=filename,
                abstract=res.get('abstract', ''),
                relevant_excerpts=res.get('relevant_excerpts', []),
                score=res.get('score', 0.0),
                metadata=metadata,
                full_content_path=full_content_path
            ))
            
        return SearchResponse(results=formatted_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/watch/status", response_model=WatchStatusResponse)
async def get_watch_status():
    """
    Get current watch directories and system status.
    """
    dirs = [str(d) for d in get_watch_dirs()]
    return WatchStatusResponse(
        watch_dirs=dirs,
        mode=CONFIG.get("mode", "embedded"),
        language=CONFIG.get("language", "zh")
    )

@app.post("/api/v1/watch/directories")
async def add_directory(request: WatchDirRequest, background_tasks: BackgroundTasks):
    """
    Add a new directory to watch and index.
    """
    success = add_watch_dir(request.path)
    if success:
        # Trigger re-indexing in background
        background_tasks.add_task(index_all)
        return {"status": "success", "message": f"Added {request.path} to watch list. Indexing started in background."}
    else:
        raise HTTPException(status_code=400, detail="Directory already in watch list or invalid path.")

@app.delete("/api/v1/watch/directories")
async def remove_directory(request: WatchDirRequest):
    """
    Remove a directory from watch list.
    """
    success = remove_watch_dir(request.path)
    if success:
        return {"status": "success", "message": f"Removed {request.path} from watch list."}
    else:
        raise HTTPException(status_code=404, detail="Directory not found in watch list.")

@app.post("/api/v1/index/sync")
async def trigger_index(background_tasks: BackgroundTasks):
    """
    Manually trigger a full index sync.
    """
    background_tasks.add_task(index_all)
    return {"status": "success", "message": "Indexing triggered in background."}

@app.get("/api/v1/health")
async def health_check():
    """
    Check if the API server is running.
    """
    return {"status": "healthy", "service": "ContextBridge API"}
