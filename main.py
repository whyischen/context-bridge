from core.config import init_workspace
from core.watcher import start_watching

if __name__ == "__main__":
    print("Initializing ContextBridge Workspace...")
    init_workspace()
    print("Starting ContextBridge Engine...")
    start_watching()
