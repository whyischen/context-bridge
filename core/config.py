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
        
    print(f"Workspace initialized at {WORKSPACE_DIR} in {CONFIG.get('mode', 'embedded')} mode")
