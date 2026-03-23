import os
import yaml
from pathlib import Path

CONFIG_PATH = Path(os.path.expanduser("~/.cbridge/config.yaml"))

def load_config():
    # Ensure config directory exists
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            # Ensure language defaults to English if not specified
            if "language" not in config:
                config["language"] = "en"
            # Ensure embedding config has defaults
            if "embedding" not in config:
                config["embedding"] = {
                    "model": "gte-small-zh"  # Default to GTE-Small-Zh
                }
            # Ensure search config has defaults
            if "search" not in config:
                config["search"] = {
                    "min_similarity": 0.5,  # Lower threshold for reranked results
                    "default_top_k": 5,
                    "optimizer": {
                        "semantic_weight": 0.40,
                        "bm25_weight": 0.30,
                        "keyword_weight": 0.15,
                        "position_weight": 0.10,
                        "title_weight": 0.05,
                        "bm25_k1": 1.5,
                        "bm25_b": 0.75
                    }
                }
            elif "optimizer" not in config["search"]:
                config["search"]["optimizer"] = {
                    "semantic_weight": 0.40,
                    "bm25_weight": 0.30,
                    "keyword_weight": 0.15,
                    "position_weight": 0.10,
                    "title_weight": 0.05,
                    "bm25_k1": 1.5,
                    "bm25_b": 0.75
                }
            # Update min_similarity if it's still at old default
            if config["search"].get("min_similarity", 0.5) == 0.5:
                config["search"]["min_similarity"] = 0.3
            return config
    return {
        "mode": "embedded", 
        "language": "en",
        "embedding": {
            "model": "gte-small-zh"  # Default to GTE-Small-Zh
        },
        "search": {
            "min_similarity": 0.3,  # Lower threshold for reranked results
            "default_top_k": 5,
            "optimizer": {
                "semantic_weight": 0.40,
                "bm25_weight": 0.30,
                "keyword_weight": 0.15,
                "position_weight": 0.10,
                "title_weight": 0.05,
                "bm25_k1": 1.5,
                "bm25_b": 0.75
            }
        }
    }

def save_config(config_data):
    # Ensure config directory exists
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(config_data, f, default_flow_style=False)

CONFIG = load_config()
WORKSPACE_DIR = Path(os.path.expanduser(CONFIG.get("workspace_dir", "~/.cbridge/workspace")))
RAW_DOCS_DIR = WORKSPACE_DIR / "raw_docs"
PARSED_DOCS_DIR = WORKSPACE_DIR / "parsed_docs"

# Support multiple watch directories
def get_watch_dirs():
    dirs = CONFIG.get("watch_dirs", [])
    if not dirs:
        # Default to RAW_DOCS_DIR if none specified
        dirs = [str(RAW_DOCS_DIR)]
    return [Path(os.path.expanduser(d)) for d in dirs]

def add_watch_dir(path_str):
    path = Path(os.path.expanduser(path_str)).absolute()
    
    dirs = CONFIG.get("watch_dirs", [str(RAW_DOCS_DIR.absolute())])
    if str(path) not in dirs:
        dirs.append(str(path))
        CONFIG["watch_dirs"] = dirs
        save_config(CONFIG)
        return True
    return False

def remove_watch_dir(path_str):
    path = Path(os.path.expanduser(path_str)).absolute()
    dirs = CONFIG.get("watch_dirs", [str(RAW_DOCS_DIR.absolute())])
    if str(path) in dirs:
        dirs.remove(str(path))
        CONFIG["watch_dirs"] = dirs
        save_config(CONFIG)
        return True
    return False

def init_workspace():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    PARSED_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Ensure all watch dirs exist
    for d in get_watch_dirs():
        if d.is_file():
            # If it explicitly exists as a file, skip mkdir
            continue
        try:
            d.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass
        
    # Inject demo doc out of the box
    demo_doc = RAW_DOCS_DIR / "Welcome_to_ContextBridge.md"
    demo_needs_indexing = False
    
    if not demo_doc.exists():
        demo_content = (
            "# Welcome to ContextBridge!\n\n"
            "## Introduction\n"
            "ContextBridge is a lightweight Knowledge Base plugin for AI Agents.\n"
            "It gives your local AI assistants instant access to read and understand your local Office documents (Word, Excel, PDF, etc.) directly into high-fidelity Markdown context.\n\n"
            "## Key Features\n"
            "- **Smart Folder Watcher**: Instantly detects file creations, modifications, and deletions to keep the context updated.\n"
            "- **Batteries Included**: Comes with an embedded search runtime, no need to manually install external vector databases.\n"
            "- **i18n Support**: Switch between English and Chinese command line seamlessly.\n\n"
            "You can try searching this right now by running:\n"
            "> cbridge search ContextBridge\n"
        )
        with open(demo_doc, "w", encoding="utf-8") as f:
            f.write(demo_content)
        demo_needs_indexing = True
            
    # Index demo doc if it was just created or check if it needs indexing
    if demo_needs_indexing:
        try:
            from core.factories import initialize_system
            import logging
            logger = logging.getLogger(__name__)
            
            cm = initialize_system()
            demo_content = demo_doc.read_text(encoding="utf-8")
            success = cm.write_context(demo_doc.name, demo_content, level="L2")
            
            if success:
                logger.info(f"✅ Demo document indexed: {demo_doc.name}")
            else:
                logger.warning(f"⚠️ Failed to index demo document: {demo_doc.name}")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Error indexing demo document: {e}", exc_info=True)

    from core.i18n import t
    from rich.console import Console
    console = Console(stderr=True)
    console.print(t("workspace_init", dir=WORKSPACE_DIR))


def get_search_config():
    """
    获取搜索配置参数
    
    Returns:
        dict: 包含 min_similarity 和 default_top_k 的字典
    """
    search_config = CONFIG.get("search", {})
    return {
        "min_similarity": search_config.get("min_similarity", 0.5),
        "default_top_k": search_config.get("default_top_k", 5)
    }

def update_search_config(min_similarity=None, default_top_k=None):
    """
    更新搜索配置参数
    
    Args:
        min_similarity: 最小相似度阈值 (0.0-1.0)
        default_top_k: 默认返回结果数量
    
    Returns:
        bool: 更新是否成功
    """
    if "search" not in CONFIG:
        CONFIG["search"] = {}
    
    if min_similarity is not None:
        if not 0.0 <= min_similarity <= 1.0:
            return False
        CONFIG["search"]["min_similarity"] = min_similarity
    
    if default_top_k is not None:
        if default_top_k < 1:
            return False
        CONFIG["search"]["default_top_k"] = default_top_k
    
    save_config(CONFIG)
    return True
