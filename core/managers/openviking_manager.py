import logging
import uuid
from typing import List, Dict, Any
from rich.console import Console
from core.interfaces.context_manager import IContextManager
from core.interfaces.search_runtime import ISearchRuntime
from core.i18n import t

from core.utils.logger import get_logger

logger = get_logger("viking")
console = Console(stderr=True)

class OpenVikingManager(IContextManager):
    def __init__(self, search_runtime: ISearchRuntime, config: dict):
        self.search_runtime = search_runtime
        self.config = config  # Store full config for optimizer access
        self.mount_path = config.get("openviking", {}).get("mount_path", "viking://contextbridge/")
        self.collection_name = config.get("qmd", {}).get("collection", "cb_documents")
        
        # Load search configuration
        search_config = config.get("search", {})
        self.default_min_similarity = search_config.get("min_similarity", 0.5)
        self.default_top_k = search_config.get("default_top_k", 5)
        
        logger.debug(f"Initializing embedded OpenViking manager, mount path: {self.mount_path}")
        logger.debug(f"Search config: min_similarity={self.default_min_similarity}, default_top_k={self.default_top_k}")

    def _generate_l0_abstract(self, content: str) -> str:
        # 兼容保留原有 API 形式，但不再使用
        return content[:100] + "..." if len(content) > 100 else content

    def _generate_l1_overview(self, content: str) -> str:
        # 兼容保留原有 API 形式，但不再使用
        return content[:500] + "..." if len(content) > 500 else content

    def write_context(self, filename: str, content: str, level: str = "L2") -> bool:
        try:
            uri = f"{self.mount_path}{filename}"
            
            logger.debug(f"📝 [OpenViking] Processing chunked context: {uri}")
            
            from core.utils.text_processor import HeuristicExtractor, MarkdownTextSplitter
            import hashlib
            
            l0_abstract = HeuristicExtractor.extract_l0_abstract(filename, content)
            l1_overview = HeuristicExtractor.extract_l1_outline(content)
            
            splitter = MarkdownTextSplitter(chunk_size=800, chunk_overlap=150)
            chunks = splitter.split_text(content)
            
            doc_ids = []
            vectors = []
            payloads = []
            
            base_id = hashlib.md5(uri.encode('utf-8')).hexdigest()
            
            # 1. 构造 L0 payload
            payloads.append({
                "uri": uri,
                "filename": filename,
                "l0_abstract": l0_abstract,
                "l1_overview": l1_overview,
                "text": l0_abstract,  
                "level": "L0",
                "chunk_id": "0"
            })
            doc_ids.append(f"{base_id}_L0")
            
            # 2. 构造 L1 payload
            payloads.append({
                "uri": uri,
                "filename": filename,
                "l0_abstract": l0_abstract,
                "l1_overview": l1_overview,
                "text": l1_overview, 
                "level": "L1",
                "chunk_id": "0"
            })
            doc_ids.append(f"{base_id}_L1")
            
            # 3. 构造 L2 payloads
            for idx, chunk in enumerate(chunks):
                payloads.append({
                    "uri": uri,
                    "filename": filename,
                    "l0_abstract": l0_abstract,
                    "l1_overview": "", # 避免 payload 爆炸
                    "text": chunk,
                    "level": "L2",
                    "chunk_id": str(idx + 1)
                })
                doc_ids.append(f"{base_id}_L2_{idx+1}")
                
            return self.search_runtime.upsert_batch(
                collection_name=self.collection_name,
                doc_ids=doc_ids,
                vectors=[[] for _ in range(len(doc_ids))],
                payloads=payloads
            )
        except Exception as e:
            logger.error(f"Error writing context for {filename}: {e}", exc_info=True)
            return False

    def delete_context(self, filename: str) -> bool:
        try:
            uri = f"{self.mount_path}{filename}"
            logger.debug(f"🗑️ [OpenViking] Deleting context: {uri}")
            return self.search_runtime.delete_by_uri(self.collection_name, uri)
        except Exception as e:
            logger.error(f"Error deleting context for {filename}: {e}", exc_info=True)
            return False

    def recursive_retrieve(
        self, 
        query: str, 
        top_k: int = None, 
        min_similarity: float = None,
        enable_rerank: bool = True,
        explain: bool = False
    ) -> List[Dict[str, Any]]:
        try:
            # Use configured defaults if not specified
            if top_k is None:
                top_k = self.default_top_k
            if min_similarity is None:
                min_similarity = self.default_min_similarity
            
            logger.debug(f"🔍 [OpenViking] Recursive Searching: {query}")
            logger.debug(f"Parameters: top_k={top_k}, min_similarity={min_similarity}, rerank={enable_rerank}, explain={explain}")
            
            # Phase 1: 意图宽筛 (Search in L0 and L1)
            phase1_results = self.search_runtime.hybrid_search(
                collection_name=self.collection_name,
                query_text=query,
                top_k=5,  # Increased to get more candidates
                where={"level": {"$in": ["L0", "L1"]}}
            )
            
            if not phase1_results:
                return []
            
            # Filter Phase 1 results by minimum similarity threshold
            phase1_results = [r for r in phase1_results if r.get("score", 0.0) >= min_similarity]
            
            if not phase1_results:
                logger.debug(f"No results passed Phase 1 similarity threshold ({min_similarity})")
                return []
            
            logger.debug(f"Phase 1: {len(phase1_results)} documents passed similarity threshold")
            for res in phase1_results[:3]:
                logger.debug(f"  - {res.get('metadata', {}).get('filename', 'unknown')}: score={res.get('score', 0.0):.3f}")
                
            # 提取高相关度的 URI
            matched_uris = set()
            uri_to_abstract = {}
            for res in phase1_results:
                meta = res.get("metadata", {})
                uri = meta.get("uri")
                if uri:
                    matched_uris.add(uri)
                    if uri not in uri_to_abstract and meta.get("l0_abstract"):
                        uri_to_abstract[uri] = meta.get("l0_abstract")
            
            if not matched_uris:
                return []
                
            # Phase 2: 细粒度打捞 (Search L2 chunks within matched URIs)
            where_clause = {
                "$and": [
                    {"level": "L2"},
                    {"uri": {"$in": list(matched_uris)}}
                ]
            }
            
            phase2_results = self.search_runtime.hybrid_search(
                collection_name=self.collection_name,
                query_text=query,
                top_k=top_k * 3, # 多捞一点便于组装
                where=where_clause
            )
            
            # Filter Phase 2 results by minimum similarity threshold
            phase2_results = [r for r in phase2_results if r.get("score", 0.0) >= min_similarity]
            
            # 3. 组装并返回最终级联上下文
            assembled_context = {}
            for res in phase2_results:
                meta = res.get("metadata", {})
                uri = meta.get("uri", "")
                chunk_text = res.get("text", "")
                score = res.get("score", 0.0)
                
                if uri not in assembled_context:
                    assembled_context[uri] = {
                        "uri": uri,
                        "filename": meta.get("filename", ""),
                        "abstract": uri_to_abstract.get(uri, meta.get("l0_abstract", "")),
                        "relevant_excerpts": [],
                        "score": score
                    }
                else:
                    # 保持最大分数
                    if score > assembled_context[uri]["score"]:
                        assembled_context[uri]["score"] = score
                
                # 避免重复的 L2 片段
                if chunk_text not in assembled_context[uri]["relevant_excerpts"]:
                    assembled_context[uri]["relevant_excerpts"].append(chunk_text)
            
            # Sort by score
            results = sorted(assembled_context.values(), key=lambda x: x["score"], reverse=True)
            results = results[:top_k * 2]  # Get more candidates for reranking
            
            # 4. Apply advanced reranking if enabled
            if enable_rerank and results:
                from core.utils.search_optimizer import SearchOptimizer
                
                # Get optimizer config from search config
                search_config = self.config.get("search", {})
                optimizer_config = search_config.get("optimizer", {})
                
                logger.debug(f"✨ Applying advanced reranking (BM25 + Keywords + Position)")
                results = SearchOptimizer.optimize_results(
                    query=query,
                    results=results,
                    config=optimizer_config,
                    explain=explain
                )
            
            # 5. Apply threshold filtering after reranking (scores may have changed)
            if min_similarity > 0.0:
                pre_filter_count = len(results)
                results = [r for r in results if r.get('score', 0.0) >= min_similarity]
                post_filter_count = len(results)
                if pre_filter_count > post_filter_count:
                    logger.debug(f"Filtered {pre_filter_count - post_filter_count} results after reranking (threshold: {min_similarity})")
            
            # 6. Return final top_k results
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error retrieving context for query '{query}': {e}", exc_info=True)
            return []

    def get_all_filenames(self) -> List[str]:
        try:
            metadatas = self.search_runtime.get_all_metadatas(self.collection_name)
            # Use set to deduplicate filenames (each file has multiple chunks)
            filenames = set()
            for meta in metadatas:
                if "filename" in meta:
                    filenames.add(meta["filename"])
            return list(filenames)
        except Exception as e:
            logger.error(f"Error getting all filenames: {e}", exc_info=True)
            return []
