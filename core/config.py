import os
import yaml
from pathlib import Path

CONFIG_PATH = Path("config.yaml")

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {"mode": "embedded"}

def save_config(config_data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(config_data, f, default_flow_style=False)

CONFIG = load_config()
WORKSPACE_DIR = Path(os.path.expanduser(CONFIG.get("workspace_dir", "~/ContextBridge_Workspace")))
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
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
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

def is_configured() -> bool:
    """
    检查 ContextBridge 是否已配置。
    
    Returns:
        True 如果配置文件存在且包含有效的 mode，否则 False
    """
    if not CONFIG_PATH.exists():
        return False
    
    config = load_config()
    return config.get("mode") is not None

def auto_configure(workspace_dir=None):
    """
    自动检测环境并生成配置。
    
    Args:
        workspace_dir: 可选的自定义工作区目录
        
    Returns:
        配置结果字典
    """
    from typing import Dict, Any, Optional
    
    # 检查是否已配置
    if is_configured():
        return {
            "status": "already_configured",
            "message": "ContextBridge is already configured",
            "config": CONFIG
        }
    
    # 检测外部服务
    from core.factories import detect_services
    services = detect_services()
    
    # 生成配置
    config_data = {
        "mode": "external" if (services.get("qmd_available") and services.get("openviking_available")) else "embedded",
        "workspace_dir": workspace_dir or str(Path.home() / "ContextBridge_Workspace"),
        "watch_dirs": [],
    }
    
    if services.get("qmd_available"):
        config_data["qmd"] = {
            "endpoint": services.get("qmd_endpoint", "http://localhost:9090"),
            "collection": "contextbridge_docs"
        }
    
    if services.get("openviking_available"):
        config_data["openviking"] = {
            "endpoint": services.get("openviking_endpoint", "http://localhost:8080"),
            "mount_path": "viking://contextbridge/"
        }
    
    # 保存配置
    save_config(config_data)
    
    return {
        "status": "success",
        "mode": config_data["mode"],
        "workspace": config_data["workspace_dir"],
        "message": f"ContextBridge configured in {config_data['mode']} mode"
    }

def init_workspace():
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    PARSED_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Ensure all watch dirs exist
    for d in get_watch_dirs():
        d.mkdir(parents=True, exist_ok=True)
        
    # Inject demo doc out of the box
    demo_doc = RAW_DOCS_DIR / "Welcome_to_ContextBridge.md"
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
            
        try:
            from core.factories import initialize_system
            cm = initialize_system()
            # Demo doc is .md, no need to copy to parsed_docs
            cm.write_context(demo_doc.name, demo_content, level="L2")
        except Exception as e:
            pass

    from core.i18n import i18n
    i18n.print("workspace_initialized", workspace=WORKSPACE_DIR, mode=CONFIG.get('mode', 'embedded'))
