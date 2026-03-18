import time
import os
import queue
import threading
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from rich.console import Console
from core.config import RAW_DOCS_DIR, PARSED_DOCS_DIR, get_watch_dirs, CONFIG
from core.parser import parse_document, SUPPORTED_EXTENSIONS
from core.factories import initialize_system
from tqdm import tqdm
from core.i18n import t
from core.utils.logger import setup_logger

console = Console(stderr=True)
logger = setup_logger("cbridge-watcher")

def log_and_print(message, level="info"):
    """统一的日志输出函数：既显示在控制台也记录到日志文件"""
    # 记录到日志文件
    if level == "info":
        logger.info(message)
    elif level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "debug":
        logger.debug(message)
    
    # 如果是前台运行（终端可用），也显示在控制台
    import sys
    if sys.stdout.isatty():
        console.print(message)

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
                    log_and_print(t("watch_del", name=path.name))
                    context_manager.delete_context(path.name)
                elif action in ["created", "modified"]:
                    log_and_print(f"🔄 正在向量化: {path.name}")
                    content, error = parse_document(path)
                    if content:
                        log_and_print(f"✅ 向量化成功: {path.name}")
                        if path.suffix.lower() not in ['.md', '.txt']:
                            parsed_path = PARSED_DOCS_DIR / f"{path.stem}.md"
                            with open(parsed_path, "w", encoding="utf-8") as f:
                                f.write(content)
                        context_manager.write_context(path.name, content, level="L2")
                    else:
                        log_and_print(f"❌ 向量化失败: {path.name}", level="error")
                        log_and_print(f"   原因: {error}", level="error")
            except Exception as e:
                log_and_print(f"Error processing {file_path}: {e}", level="error")
                import traceback
                logger.error(traceback.format_exc())
            finally:
                task_queue.task_done()
    except Exception as e:
        log_and_print(f"Worker thread fatal error: {e}", level="error")
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

        # 检查文件大小（低性能设备优化）
        try:
            file_size_mb = path.stat().st_size / 1024 / 1024
            if file_size_mb > MAX_FILE_SIZE_MB:
                _resource_monitor["large_file_skips"] += 1
                log_and_print(f"⚠️  跳过大文件：{path.name} ({file_size_mb:.1f}MB > {MAX_FILE_SIZE_MB}MB)", level="warning")
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
            log_and_print(t("watch_event", event=ev_str, name=path.name))
        
        # 检查队列是否已满
        if task_queue.full():
            _resource_monitor["queue_drops"] += 1
            log_and_print(f"⚠️  任务队列已满，丢弃事件：{path.name}", level="warning")
            return
        
        # 非阻塞放入队列
        try:
            task_queue.put((event_type, file_path), block=False)
        except queue.Full:
            _resource_monitor["queue_drops"] += 1
            log_and_print(f"⚠️  任务队列已满，丢弃事件：{path.name}", level="warning")

    def on_created(self, event):
        if not event.is_directory:
            self._queue_task(event.src_path, "created")

    def on_modified(self, event):
        if not event.is_directory:
            self._queue_task(event.src_path, "modified")

    def on_deleted(self, event):
        if not event.is_directory:
            self._queue_task(event.src_path, "deleted")

def index_dir(directory: Path, show_progress=True):
    """Index a single directory and show progress."""
    context_manager = initialize_system()
    all_files = []
    
    # 扫描阶段
    if show_progress:
        log_and_print(f"📂 扫描文件夹: {directory}")
    
    for root, _, files in os.walk(directory):
        for f in files:
            path = Path(root) / f
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                all_files.append(path)

    if not all_files:
        log_and_print(t("idx_no_files"))
        return {"total": 0, "success": 0, "failed": 0, "failed_files": []}

    if show_progress:
        log_and_print(f"✅ 发现 {len(all_files)} 个文件")
        log_and_print(f"🔄 开始向量化...")
    
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
                logger.error(f"Failed to index {path.name}: {error}")
    
    if show_progress:
        log_and_print(f"✅ 向量化完成!")
        log_and_print(f"成功: {success_count} | 失败: {failed_count}")
    
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
        log_and_print(t("idx_ghost_clean", count=len(ghost_files)))
        for f in ghost_files:
            context_manager.delete_context(f)

    if not all_files:
        log_and_print(t("idx_no_files"))
        return

    log_and_print(t("idx_found", count=len(all_files)))
    for path in tqdm(all_files, desc=t("idx_progress"), unit="file"):
        content, error = parse_document(path)
        if content:
            # Only save to parsed_docs if conversion was needed (not .md or .txt)
            if path.suffix.lower() not in ['.md', '.txt']:
                parsed_path = PARSED_DOCS_DIR / f"{path.stem}.md"
                with open(parsed_path, "w", encoding="utf-8") as f:
                    f.write(content)
            context_manager.write_context(path.name, content, level="L2")
            tqdm.write(f"✅ {path.name}")
            logger.info(f"Successfully indexed: {path.name}")
        else:
            tqdm.write(f"❌ {path.name}  {error}")
            logger.error(f"Failed to index {path.name}: {error}")
    log_and_print(t("idx_complete"))

def start_watching():
    try:
        context_manager = initialize_system()
    except Exception as e:
        log_and_print(f"Failed to initialize system: {e}", level="error")
        import traceback
        logger.error(traceback.format_exc())
        return
    
    # 输出性能模式信息
    log_and_print(f"📊 性能模式：{PERFORMANCE_MODE.upper()}")
    log_and_print(f"   - 轮询间隔：{POLL_INTERVAL}秒")
    log_and_print(f"   - 防抖时间：{DEBOUNCE_SECONDS}秒")
    log_and_print(f"   - 最大文件大小：{MAX_FILE_SIZE_MB}MB")
    log_and_print(f"   - 任务队列大小：{MAX_QUEUE_SIZE}")
    log_and_print(f"   - Worker 线程数：{WORKER_THREADS}")
    
    # Start worker threads for async parsing
    worker_threads = []
    for i in range(WORKER_THREADS):
        worker_thread = threading.Thread(target=_worker_loop, args=(context_manager, i), daemon=True)
        worker_thread.start()
        worker_threads.append(worker_thread)
    log_and_print(f"✅ 已启动 {WORKER_THREADS} 个 worker 线程")
    
    event_handler = DocumentHandler(context_manager)
    observer = PollingObserver(timeout=POLL_INTERVAL)  # 使用配置的轮询间隔
    
    watched_dirs = set()

    def schedule_new_dirs():
        try:
            for d in get_watch_dirs():
                d = Path(d)
                if str(d) not in watched_dirs:
                    d.mkdir(parents=True, exist_ok=True)
                    observer.schedule(event_handler, str(d), recursive=True)
                    log_and_print(t("watch_dir", dir=d))
                    watched_dirs.add(str(d))
        except Exception as e:
            log_and_print(f"Error scheduling watch directories: {e}", level="error")
            import traceback
            logger.error(traceback.format_exc())

    schedule_new_dirs()
    observer.start()
    log_and_print("ContextBridge watcher started successfully")
    
    try:
        while True:
            time.sleep(POLL_INTERVAL)
            schedule_new_dirs()  # Periodically check for newly added watch dirs
    except KeyboardInterrupt:
        log_and_print("Shutting down...", level="warning")
        observer.stop()
        # 为每个 worker 发送停止信号
        for _ in worker_threads:
            task_queue.put(("stop", None))
    except Exception as e:
        log_and_print(f"Error in watch loop: {e}", level="error")
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
            log_and_print(f"📊 资源监控统计:")
            log_and_print(f"   - 队列丢弃事件：{_resource_monitor['queue_drops']}")
            log_and_print(f"   - 跳过大文件：{_resource_monitor['large_file_skips']}")
        log_and_print("✅ ContextBridge watcher stopped.")
