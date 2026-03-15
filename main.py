from core.config import init_workspace
from core.watcher import start_watching
from core.i18n import i18n

if __name__ == "__main__":
    i18n.print("init_workspace")
    init_workspace()
    i18n.print("start_engine")
    start_watching()
