from typing import List, Dict, Any
from core.interfaces.search_runtime import ISearchRuntime
from core.i18n import i18n

class QMDRuntime(ISearchRuntime):
    def __init__(self, config):
        self.mode = config.get("mode", "embedded")
        self.endpoint = config.get("qmd", {}).get("endpoint", "http://localhost:9090")
        self.collection_name = config.get("qmd", {}).get("collection", "cb_documents")
        
        if self.mode == "embedded":
            i18n.print("qmd_init_embedded")
            import chromadb
            import os
            from pathlib import Path
            
            workspace_dir = Path(os.path.expanduser(config.get("workspace_dir", "~/ContextBridge_Workspace")))
            db_path = workspace_dir / "qmd_embedded"
            db_path.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=str(db_path))
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
        else:
            i18n.print("qmd_init_external", endpoint=self.endpoint, collection=self.collection_name)
            self.client = None # 实际场景中这里会初始化 QMD SDK

    def upsert(self, collection_name: str, doc_id: str, vector: List[float], payload: Dict[str, Any]) -> bool:
        if self.mode == "embedded":
            # 模拟 QMD 的 upsert
            # ChromaDB 可以自动生成 embedding，这里我们简化处理，传入 text
            text = payload.pop("text", "")
            self.collection.add(
                documents=[text],
                metadatas=[payload],
                ids=[doc_id]
            )
            return True
        else:
            i18n.print("qmd_write_ext", doc_id=doc_id)
            return True

    def delete_by_uri(self, collection_name: str, uri: str) -> bool:
        if self.mode == "embedded":
            # ChromaDB supports deleting by where clause
            self.collection.delete(where={"uri": uri})
            return True
        else:
            i18n.print("qmd_del_ext", uri=uri)
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
            i18n.print("qmd_ret_ext", query=query_text)
            return []
