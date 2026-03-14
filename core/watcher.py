import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from core.config import RAW_DOCS_DIR, PARSED_DOCS_DIR, get_watch_dirs
from core.parser import parse_document
from core.factories import initialize_system
from tqdm import tqdm

class DocumentHandler(FileSystemEventHandler):
    def __init__(self, context_manager):
        self.context_manager = context_manager

    def process_file(self, file_path, event_type="created"):
        path = Path(file_path)
        if path.suffix.lower() in ['.docx', '.xlsx', '.pdf', '.pptx', '.md', '.txt']:
            if event_type == "deleted":
                print(f"File deleted: {path.name}")
                self.context_manager.delete_context(path.name)
                return

            print(f"File {event_type}: {path.name}")
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
        print("No files found to index.")
        return

    print(f"Found {len(all_files)} files. Starting initial indexing...")
    for path in tqdm(all_files, desc="Indexing files", unit="file"):
        content = parse_document(path)
        if content:
            parsed_path = PARSED_DOCS_DIR / f"{path.stem}.md"
            with open(parsed_path, "w", encoding="utf-8") as f:
                f.write(content)
            context_manager.write_context(path.name, content, level="L2")
    print("Indexing complete!")

def start_watching():
    context_manager = initialize_system()
    event_handler = DocumentHandler(context_manager)
    observer = Observer()
    
    watch_dirs = get_watch_dirs()
    for d in watch_dirs:
        observer.schedule(event_handler, str(d), recursive=True)
        print(f"Watching for document changes in {d}...")
        
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
