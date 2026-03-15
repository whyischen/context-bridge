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
            "# 欢迎使用 ContextBridge (Welcome to ContextBridge!)\n\n"
            "## 介绍 (Introduction)\n"
            "ContextBridge 是一款专为 AI 智能体打造的一站式本地记忆桥梁 (The All-in-One Local Memory Bridge for AI Agents)。\n"
            "它能够让您的本地 AI 智能体瞬间读取 Office 文档 (Word、Excel、PDF、PowerPoint 等)，并自动转化为高保真的 Markdown 内容。\n\n"
            "## 核心特性 (Key Features)\n"
            "- **实时目录监控 (Dynamic Monitoring)**: 自动感知文件新增、修改与删除，保持上下文永远最新。\n"
            "- **开箱即用 (Batteries Included)**: 内嵌 ChromaDB 检索引擎，零额外配置，本地向量搜索即刻生效。\n"
            "- **多语言界面 (i18n Support)**: 支持中英文命令行无缝切换。\n\n"
            "您可以尝试随时运行搜索指令，例如:\n"
            "> cbridge search ContextBridge\n"
        )
        with open(demo_doc, "w", encoding="utf-8") as f:
            f.write(demo_content)
            
        try:
            from core.factories import initialize_system
            cm = initialize_system()
            parsed_path = PARSED_DOCS_DIR / f"{demo_doc.stem}.md"
            with open(parsed_path, "w", encoding="utf-8") as pf:
                pf.write(demo_content)
            cm.write_context(demo_doc.name, demo_content, level="L2")
        except Exception as e:
            pass

    from core.i18n import i18n
    i18n.print("workspace_initialized", workspace=WORKSPACE_DIR, mode=CONFIG.get('mode', 'embedded'))
