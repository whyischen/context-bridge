import logging
import uuid
from typing import List, Dict, Any
from rich.console import Console
from core.interfaces.context_manager import IContextManager
from core.interfaces.search_runtime import ISearchRuntime
from core.i18n import t

logger = logging.getLogger(__name__)
console = Console(stderr=True)

class OpenVikingManager(IContextManager):
    def __init__(self, search_runtime: ISearchRuntime, config: dict):
        self.search_runtime = search_runtime
        self.mount_path = config.get("openviking", {}).get("mount_path", "viking://contextbridge/")
        self.collection_name = config.get("qmd", {}).get("collection", "cb_documents")
        
        logger.debug(f"Initializing embedded OpenViking manager, mount path: {self.mount_path}")

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

    def recursive_retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"🔍 [OpenViking] Recursive Searching: {query}")
            
            # Phase 1: 意图宽筛 (Search in L0 and L1)
            phase1_results = self.search_runtime.hybrid_search(
                collection_name=self.collection_name,
                query_text=query,
                top_k=3, 
                where={"level": {"$in": ["L0", "L1"]}}
            )
            
            if not phase1_results:
                return []
                
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
                top_k=top_k * 2, # 多捞一点便于组装
                where=where_clause
            )
            
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
                        
                assembled_context[uri]["relevant_excerpts"].append(chunk_text)
                
            return list(assembled_context.values())
        except Exception as e:
            logger.error(f"Error retrieving context for query '{query}': {e}", exc_info=True)
            return []

    def get_all_filenames(self) -> List[str]:
        try:
            metadatas = self.search_runtime.get_all_metadatas(self.collection_name)
            return [meta.get("filename") for meta in metadatas if "filename" in meta]
        except Exception as e:
            logger.error(f"Error getting all filenames: {e}", exc_info=True)
            return []
