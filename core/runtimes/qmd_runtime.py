import logging
from typing import List, Dict, Any
from rich.console import Console
from core.interfaces.search_runtime import ISearchRuntime
from core.i18n import t

logger = logging.getLogger(__name__)
console = Console(stderr=True)

class QMDRuntime(ISearchRuntime):
    def __init__(self, config):
        self.mode = config.get("mode", "embedded")
        self.endpoint = config.get("qmd", {}).get("endpoint", "http://localhost:9791")
        self.collection_name = config.get("qmd", {}).get("collection", "cb_documents")
        
        if self.mode == "embedded":
            console.print(t("qmd_init_embed"))
            from core.utils.model_downloader import ensure_chroma_model
            ensure_chroma_model()
            
            import chromadb
            import os
            from pathlib import Path
            
            workspace_dir = Path(os.path.expanduser(config.get("workspace_dir", "~/ContextBridge_Workspace")))
            db_path = workspace_dir / "qmd_embedded"
            db_path.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=str(db_path))
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
        else:
            console.print(t("qmd_init_ext", endpoint=self.endpoint, collection=self.collection_name))
            self.client = None # 实际场景中这里会初始化 QMD SDK

    def upsert(self, collection_name: str, doc_id: str, vector: List[float], payload: Dict[str, Any]) -> bool:
        if self.mode == "embedded":
            # 模拟 QMD 的 upsert
            # ChromaDB 可以自动生成 embedding，这里我们简化处理，传入 text
            text = payload.pop("text", "")
            self.collection.upsert(
                documents=[text],
                metadatas=[payload],
                ids=[doc_id]
            )
            return True
        else:
            console.print(t("qmd_write_ext", endpoint=self.endpoint, collection=collection_name, doc_id=doc_id))
            return True

    def delete_by_uri(self, collection_name: str, uri: str) -> bool:
        if self.mode == "embedded":
            # ChromaDB supports deleting by where clause
            self.collection.delete(where={"uri": uri})
            return True
        else:
            console.print(t("qmd_del_ext", endpoint=self.endpoint, collection=collection_name, uri=uri))
            return True

    def hybrid_search(self, collection_name: str, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.mode == "embedded":
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k
            )
            
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "score": results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
                    })
            return formatted_results
        else:
            console.print(t("qmd_search_ext", endpoint=self.endpoint, collection=collection_name, query=query_text))
            return []

    def get_all_metadatas(self, collection_name: str) -> List[Dict[str, Any]]:
        if self.mode == "embedded":
            try:
                results = self.collection.get(include=["metadatas"])
                if results and "metadatas" in results and results["metadatas"]:
                    return [meta for meta in results["metadatas"] if meta]
            except Exception as e:
                logger.error(f"Error getting metadatas from ChromaDB: {e}")
            return []
        else:
            return []
