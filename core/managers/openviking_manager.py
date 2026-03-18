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
        self.mode = config.get("mode", "embedded")
        self.mount_path = config.get("openviking", {}).get("mount_path", "viking://contextbridge/")
        self.endpoint = config.get("openviking", {}).get("endpoint", "http://localhost:9780")
        self.collection_name = config.get("qmd", {}).get("collection", "cb_documents")
        
        if self.mode == "embedded":
            console.print(t("ov_init_embed", mount_path=self.mount_path))
        else:
            console.print(t("ov_init_ext", endpoint=self.endpoint, mount_path=self.mount_path))

    def _generate_l0_abstract(self, content: str) -> str:
        # 模拟生成 L0 摘要 (实际应调用 LLM)
        return content[:100] + "..." if len(content) > 100 else content

    def _generate_l1_overview(self, content: str) -> str:
        # 模拟生成 L1 总览
        return content[:500] + "..." if len(content) > 500 else content

    def write_context(self, filename: str, content: str, level: str = "L2") -> bool:
        try:
            uri = f"{self.mount_path}{filename}"
            
            if self.mode == "embedded":
                # 减少日志噪音，只在调试模式下输出
                logger.debug(f"📝 [OpenViking] Processing context: {uri}")
                
                # 1. 生成分层上下文
                l0_abstract = self._generate_l0_abstract(content)
                l1_overview = self._generate_l1_overview(content)
                
                # 2. 存入底层检索运行时 (QMD)
                # Use deterministic doc_id based on URI to avoid duplicates on update
                import hashlib
                doc_id = hashlib.md5(uri.encode('utf-8')).hexdigest()
                payload = {
                    "uri": uri,
                    "filename": filename,
                    "l0_abstract": l0_abstract,
                    "l1_overview": l1_overview,
                    "text": content, # 实际中 L2 可能存在对象存储，这里简化存入向量库
                    "level": level
                }
                
                # 依赖注入：调用底层引擎
                return self.search_runtime.upsert(
                    collection_name=self.collection_name,
                    doc_id=doc_id,
                    vector=[], # 简化：由底层引擎自动生成
                    payload=payload
                )
            else:
                logger.debug(f"📝 [OpenViking] External write: {uri}")
                return True
        except Exception as e:
            logger.error(f"Error writing context for {filename}: {e}", exc_info=True)
            return False

    def delete_context(self, filename: str) -> bool:
        try:
            uri = f"{self.mount_path}{filename}"
            if self.mode == "embedded":
                logger.debug(f"🗑️ [OpenViking] Deleting context: {uri}")
                return self.search_runtime.delete_by_uri(self.collection_name, uri)
            else:
                logger.debug(f"🗑️ [OpenViking] External delete: {uri}")
                return True
        except Exception as e:
            logger.error(f"Error deleting context for {filename}: {e}", exc_info=True)
            return False

    def recursive_retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            if self.mode == "embedded":
                logger.debug(f"🔍 [OpenViking] Searching: {query}")
                
                # 1. 意图分析 (省略)
                # 2. 调用底层引擎寻找高分目录/文档
                results = self.search_runtime.hybrid_search(
                    collection_name=self.collection_name,
                    query_text=query,
                    top_k=top_k
                )
                
                # 3. 组装并返回最终上下文
                final_context = []
                for res in results:
                    metadata = res.get("metadata", {})
                    final_context.append({
                        "uri": metadata.get("uri", ""),
                        "content": res.get("text", ""),
                        "score": res.get("score", 0.0)
                    })
                return final_context
            else:
                logger.debug(f"🔍 [OpenViking] External search: {query}")
                return []
        except Exception as e:
            logger.error(f"Error retrieving context for query '{query}': {e}", exc_info=True)
            return []

    def get_all_filenames(self) -> List[str]:
        try:
            if self.mode == "embedded":
                metadatas = self.search_runtime.get_all_metadatas(self.collection_name)
                return [meta.get("filename") for meta in metadatas if "filename" in meta]
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting all filenames: {e}", exc_info=True)
            return []
