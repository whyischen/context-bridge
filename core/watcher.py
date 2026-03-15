import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from core.config import RAW_DOCS_DIR, PARSED_DOCS_DIR, get_watch_dirs
from core.parser import parse_document
from core.factories import initialize_system
from tqdm import tqdm
from core.i18n import i18n

class DocumentHandler(FileSystemEventHandler):
    def __init__(self, context_manager):
        self.context_manager = context_manager

    def process_file(self, file_path, event_type="created"):
        path = Path(file_path)
        if path.suffix.lower() in ['.docx', '.xlsx', '.pdf', '.pptx', '.md', '.txt']:
            if event_type == "deleted":
                i18n.print("file_deleted", name=path.name)
                self.context_manager.delete_context(path.name)
                return

            i18n.print("file_event", event_type=event_type, name=path.name)
            content = parse_document(path)
            if content:
                # Save parsed markdown
                parsed_path = PARSED_DOCS_DIR / f"{path.stem}.md"
                with open(parsed_path, "w", encoding="utf-8") as f:
                    f.write(content)
                # 通过上下文管理器写入数据 (如 OpenViking)
                self.context_manager.write_context(path.name, content, level="L2")

    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path, "created")

    def on_modified(self, event):
        if not event.is_directory:
            self.process_file(event.src_path, "modified")

    def on_deleted(self, event):
        if not event.is_directory:
            self.process_file(event.src_path, "deleted")

def index_all():
    context_manager = initialize_system()
    watch_dirs = get_watch_dirs()
    
    all_files = []
    for d in watch_dirs:
        for root, _, files in os.walk(d):
            for f in files:
                path = Path(root) / f
                if path.suffix.lower() in ['.docx', '.xlsx', '.pdf', '.pptx', '.md', '.txt']:
                    all_files.append(path)
                    
    if not all_files:
        i18n.print("no_files_index")
        return

    i18n.print("found_files_index", count=len(all_files))
    for path in tqdm(all_files, desc=i18n.get("indexing_files"), unit="file"):
        content = parse_document(path)
        if content:
            parsed_path = PARSED_DOCS_DIR / f"{path.stem}.md"
            with open(parsed_path, "w", encoding="utf-8") as f:
                f.write(content)
            context_manager.write_context(path.name, content, level="L2")
    i18n.print("index_complete")

def start_watching():
    context_manager = initialize_system()
    event_handler = DocumentHandler(context_manager)
    observer = Observer()
    
    watch_dirs = get_watch_dirs()
    for d in watch_dirs:
        observer.schedule(event_handler, str(d), recursive=True)
        i18n.print("watching_dirs", dir=d)
        
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
