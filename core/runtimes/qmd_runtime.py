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
        self.client = None
        self.collection = None
        
        if self.mode == "embedded":
            try:
                logger.info("⚙️ Initializing embedded QMD engine (based on ChromaDB)...")
                from core.utils.model_downloader import ensure_chroma_model
                ensure_chroma_model()
                
                import chromadb
                from chromadb.config import Settings
                import os
                from pathlib import Path
                
                workspace_dir = Path(os.path.expanduser(config.get("workspace_dir", "~/.cbridge/workspace")))
                db_path = workspace_dir / "qmd_embedded"
                db_path.mkdir(parents=True, exist_ok=True)
                
                # Configure ChromaDB to use our custom models directory
                models_dir = Path.home() / ".cbridge" / "models"
                
                # Use new Chroma client initialization with Settings
                settings = Settings(
                    is_persistent=True,
                    persist_directory=str(db_path),
                    anonymized_telemetry=False,
                )
                
                self.client = chromadb.Client(settings)
                self.collection = self.client.get_or_create_collection(name=self.collection_name)
            except Exception as e:
                console.print(f"[bold red]Failed to initialize embedded QMD: {e}[/bold red]")
                logger.error(f"QMD initialization error: {e}", exc_info=True)
                raise
        else:
            logger.info(f"⚙️ Initializing external QMD: {self.endpoint}")
            self.client = None # 实际场景中这里会初始化 QMD SDK

    def upsert(self, collection_name: str, doc_id: str, vector: List[float], payload: Dict[str, Any]) -> bool:
        if self.mode == "embedded":
            try:
                if not self.collection:
                    logger.error("Collection not initialized")
                    return False
                # 模拟 QMD 的 upsert
                # ChromaDB 可以自动生成 embedding，这里我们简化处理，传入 text
                text = payload.pop("text", "")
                self.collection.upsert(
                    documents=[text],
                    metadatas=[payload],
                    ids=[doc_id]
                )
                return True
            except Exception as e:
                logger.error(f"Error upserting document {doc_id}: {e}", exc_info=True)
                return False
        else:
            logger.debug(f"📝 [QMD] External write: {doc_id}")
            return True

    def delete_by_uri(self, collection_name: str, uri: str) -> bool:
        if self.mode == "embedded":
            try:
                if not self.collection:
                    logger.error("Collection not initialized")
                    return False
                # ChromaDB supports deleting by where clause
                self.collection.delete(where={"uri": uri})
                return True
            except Exception as e:
                logger.error(f"Error deleting document with uri {uri}: {e}", exc_info=True)
                return False
        else:
            logger.debug(f"🗑️ [QMD] External delete: {uri}")
            return True

    def hybrid_search(self, collection_name: str, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.mode == "embedded":
            try:
                if not self.collection:
                    logger.error("Collection not initialized")
                    return []
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
            except Exception as e:
                logger.error(f"Error searching: {e}", exc_info=True)
                return []
        else:
            logger.debug(f"🔍 [QMD] External search: {query_text}")
            return []

    def get_all_metadatas(self, collection_name: str) -> List[Dict[str, Any]]:
        if self.mode == "embedded":
            try:
                if not self.collection:
                    logger.error("Collection not initialized")
                    return []
                results = self.collection.get(include=["metadatas"])
                if results and "metadatas" in results and results["metadatas"]:
                    return [meta for meta in results["metadatas"] if meta]
            except Exception as e:
                logger.error(f"Error getting metadatas from ChromaDB: {e}", exc_info=True)
            return []
        else:
            return []
