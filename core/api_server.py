from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

from core.factories import initialize_system
from core.config import get_watch_dirs, add_watch_dir, remove_watch_dir, CONFIG, save_config
from core.watcher import index_all

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
    top_k: int = 5

class SearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float

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
    Semantic search across all indexed documents.
    """
    try:
        cm = get_context_manager()
        results = cm.recursive_retrieve(request.query, top_k=request.top_k)
        
        formatted_results = []
        for res in results:
            formatted_results.append(SearchResult(
                content=res.get('content', ''),
                metadata={"source": res.get('uri', 'Unknown')},
                score=res.get('score', 0.0)
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
