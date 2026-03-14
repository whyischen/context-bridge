import logging
import uuid
from typing import List, Dict, Any
from core.interfaces.context_manager import IContextManager
from core.interfaces.search_runtime import ISearchRuntime

logger = logging.getLogger(__name__)

class OpenVikingManager(IContextManager):
    def __init__(self, search_runtime: ISearchRuntime, config: dict):
        self.search_runtime = search_runtime
        self.mode = config.get("mode", "embedded")
        self.mount_path = config.get("openviking", {}).get("mount_path", "viking://contextbridge/")
        self.endpoint = config.get("openviking", {}).get("endpoint", "http://localhost:8080")
        self.collection_name = config.get("qmd", {}).get("collection", "cb_documents")
        
        if self.mode == "embedded":
            logger.info(f"初始化内嵌 OpenViking 管理器, 挂载路径: {self.mount_path}")
        else:
            logger.info(f"接入外部 OpenViking 服务: {self.endpoint}, 挂载路径: {self.mount_path}")

    def _generate_l0_abstract(self, content: str) -> str:
        # 模拟生成 L0 摘要 (实际应调用 LLM)
        return content[:100] + "..." if len(content) > 100 else content

    def _generate_l1_overview(self, content: str) -> str:
        # 模拟生成 L1 总览
        return content[:500] + "..." if len(content) > 500 else content

    def write_context(self, filename: str, content: str, level: str = "L2") -> bool:
        uri = f"{self.mount_path}{filename}"
        
        if self.mode == "embedded":
            logger.info(f"[OpenViking] 正在处理上下文: {uri}")
            
            # 1. 生成分层上下文
            l0_abstract = self._generate_l0_abstract(content)
            l1_overview = self._generate_l1_overview(content)
            
            # 2. 存入底层检索运行时 (QMD)
            doc_id = str(uuid.uuid4())
            payload = {
                "uri": uri,
                "filename": filename,
                "l0_abstract": l0_abstract,
                "l1_overview": l1_overview,
                "text": content, # 实际中 L2 可能存在对象存储，这里简化存入向量库
                "level": level
            }
            
            # 依赖注入：调用底层引擎
            self.search_runtime.upsert(
                collection_name=self.collection_name,
                doc_id=doc_id,
                vector=[], # 简化：由底层引擎自动生成
                payload=payload
            )
            return True
        else:
            logger.info(f"[外部 OpenViking] 模拟通过 API 将上下文写入 {uri}")
            return True

    def delete_context(self, filename: str) -> bool:
        uri = f"{self.mount_path}{filename}"
        if self.mode == "embedded":
            logger.info(f"[OpenViking] 正在删除上下文: {uri}")
            return self.search_runtime.delete_by_uri(self.collection_name, uri)
        else:
            logger.info(f"[外部 OpenViking] 模拟通过 API 删除上下文 {uri}")
            return True

    def recursive_retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.mode == "embedded":
            logger.info(f"[OpenViking] 执行目录递归检索策略: {query}")
            
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
            logger.info(f"[外部 OpenViking] 模拟向 {self.endpoint} 发起递归检索: {query}")
            return []
