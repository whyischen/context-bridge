import time
import os
import queue
import threading
import re
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from rich.console import Console
from core.config import RAW_DOCS_DIR, PARSED_DOCS_DIR, get_watch_dirs, CONFIG, add_watch_dir, remove_watch_dir
from core.parser import parse_document, SUPPORTED_EXTENSIONS
from core.factories import initialize_system
from tqdm import tqdm
from core.i18n import t
from core.utils.logger import get_logger

logger = get_logger("watcher")

# Removed log_and_print as it's now handled by the unified logger

# ============================================================================
# 性能优化配置
# ============================================================================

# 从配置文件读取性能参数
WATCHER_CONFIG = CONFIG.get("watcher", {})
PERFORMANCE_MODE = WATCHER_CONFIG.get("performance_mode", "balanced")  # low|balanced|high
POLL_INTERVAL = WATCHER_CONFIG.get("poll_interval", 5)
DEBOUNCE_SECONDS = WATCHER_CONFIG.get("debounce_seconds", 3)
MAX_FILE_SIZE_MB = WATCHER_CONFIG.get("max_file_size_mb", 50)
MAX_QUEUE_SIZE = WATCHER_CONFIG.get("max_queue_size", 1000)
WORKER_THREADS = WATCHER_CONFIG.get("worker_threads", 1)

# 根据性能模式调整参数
if PERFORMANCE_MODE == "low":
    # 低性能模式：最保守的设置
    POLL_INTERVAL = max(POLL_INTERVAL, 10)
    DEBOUNCE_SECONDS = max(DEBOUNCE_SECONDS, 5)
    MAX_FILE_SIZE_MB = min(MAX_FILE_SIZE_MB, 10)
    MAX_QUEUE_SIZE = min(MAX_QUEUE_SIZE, 100)
    WORKER_THREADS = 1
elif PERFORMANCE_MODE == "balanced":
    # 平衡模式：中等设置
    POLL_INTERVAL = max(POLL_INTERVAL, 5)
    DEBOUNCE_SECONDS = max(DEBOUNCE_SECONDS, 3)
    MAX_FILE_SIZE_MB = min(MAX_FILE_SIZE_MB, 50)
    MAX_QUEUE_SIZE = min(MAX_QUEUE_SIZE, 500)
    WORKER_THREADS = min(WORKER_THREADS, 2)
# high 模式使用配置文件中的值

# Global task queue for asynchronous parsing with size limit
task_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
_last_modified_times = {}

# 资源监控
_resource_monitor = {
    "queue_drops": 0,
    "large_file_skips": 0,
    "last_check": 0
}

def _worker_loop(context_manager):
    """Background worker to process files from the queue."""
    try:
        while True:
            try:
                action, file_path = task_queue.get()
                if action == "stop":
                    task_queue.task_done()
                    break
                
                path = Path(file_path)
                if action == "deleted":
                    logger.info(t("watch_del", name=path.name))
                    context_manager.delete_context(path.name)
                elif action in ["created", "modified"]:
                    logger.info(t("watch_vectorizing", name=path.name))
                    content, error = parse_document(path)
                    if content:
                        logger.info(t("watch_vectorize_success", name=path.name))
                        if path.suffix.lower() not in ['.md', '.txt']:
                            parsed_path = PARSED_DOCS_DIR / f"{path.stem}.md"
                            with open(parsed_path, "w", encoding="utf-8") as f:
                                f.write(content)
                        context_manager.write_context(path.name, content, level="L2")
                    else:
                        logger.error(t("watch_vectorize_failed", name=path.name))
                        logger.error(t("watch_vectorize_reason", error=error))
            except Exception as e:
                logger.error(t("watch_error_processing", file_path=file_path, error=e))
                import traceback
                logger.error(traceback.format_exc())
            finally:
                task_queue.task_done()
    except Exception as e:
        logger.error(t("watch_worker_fatal", error=e))
        import traceback
        logger.error(traceback.format_exc())

class DocumentHandler(FileSystemEventHandler):
    def __init__(self, context_manager):
        self.context_manager = context_manager

    def _queue_task(self, file_path, event_type):
        global _resource_monitor  # 必须在函数开头声明
        
        path = Path(file_path)
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return
            
        # Filter files to only those that are explicitly watched or inside watched dirs
        try:
            resolved_path = path.resolve()
            is_watched = False
            for d in get_watch_dirs():
                d_path = Path(d).resolve()
                if d_path.is_file() and resolved_path == d_path:
                    is_watched = True
                    break
                elif d_path.is_dir():
                    try:
                        resolved_path.relative_to(d_path)
                        is_watched = True
                        break
                    except ValueError:
                        pass
            if not is_watched:
                return
        except Exception:
            pass

        # 检查文件大小（低性能设备优化）
        try:
            file_size_mb = path.stat().st_size / 1024 / 1024
            if file_size_mb > MAX_FILE_SIZE_MB:
                _resource_monitor["large_file_skips"] += 1
                logger.warning(t("watch_skip_large_file", name=path.name, size=file_size_mb, max_size=MAX_FILE_SIZE_MB))
                return
        except (FileNotFoundError, PermissionError):
            return  # 文件不存在或无权限，跳过

        # Debounce logic for modify/create events
        if event_type in ["created", "modified"]:
            current_time = time.time()
            last_time = _last_modified_times.get(str(path), 0)
            if current_time - last_time < DEBOUNCE_SECONDS:
                return  # Ignore event, debounced
            _last_modified_times[str(path)] = current_time

        if event_type == "deleted":
            _last_modified_times.pop(str(path), None)
        else:
            ev_map = {"created": "create", "modified": "modify", "deleted": "delete"}
            ev_str = t(f"watch_ev_{ev_map.get(event_type, event_type)}")
            logger.info(t("watch_event", event=ev_str, name=path.name))
        
        # 检查队列是否已满
        if task_queue.full():
            _resource_monitor["queue_drops"] += 1
            logger.warning(t("watch_queue_full", name=path.name))
            return
        
        # 非阻塞放入队列
        try:
            task_queue.put((event_type, file_path), block=False)
        except queue.Full:
            _resource_monitor["queue_drops"] += 1
            logger.warning(t("watch_queue_full", name=path.name))

    def on_created(self, event):
        if not event.is_directory:
            self._queue_task(event.src_path, "created")

    def on_modified(self, event):
        if not event.is_directory:
            self._queue_task(event.src_path, "modified")

    def on_deleted(self, event):
        if not event.is_directory:
            self._queue_task(event.src_path, "deleted")

def index_dir(directory: Path, show_progress=True, skip_scan_log=False):
    """Index a single directory and show progress."""
    import warnings
    # Temporarily suppress general warnings like pydub to avoid spamming the progress bar
    warnings.filterwarnings("ignore")
        
    context_manager = initialize_system()
    all_files = []
        
    # 扫描阶段
    if show_progress and not skip_scan_log:
        logger.info(t("idx_scanning_dir", directory=directory))
    
    if directory.is_file():
        if directory.suffix.lower() in SUPPORTED_EXTENSIONS:
            all_files.append(directory)
    else:
        for root, _, files in os.walk(directory):
            for f in files:
                path = Path(root) / f
                if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    all_files.append(path)

    if not all_files:
        logger.info(t("idx_no_files"))
        return {"total": 0, "success": 0, "failed": 0, "failed_files": []}

    if show_progress and not skip_scan_log:
        logger.info(t("idx_files_found", count=len(all_files)))
        logger.info(t("idx_starting_vectorize"))
        
    logger.info("=" * 50)
    logger.info(f"开始索引向量数据: {directory}")
    logger.info(f"需要索引 {len(all_files)} 个文件")
    logger.info("=" * 50)
    
    success_count = 0
    failed_count = 0
    failed_files = []
    
    # 向量化阶段 - 减少输出噪音
    for path in tqdm(all_files, desc=t("idx_progress"), unit="file", disable=not show_progress):
        content, error = parse_document(path)
        if content:
            if path.suffix.lower() not in ['.md', '.txt']:
                parsed_path = PARSED_DOCS_DIR / f"{path.stem}.md"
                with open(parsed_path, "w", encoding="utf-8") as f:
                    f.write(content)
            context_manager.write_context(path.name, content, level="L2")
            success_count += 1
            # 只在详细模式下输出每个文件的成功信息
            # if show_progress:
            #     tqdm.write(f"[green]✅ {path.name}[/green]")
        else:
            failed_count += 1
            failed_files.append({"file": path.name, "error": error})
            # 失败时仍然输出，但简化错误信息
            if show_progress:
                error_short = error[:100] + "..." if len(error) > 100 else error
                tqdm.write(f"❌ {path.name} {error_short}")
                logger.error(t("idx_failed_log", name=path.name, error=error))
    
    if show_progress:
        logger.info(t("idx_vectorize_complete"))
        # Removed duplicate idx_summary log since caller prints it
        
    logger.info("=" * 50)
    logger.info("📊 索引汇总")
    logger.info(f"总文件数: {len(all_files)}")
    logger.info(f"成功: {success_count}")
    logger.info(f"失败: {failed_count}")
    logger.info("✅ 向量数据索引完成")
    logger.info("=" * 50)

    
    return {
        "total": len(all_files),
        "success": success_count,
        "failed": failed_count,
        "failed_files": failed_files
    }

def index_all():
    context_manager = initialize_system()
    watch_dirs = get_watch_dirs()
    
    all_files = []
    local_filenames = set()
    for d in watch_dirs:
        d_path = Path(d)
        if d_path.is_file():
            if d_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                all_files.append(d_path)
                local_filenames.add(d_path.name)
        else:
            for root, _, files in os.walk(d):
                for f in files:
                    path = Path(root) / f
                    if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                        all_files.append(path)
                        local_filenames.add(path.name)
                    
    # Clean up ghost data
    indexed_filenames = context_manager.get_all_filenames()
    ghost_files = [f for f in indexed_filenames if f not in local_filenames]
    if ghost_files:
        logger.info(t("idx_ghost_clean", count=len(ghost_files)))
        for f in ghost_files:
            context_manager.delete_context(f)

    if not all_files:
        logger.info(t("idx_no_files"))
        return

    logger.info(t("idx_found", count=len(all_files)))
    for path in tqdm(all_files, desc=t("idx_progress"), unit="file"):
        content, error = parse_document(path)
        if content:
            # Only save to parsed_docs if conversion was needed (not .md or .txt)
            if path.suffix.lower() not in ['.md', '.txt']:
                parsed_path = PARSED_DOCS_DIR / f"{path.stem}.md"
                with open(parsed_path, "w", encoding="utf-8") as f:
                    f.write(content)
            context_manager.write_context(path.name, content, level="L2")
            # 使用 logger 而不是 tqdm.write，避免后台进程的编码问题
            logger.info(t("idx_success_log", name=path.name))
        else:
            # 使用 logger 而不是 tqdm.write，避免后台进程的编码问题
            logger.error(t("idx_failed_log", name=path.name, error=error))
    logger.info(t("idx_complete"))

def start_watching():
    try:
        context_manager = initialize_system()
    except Exception as e:
        logger.error(t("watch_init_failed", error=e))
        import traceback
        logger.error(traceback.format_exc())
        return
    
    # 输出性能模式信息
    logger.info(t("watch_performance_mode", mode=PERFORMANCE_MODE.upper()))
    logger.info(t("watch_poll_interval", interval=POLL_INTERVAL))
    logger.info(t("watch_debounce_time", seconds=DEBOUNCE_SECONDS))
    logger.info(t("watch_max_file_size", size=MAX_FILE_SIZE_MB))
    logger.info(t("watch_queue_size", size=MAX_QUEUE_SIZE))
    logger.info(t("watch_worker_threads", count=WORKER_THREADS))
    
    # Start worker threads for async parsing
    worker_threads = []
    for i in range(WORKER_THREADS):
        worker_thread = threading.Thread(target=_worker_loop, args=(context_manager,), daemon=True)
        worker_thread.start()
        worker_threads.append(worker_thread)
    logger.info(t("watch_workers_started", count=WORKER_THREADS))
    
    event_handler = DocumentHandler(context_manager)
    observer = PollingObserver(timeout=POLL_INTERVAL)  # 使用配置的轮询间隔
    
    watched_dirs = set()

    def schedule_new_dirs():
        try:
            for d in get_watch_dirs():
                d_path = Path(d)
                watch_path = d_path.parent if d_path.is_file() else d_path
                
                if str(watch_path) not in watched_dirs:
                    if not watch_path.exists():
                        watch_path.mkdir(parents=True, exist_ok=True)
                    
                    # Schedule monitoring for the directory
                    # If the user specifically wanted to watch a file, we watch its parent but the event handler will filter
                    observer.schedule(event_handler, str(watch_path), recursive=not d_path.is_file())
                    logger.info(t("watch_dir", dir=watch_path))
                    watched_dirs.add(str(watch_path))
        except Exception as e:
            logger.error(t("watch_schedule_error", error=e))
            import traceback
            logger.error(traceback.format_exc())

    schedule_new_dirs()
    
    # Index existing documents on startup
    logger.info(t("watch_indexing_existing"))
    try:
        index_all()
    except Exception as e:
        logger.error(t("watch_index_failed", error=e))
        import traceback
        logger.error(traceback.format_exc())
    
    observer.start()
    logger.info(t("watch_started_success"))
    
    try:
        while True:
            time.sleep(POLL_INTERVAL)
            schedule_new_dirs()  # Periodically check for newly added watch dirs
    except KeyboardInterrupt:
        logger.warning("Shutting down...")
        observer.stop()
        # 为每个 worker 发送停止信号
        for _ in worker_threads:
            task_queue.put(("stop", None))
    except Exception as e:
        logger.error(t("watch_loop_error", error=e))
        import traceback
        logger.error(traceback.format_exc())
        observer.stop()
        # 为每个 worker 发送停止信号
        for _ in worker_threads:
            task_queue.put(("stop", None))
    finally:
        observer.join()
        # 等待所有 worker 线程结束
        for wt in worker_threads:
            wt.join()
        # 输出资源监控统计
        if _resource_monitor["queue_drops"] > 0 or _resource_monitor["large_file_skips"] > 0:
            logger.info(t("watch_resource_stats"))
            logger.info(t("watch_queue_drops", count=_resource_monitor['queue_drops']))
            logger.info(t("watch_large_file_skips", count=_resource_monitor['large_file_skips']))
# ============================================================================
# CLI Helper Wrappers
# ============================================================================

def list_monitored_dirs():
    """Proxy to config.get_watch_dirs returned as strings."""
    return [str(d) for d in get_watch_dirs()]

def add_monitored_dir(path: str):
    """Proxy to config.add_watch_dir."""
    return add_watch_dir(path)

def remove_monitored_dir(path: str):
    """Proxy to config.remove_watch_dir."""
    return remove_watch_dir(path)

def index_all_dirs():
    """Alias for search-friendly naming in CLI."""
    return index_all()
