#!/usr/bin/env python3
import sys
import click
import asyncio
from pathlib import Path
from rich.console import Console

from core.factories import initialize_system
from core.config import init_workspace, CONFIG, WORKSPACE_DIR, CONFIG_PATH, save_config, get_watch_dirs, add_watch_dir, remove_watch_dir
from core.watcher import start_watching, index_all, index_dir
from core.mcp_server import main as mcp_main
from core.i18n import t

console = Console(stderr=True)

@click.group(help=t("cli_desc"))
def cli():
    pass

@cli.command(help=t("init_desc"))
def init():
    import os
    import signal
    import shutil
    import subprocess
    import sys
    from pathlib import Path
    from core.utils.logger import setup_logger
    from core.watcher import start_watching
    
    console.print(t("init_welcome"))
    
    # Step 1: Check if configuration exists and ask to delete
    if CONFIG_PATH.exists():
        console.print(t("init_config_exists", path=CONFIG_PATH.absolute()))
        if click.confirm(t("init_config_delete_confirm"), default=True):
            CONFIG_PATH.unlink()
            console.print(t("init_config_deleted"))
            
            # Also clean up workspace if exists
            if WORKSPACE_DIR.exists():
                if click.confirm(t("init_workspace_delete_confirm", dir=WORKSPACE_DIR), default=False):
                    shutil.rmtree(WORKSPACE_DIR)
                    console.print(t("init_workspace_deleted"))
        else:
            console.print(t("init_cancelled"))
            return
    
    # Step 2: Stop any running services
    pid_file = Path.home() / ".cbridge" / "cbridge.pid"
    watcher_pid_file = Path.home() / ".cbridge" / "cbridge_watcher.pid"
    
    stopped_any = False
    
    # Stop watcher
    if watcher_pid_file.exists():
        try:
            pid = int(watcher_pid_file.read_text().strip())
            if sys.platform == "win32":
                import subprocess
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True, capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
            watcher_pid_file.unlink()
            console.print(t("init_stopped_watcher", pid=pid))
            stopped_any = True
        except (ProcessLookupError, subprocess.CalledProcessError, ValueError):
            watcher_pid_file.unlink()
        except PermissionError:
            console.print(t("init_stop_permission_error"))
    
    # Stop serve daemon
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            if sys.platform == "win32":
                import subprocess
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True, capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
            pid_file.unlink()
            console.print(t("init_stopped_serve", pid=pid))
            stopped_any = True
        except (ProcessLookupError, subprocess.CalledProcessError, ValueError):
            pid_file.unlink()
        except PermissionError:
            console.print(t("init_stop_permission_error"))
    
    if stopped_any:
        console.print(t("init_services_stopped"))
    
    # Step 3: Interactive configuration
    console.print(t("init_config_prompt"))
    
    lang = click.prompt(t("choose_lang"), type=click.Choice(['zh', 'en']), default='en')
    
    mode = click.prompt(t("choose_mode"), type=click.Choice(['embedded', 'external']), default='embedded')
    
    config_data = {"mode": mode, "language": lang, "watch_dirs": []}
    
    if mode == 'external':
        ov_endpoint = click.prompt(t("ov_endpoint"), default="http://localhost:9780")
        ov_mount = click.prompt(t("ov_mount"), default="viking://contextbridge/")
        qmd_endpoint = click.prompt(t("qmd_endpoint"), default="http://localhost:9791")
        qmd_collection = click.prompt(t("qmd_collection"), default="cb_documents")
        
        config_data["openviking"] = {
            "endpoint": ov_endpoint,
            "mount_path": ov_mount
        }
        config_data["qmd"] = {
            "endpoint": qmd_endpoint,
            "collection": qmd_collection
        }
    
    workspace = click.prompt(t("workspace_dir"), default="~/.cbridge/workspace")
    config_data["workspace_dir"] = workspace
    
    save_config(config_data)
    console.print(t("config_saved", path=CONFIG_PATH.absolute()))
    init_workspace()
    
    # Step 4: Start daemon automatically
    console.print(t("init_starting_daemon"))
    
    try:
        # 确保日志目录存在
        log_dir = Path.home() / ".cbridge" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 直接调用 start 函数，默认后台模式
        import subprocess
        import sys
        
        # 启动后台服务
        if sys.platform == "win32":
            # Windows: spawn a detached subprocess
            pid_file = Path.home() / ".cbridge" / "cbridge_watcher.pid"
            cmd = [sys.executable, "-m", "cbridge", "start"]
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            DETACHED_PROCESS = 0x00000008
            proc = subprocess.Popen(
                cmd,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            pid_file.parent.mkdir(parents=True, exist_ok=True)
            pid_file.write_text(str(proc.pid))
            console.print(f"[green]✅ ContextBridge watcher started in background (PID {proc.pid})[/green]")
        else:
            # Unix: traditional double-fork daemonize
            pid = os.fork()
            if pid > 0:
                pid_file = Path.home() / ".cbridge" / "cbridge_watcher.pid"
                pid_file.parent.mkdir(parents=True, exist_ok=True)
                pid_file.write_text(str(pid))
                console.print(f"[green]✅ ContextBridge watcher started in background (PID {pid})[/green]")
            else:
                # 子进程中启动服务
                os.chdir("/")
                os.setsid()
                os.umask(0)
                
                # 重定向输出到日志
                logger = setup_logger("cbridge-watcher")
                
                class LoggerWriter:
                    def __init__(self, log_func):
                        self.log_func = log_func
                    def write(self, msg):
                        if msg and msg.strip():
                            self.log_func(msg.strip())
                    def flush(self):
                        pass
                    def isatty(self):
                        return False
                
                sys.stdout = LoggerWriter(logger.info)
                sys.stderr = LoggerWriter(logger.error)
                
                # 启动监控服务
                init_workspace()
                start_watching()
                return
        
        console.print(f"[dim]📝 Logs: {log_dir / 'cbridge-watcher.log'}[/dim]")
        console.print(f"[dim]💡 Use 'cbridge logs -f' to view real-time logs[/dim]")
        console.print(f"[dim]💡 Use 'cbridge stop' to stop the watcher[/dim]")
        console.print(t("init_complete"))
        
    except Exception as e:
        console.print(t("init_daemon_failed", error=str(e)))

@cli.group(help=t("watch_desc"))
def watch():
    pass

@watch.command(name="list", help=t("watch_list_desc"))
def watch_list():
    dirs = get_watch_dirs()
    console.print(t("watch_list_title"))
    for d in dirs:
        console.print(f"  [green]•[/green] {d}")

@watch.command(name="add", help=t("watch_add_desc"))
@click.argument("path")
@click.option('--no-index', is_flag=True, help='仅添加到监控列表，不立即索引（后台执行时索引）')
@click.option('--quiet', '-q', is_flag=True, help='静默模式，减少日志输出')
@click.option('--background', '-b', is_flag=True, help='后台执行索引，立即返回')
def watch_add(path, no_index, quiet, background):
    import sys
    import os
    from pathlib import Path as PathLib
    
    if add_watch_dir(path):
        console.print(t("watch_add_success", path=path))
        
        if no_index:
            console.print()
            console.print("[green]✅ 文件夹已添加到监控列表[/green]")
            console.print("[dim]💡 提示: 使用 'cbridge start' 启动后台监控并自动索引[/dim]")
            console.print("[dim]💡 提示: 使用 'cbridge index' 手动索引所有文件[/dim]")
        else:
            # 统计文件数量
            console.print()
            console.print("[cyan]📂 正在扫描文件夹...[/cyan]")
            
            from core.parser import SUPPORTED_EXTENSIONS
            target_path = PathLib(path).absolute()
            
            # 扫描支持的文件
            all_files = []
            if target_path.is_file():
                if target_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    all_files.append(target_path)
            else:
                for root, _, files in os.walk(target_path):
                    for f in files:
                        file_path = PathLib(root) / f
                        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                            all_files.append(file_path)
            
            if not all_files:
                console.print("[yellow]⚠️  未发现支持的文件格式[/yellow]")
                console.print(f"[dim]支持的格式: {', '.join(SUPPORTED_EXTENSIONS)}[/dim]")
                return
            
            console.print(f"[green]✅ 发现 {len(all_files)} 个文件需要索引[/green]")
            
            # 如果指定了 background 参数，直接后台执行
            if background:
                console.print()
                console.print("[cyan]🚀 启动后台索引进程...[/cyan]")
                
                # 启动后台索引进程
                import subprocess
                
                # 构建后台命令
                cmd = [sys.executable, "-m", "cbridge", "index", "--path", str(target_path)]
                if quiet:
                    cmd.append("--quiet")
                
                try:
                    # 确保日志目录存在
                    from pathlib import Path
                    log_dir = Path.home() / ".cbridge" / "logs"
                    log_dir.mkdir(parents=True, exist_ok=True)
                    log_file = log_dir / "cbridge-watcher.log"
                    
                    # Windows 平台使用 creationflags 参数
                    if sys.platform == "win32":
                        with open(log_file, "a", encoding="utf-8") as f:
                            subprocess.Popen(cmd, 
                                           creationflags=subprocess.CREATE_NO_WINDOW,
                                           stdout=f, stderr=f)
                    else:
                        with open(log_file, "a", encoding="utf-8") as f:
                            subprocess.Popen(cmd, stdout=f, stderr=f)
                    
                    console.print("[green]✅ 文件夹已添加到监控列表，后台索引已启动[/green]")
                    console.print("[dim]💡 提示: 使用 'cbridge logs' 查看索引进度[/dim]")
                    console.print("[dim]💡 提示: 使用 'cbridge status' 查看系统状态[/dim]")
                except Exception as e:
                    console.print(f"[red]❌ 启动后台索引失败: {e}[/red]")
                    console.print("[yellow]⚠️  将改为前台执行索引...[/yellow]")
                    # 回退到前台执行
                    result = index_dir(target_path, show_progress=not quiet)
                    _display_index_summary(result, quiet)
            else:
                # 询问用户是否需要后台执行
                console.print()
                if len(all_files) > 10:  # 文件较多时建议后台执行
                    console.print("[yellow]💡 检测到文件数量较多，建议后台执行以避免阻塞[/yellow]")
                
                import click
                use_background = click.confirm(
                    "是否需要后台执行索引？(后台执行可立即返回，使用 'cbridge logs' 查看进度)",
                    default=len(all_files) > 10
                )
                
                if use_background:
                    console.print()
                    console.print("[cyan]🚀 启动后台索引进程...[/cyan]")
                    
                    # 启动后台索引进程
                    import subprocess
                    
                    # 构建后台命令
                    cmd = [sys.executable, "-m", "cbridge", "index", "--path", str(target_path)]
                    if quiet:
                        cmd.append("--quiet")
                    
                    try:
                        # Windows 平台使用 creationflags 参数
                        if sys.platform == "win32":
                            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
                        else:
                            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        
                        console.print("[green]✅ 文件夹已添加到监控列表，后台索引已启动[/green]")
                        console.print("[dim]💡 提示: 使用 'cbridge logs' 查看索引进度[/dim]")
                        console.print("[dim]💡 提示: 使用 'cbridge status' 查看系统状态[/dim]")
                    except Exception as e:
                        console.print(f"[red]❌ 启动后台索引失败: {e}[/red]")
                        console.print("[yellow]⚠️  将改为前台执行索引...[/yellow]")
                        # 回退到前台执行
                        result = index_dir(target_path, show_progress=not quiet)
                        _display_index_summary(result, quiet)
                else:
                    console.print()
                    console.print("[cyan]🔄 开始前台索引...[/cyan]")
                    # 执行向量化并显示进度
                    result = index_dir(target_path, show_progress=not quiet)
                    _display_index_summary(result, quiet)
                    
                    console.print()
                    console.print("[green]✅ 文件夹已添加到监控列表并完成索引[/green]")
                    console.print("[dim]💡 提示: 使用 'cbridge start' 启动后台监控[/dim]")
                    console.print("[dim]💡 提示: 使用 'cbridge logs' 查看实时日志[/dim]")
    else:
        console.print(t("watch_add_exists", path=path))

@watch.command(name="remove", help=t("watch_remove_desc"))
@click.argument("path")
@click.option('--skip-cleanup', is_flag=True, help='跳过向量数据清理（仅从监控列表移除）')
@click.option('--wait', is_flag=True, help='等待清理完成（默认后台执行）')
def watch_remove(path, skip_cleanup, wait):
    import threading
    from pathlib import Path as PathLib
    from core.utils.logger import setup_logger
    
    if not remove_watch_dir(path):
        console.print(t("watch_remove_not_found", path=path))
        return
    
    console.print(t("watch_remove_success", path=path))
    
    if skip_cleanup:
        console.print("[yellow]⚠️  已跳过向量数据清理[/yellow]")
        console.print("[dim]💡 提示: 向量数据仍保留在数据库中[/dim]")
        return
    
    console.print()
    console.print("[cyan]🔄 正在扫描文件夹...[/cyan]")
    
    try:
        from core.parser import SUPPORTED_EXTENSIONS
        import os
        
        target_path = PathLib(path).absolute()
        
        # 快速扫描需要删除的文件
        files_to_delete = []
        if target_path.is_file():
            if target_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                files_to_delete.append(target_path.name)
        else:
            for root, _, files in os.walk(target_path):
                for f in files:
                    file_path = PathLib(root) / f
                    if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                        files_to_delete.append(file_path.name)
        
        if not files_to_delete:
            console.print("[yellow]⚠️  未找到需要清理的文件[/yellow]")
            return
        
        console.print(f"[green]✅ 发现 {len(files_to_delete)} 个文件需要清理[/green]")
        
        if not wait:
            console.print()
            console.print("[cyan]🚀 清理任务已转入后台执行[/cyan]")
            console.print(f"[dim]💡 使用 'cbridge logs -f' 查看实时清理进度[/dim]")
            console.print(f"[dim]📝 日志文件: {PathLib.home() / '.cbridge' / 'logs' / 'cbridge-watcher.log'}[/dim]")
        
        # 后台清理函数
        def cleanup_vectors():
            logger = setup_logger("cbridge-watcher")
            try:
                from core.factories import initialize_system
                
                logger.info("=" * 50)
                logger.info(f"开始清理向量数据: {target_path}")
                logger.info(f"需要清理 {len(files_to_delete)} 个文件")
                logger.info("=" * 50)
                
                context_manager = initialize_system()
                
                success_count = 0
                failed_count = 0
                
                for idx, filename in enumerate(files_to_delete, 1):
                    try:
                        if context_manager.delete_context(filename):
                            success_count += 1
                            logger.info(f"[{idx}/{len(files_to_delete)}] ✅ 已删除: {filename}")
                            if wait:
                                console.print(f"[green]✅ [{idx}/{len(files_to_delete)}][/green] {filename}")
                        else:
                            failed_count += 1
                            logger.warning(f"[{idx}/{len(files_to_delete)}] ⚠️  未找到: {filename}")
                            if wait:
                                console.print(f"[yellow]⚠️  [{idx}/{len(files_to_delete)}][/yellow] {filename} (未找到)")
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"[{idx}/{len(files_to_delete)}] ❌ 删除失败: {filename} - {e}")
                        if wait:
                            console.print(f"[red]❌ [{idx}/{len(files_to_delete)}][/red] {filename} - {e}")
                
                # 输出汇总
                logger.info("=" * 50)
                logger.info("📊 清理汇总")
                logger.info(f"总文件数: {len(files_to_delete)}")
                logger.info(f"成功: {success_count}")
                logger.info(f"失败/未找到: {failed_count}")
                logger.info("✅ 向量数据清理完成")
                logger.info("=" * 50)
                
                if wait:
                    console.print()
                    console.print("[bold cyan]📊 清理汇总[/bold cyan]")
                    console.print(f"[dim]总文件数:[/dim] {len(files_to_delete)}")
                    console.print(f"[green]成功:[/green] {success_count}")
                    console.print(f"[yellow]失败/未找到:[/yellow] {failed_count}")
                    console.print()
                    console.print("[green]✅ 向量数据清理完成[/green]")
                
            except Exception as e:
                logger.error(f"❌ 清理过程出错: {e}")
                import traceback
                logger.error(traceback.format_exc())
                if wait:
                    console.print(f"[red]❌ 清理过程出错: {e}[/red]")
        
        # 启动后台线程
        cleanup_thread = threading.Thread(target=cleanup_vectors, daemon=False, name="VectorCleanup")
        cleanup_thread.start()
        
        # 如果用户选择等待，则阻塞直到完成
        if wait:
            console.print()
            console.print("[dim]正在清理，请稍候...[/dim]")
            console.print()
            cleanup_thread.join()
        
    except Exception as e:
        console.print(f"[red]❌ 启动清理任务失败: {e}[/red]")
        import traceback
        traceback.print_exc()

@cli.command(help=t("index_desc"))
@click.option('--path', help='索引指定路径（默认索引所有监控文件夹）')
@click.option('--quiet', '-q', is_flag=True, help='静默模式，减少日志输出')
def index(path, quiet):
    # 设置日志记录（用于后台索引进程）
    import sys
    from core.utils.logger import setup_logger
    
    # 如果是后台进程，设置日志记录
    if not sys.stdout.isatty():
        logger = setup_logger("cbridge-watcher")
        
        class LoggerWriter:
            def __init__(self, log_func):
                self.log_func = log_func
            def write(self, msg):
                if msg and msg.strip():
                    self.log_func(msg.strip())
            def flush(self):
                pass
            def isatty(self):
                return False
        
        sys.stdout = LoggerWriter(logger.info)
        sys.stderr = LoggerWriter(logger.error)
    
    if path:
        from pathlib import Path as PathLib
        from core.watcher import index_dir
        result = index_dir(PathLib(path), show_progress=not quiet)
        _display_index_summary(result, quiet)
    else:
        console.print(t("index_start"))
        index_all()

@cli.command(help=t("start_desc"))
@click.option('--foreground', '-f', is_flag=True, help='Run in foreground (default is background)')
def start(foreground):
    import subprocess
    import sys
    import os
    from pathlib import Path
    from core.utils.logger import setup_logger
    
    # 确保日志目录存在
    log_dir = Path.home() / ".cbridge" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    if not foreground:
        # 后台运行模式
        if sys.platform == "win32":
            # Windows: spawn a detached subprocess
            pid_file = Path.home() / ".cbridge" / "cbridge_watcher.pid"
            cmd = [sys.executable, sys.argv[0], "start", "--foreground"]
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            DETACHED_PROCESS = 0x00000008
            proc = subprocess.Popen(
                cmd,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            pid_file.parent.mkdir(parents=True, exist_ok=True)
            pid_file.write_text(str(proc.pid))
            console.print(f"[green]✅ ContextBridge watcher started in background (PID {proc.pid})[/green]")
            console.print(f"[dim]📝 Logs: {Path.home() / '.cbridge' / 'logs' / 'cbridge-watcher.log'}[/dim]")
            console.print(f"[dim]💡 Use 'cbridge logs -f' to view real-time logs[/dim]")
            console.print(f"[dim]💡 Use 'cbridge stop' to stop the watcher[/dim]")
            return
        else:
            # Unix: traditional double-fork daemonize
            pid = os.fork()
            if pid > 0:
                pid_file = Path.home() / ".cbridge" / "cbridge_watcher.pid"
                pid_file.parent.mkdir(parents=True, exist_ok=True)
                pid_file.write_text(str(pid))
                console.print(f"[green]✅ ContextBridge watcher started in background (PID {pid})[/green]")
                console.print(f"[dim]📝 Logs: {Path.home() / '.cbridge' / 'logs' / 'cbridge-watcher.log'}[/dim]")
                console.print(f"[dim]💡 Use 'cbridge logs -f' to view real-time logs[/dim]")
                console.print(f"[dim]💡 Use 'cbridge stop' to stop the watcher[/dim]")
                return
            os.chdir("/")
            os.setsid()
            os.umask(0)
            
            # Setup logging to file
            logger = setup_logger("cbridge-watcher")
            
            class LoggerWriter:
                def __init__(self, log_func):
                    self.log_func = log_func
                def write(self, msg):
                    if msg and msg.strip():
                        self.log_func(msg.strip())
                def flush(self):
                    pass
                def isatty(self):
                    return False
            
            sys.stdout = LoggerWriter(logger.info)
            sys.stderr = LoggerWriter(logger.error)
    else:
        # 前台运行模式 - 显示提示信息
        console.print(t("start_init"))
        init_workspace()
        console.print(t("start_engine"))
        console.print("[green]✅ ContextBridge watcher is running in foreground...[/green]")
        console.print()
        console.print("[dim]Press Ctrl+C to stop[/dim]")
        console.print()
        start_watching()
        return
    
    # 实际执行（后台模式）
    try:
        logger = setup_logger("cbridge-watcher")
        
        class LoggerWriter:
            def __init__(self, log_func):
                self.log_func = log_func
            def write(self, msg):
                if msg and msg.strip():
                    self.log_func(msg.strip())
            def flush(self):
                pass
            def isatty(self):
                return False
        
        sys.stdout = LoggerWriter(logger.info)
        sys.stderr = LoggerWriter(logger.error)
        
        console.print(t("start_init"))
        init_workspace()
        console.print(t("start_engine"))
        console.print("[green]✅ ContextBridge watcher is running...[/green]")
        start_watching()
    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)

@cli.command(help=t("serve_desc"))
@click.option('--port', default=9790, help='Port to run the API server on')
@click.option('--host', default='127.0.0.1', help='Host to bind the API server to')
@click.option('--foreground', is_flag=True, help='Run in foreground (default is background)')
def serve(port, host, foreground):
    import uvicorn
    import socket
    import os
    import signal
    from core.utils.logger import setup_logger
    
    # Step 1: Stop any running serve daemon
    pid_file = Path.home() / ".cbridge" / "cbridge.pid"
    
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            if sys.platform == "win32":
                import subprocess
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True, capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
            pid_file.unlink()
            console.print(t("serve_stopped_existing", pid=pid))
        except (ProcessLookupError, subprocess.CalledProcessError, ValueError):
            # Process not found, just clean up the PID file
            pid_file.unlink()
            console.print(t("serve_cleaned_stale_pid"))
        except PermissionError:
            console.print(t("serve_stop_permission_error"))
            sys.exit(1)
    
    # Fallback mechanism for port conflicts
    original_port = port
    max_retries = 10
    available_port = port
    
    for p in range(port, port + max_retries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, p))
                available_port = p
                break
            except OSError:
                continue
                
    if available_port != original_port:
        console.print(f"[yellow]⚠️ Port {original_port} is in use. Falling back to port {available_port}.[/yellow]")
        port = available_port

    # Default to daemon mode unless --foreground is specified
    daemon = not foreground
    
    if daemon:
        if sys.platform == "win32":
            # Windows: spawn a detached subprocess
            import subprocess
            pid_file = Path.home() / ".cbridge" / "cbridge.pid"
            cmd = [sys.executable, sys.argv[0], "serve", "--host", host, "--port", str(port)]
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            DETACHED_PROCESS = 0x00000008
            proc = subprocess.Popen(
                cmd,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            pid_file.parent.mkdir(parents=True, exist_ok=True)
            pid_file.write_text(str(proc.pid))
            console.print(t("serve_daemon_start", pid=proc.pid))
            console.print(t("serve_daemon_url", host=host, port=port))
            console.print(f"[dim]📝 Logs: {Path.home() / '.cbridge' / 'logs' / 'cbridge-serve.log'}[/dim]")
            console.print(t("serve_daemon_hint"))
            sys.exit(0)
        else:
            # Unix: traditional double-fork daemonize
            pid = os.fork()
            if pid > 0:
                console.print(t("serve_daemon_start", pid=pid))
                console.print(t("serve_daemon_url", host=host, port=port))
                console.print(f"[dim]📝 Logs: {Path.home() / '.cbridge' / 'logs' / 'cbridge-serve.log'}[/dim]")
                console.print(t("serve_daemon_hint"))
                sys.exit(0)
            os.chdir("/")
            os.setsid()
            os.umask(0)

        # Setup logging to file (both platforms)
        logger = setup_logger("cbridge-serve")

        class LoggerWriter:
            def __init__(self, log_func):
                self.log_func = log_func
            def write(self, msg):
                if msg and msg.strip():
                    self.log_func(msg.strip())
            def flush(self):
                pass
            def isatty(self):
                return False

        sys.stdout = LoggerWriter(logger.info)
        sys.stderr = LoggerWriter(logger.info)
    else:
        # 前台运行模式
        console.print(t("serve_foreground_start", host=host, port=port))
        console.print()
        console.print("[dim]Press Ctrl+C to stop[/dim]")
        console.print()

    init_workspace()
    # Start the watcher in the background
    import threading
    watcher_thread = threading.Thread(target=start_watching, daemon=True)
    watcher_thread.start()
    
    uvicorn.run("core.api_server:app", host=host, port=port, log_level="info")

@cli.command(help="Stop the background daemon started by 'serve --daemon'")
def stop():
    import os
    import signal
    pid_file = Path.home() / ".cbridge" / "cbridge.pid"
    watcher_pid_file = Path.home() / ".cbridge" / "cbridge_watcher.pid"
    
    # Try to stop watcher first
    if watcher_pid_file.exists():
        try:
            pid = int(watcher_pid_file.read_text().strip())
            if sys.platform == "win32":
                import subprocess
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True, capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
            watcher_pid_file.unlink()
            console.print(f"[green]✅ Watcher (PID {pid}) stopped.[/green]")
        except (ProcessLookupError, subprocess.CalledProcessError):
            console.print(f"[yellow]⚠️  Watcher process not found, cleaning up PID file.[/yellow]")
            watcher_pid_file.unlink()
        except PermissionError:
            console.print(f"[red]❌ Permission denied to stop watcher process.[/red]")
            sys.exit(1)
    
    # Try to stop serve daemon
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            if sys.platform == "win32":
                import subprocess
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True, capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
            pid_file.unlink()
            console.print(f"[green]✅ Daemon (PID {pid}) stopped.[/green]")
        except (ProcessLookupError, subprocess.CalledProcessError):
            console.print(f"[yellow]⚠️  Process {pid} not found, cleaning up PID file.[/yellow]")
            pid_file.unlink()
        except PermissionError:
            console.print(f"[red]❌ Permission denied to stop process {pid}.[/red]")
            sys.exit(1)
    
    if not pid_file.exists() and not watcher_pid_file.exists():
        console.print("[yellow]⚠️  No daemon PID files found. Is any daemon running?[/yellow]")
        sys.exit(1)

@cli.command(help=t("search_desc"))
@click.argument('query')
@click.option('--top-k', default=5, help='Number of results to return (default: 5)')
@click.option('--threshold', default=0.5, type=float, help='Minimum similarity score threshold, 0.0-1.0 (default: 0.5)')
@click.option('--rerank/--no-rerank', default=True, help='Enable/disable keyword-based reranking (default: enabled)')
@click.option('--explain/--no-explain', default=True, help='Show/hide detailed explanation for each result (default: enabled)')
def search(query, top_k, threshold, rerank, explain):
    context_manager = initialize_system()
    results = context_manager.recursive_retrieve(query, top_k=top_k * 2 if rerank else top_k)
    
    if not results:
        console.print(t("search_empty"))
        return
    
    # Store original scores before any processing
    for result in results:
        result['original_score'] = result.get('score', 0.0)
    
    # Apply threshold filtering
    if threshold > 0.0:
        original_count = len(results)
        results = [r for r in results if r.get('score', 0.0) >= threshold]
        filtered_count = original_count - len(results)
        if filtered_count > 0:
            console.print(t("search_filtered", count=filtered_count, threshold=threshold))
    
    # Apply keyword-based reranking
    if rerank and results:
        results = _rerank_by_keywords(query, results)
        results = results[:top_k]  # Limit to top_k after reranking
        console.print(t("search_reranked"))
    
    if not results:
        console.print(t("search_empty_after_filter"))
        return
        
    console.print(t("search_results_title", query=query))
    
    # Display results with or without explanation
    if explain:
        _display_explainable_results(query, results)
    else:
        _display_simple_results(results)

def _rerank_by_keywords(query: str, results: list) -> list:
    """
    Rerank search results based on keyword matching.
    Boosts scores for results that contain query keywords.
    Returns results with enhanced metadata for explainability.
    """
    import re
    
    # Extract keywords from query (simple tokenization)
    keywords = set(re.findall(r'\w+', query.lower()))
    
    # Calculate keyword match scores
    for result in results:
        content = result.get('content', '').lower()
        uri = result.get('uri', '').lower()
        
        # Find which keywords matched and count occurrences
        matched_keywords = {}
        for kw in keywords:
            count_content = content.count(kw)
            count_uri = uri.count(kw)
            total_count = count_content + count_uri
            if total_count > 0:
                matched_keywords[kw] = total_count
        
        # Calculate keyword match ratio
        keyword_match_count = len(matched_keywords)
        keyword_ratio = keyword_match_count / len(keywords) if keywords else 0
        
        # Store detailed matching information
        result['matched_keywords'] = matched_keywords
        result['keyword_match_count'] = keyword_match_count
        result['total_keywords'] = len(keywords)
        result['keyword_match_ratio'] = keyword_ratio
        
        # Boost original score based on keyword matches
        original_score = result.get('original_score', result.get('score', 0.0))
        # Weighted combination: 70% original score + 30% keyword match
        boosted_score = original_score * 0.7 + keyword_ratio * 0.3
        
        # Store both scores for explanation
        result['semantic_score'] = original_score
        result['keyword_score'] = keyword_ratio
        result['score'] = boosted_score
    
    # Sort by boosted score
    return sorted(results, key=lambda x: x.get('score', 0.0), reverse=True)

def _display_simple_results(results: list):
    """Display search results in simple format (original behavior)"""
    for idx, res in enumerate(results, 1):
        source = res.get('uri', 'Unknown')
        content = res.get('content', '')
        score = res.get('score', 0.0)
        console.print(t("search_result_item_numbered", 
                       idx=idx, 
                       source=source, 
                       score=score, 
                       line="-"*40, 
                       content=content.strip()))

def _display_explainable_results(query: str, results: list):
    """Display search results with detailed explanations (explainable RAG)"""
    import re
    
    for idx, res in enumerate(results, 1):
        source = res.get('uri', 'Unknown')
        content = res.get('content', '')
        score = res.get('score', 0.0)
        
        # Extract explanation metadata
        semantic_score = res.get('semantic_score', score)
        keyword_score = res.get('keyword_score', 0.0)
        matched_keywords = res.get('matched_keywords', {})
        keyword_match_count = res.get('keyword_match_count', 0)
        total_keywords = res.get('total_keywords', 0)
        
        # Convert scores to percentages
        score_pct = score * 100
        semantic_pct = semantic_score * 100
        keyword_pct = keyword_score * 100
        
        # Format matched keywords with counts
        if matched_keywords:
            kw_list = [f"{kw}({count})" for kw, count in matched_keywords.items()]
            kw_display = ", ".join(kw_list)
        else:
            kw_display = t("explain_no_keywords")
        
        # Display result header
        console.print(f"\n{t('explain_result_header', idx=idx, source=source)}")
        console.print(t("explain_match_score", score=score_pct))
        console.print(t("explain_keywords", matched=keyword_match_count, total=total_keywords, keywords=kw_display))
        
        # Display matching details
        console.print(t("explain_details_header"))
        console.print(t("explain_semantic_score", score=semantic_pct))
        console.print(t("explain_keyword_score", score=keyword_pct))
        console.print(t("explain_final_score", score=score_pct))
        
        # Display content preview
        console.print(t("explain_content_preview"))
        console.print("-" * 40)
        console.print(content.strip())
        console.print("-" * 40)

@cli.command(help=t("status_desc"))
def status():
    import os
    from pathlib import Path
    
    console.print(t("status_title"))
    console.print(t("status_lang", lang=CONFIG.get('language', 'zh')))
    console.print(t("status_mode", mode=CONFIG.get('mode', 'embedded')))
    console.print(t("status_workspace", workspace=WORKSPACE_DIR))
    console.print(t("status_ov_mount", mount=CONFIG.get('openviking', {}).get('mount_path')))
    console.print(t("status_qmd_coll", coll=CONFIG.get('qmd', {}).get('collection')))
    console.print(t("status_mcp_port", port=CONFIG.get('mcp', {}).get('port', 4733)))
    
    # Check watcher status
    watcher_pid_file = Path.home() / ".cbridge" / "cbridge_watcher.pid"
    if watcher_pid_file.exists():
        try:
            pid = int(watcher_pid_file.read_text().strip())
            if sys.platform == "win32":
                import subprocess
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True,
                    text=True
                )
                if str(pid) in result.stdout:
                    console.print(f"[green]✅ Watcher: Running (PID {pid})[/green]")
                else:
                    console.print(f"[yellow]⚠️  Watcher: Not running (stale PID {pid})[/yellow]")
            else:
                if os.kill(pid, 0) is None:
                    console.print(f"[green]✅ Watcher: Running (PID {pid})[/green]")
        except (ProcessLookupError, ValueError):
            console.print("[yellow]⚠️  Watcher: Not running[/yellow]")
    else:
        console.print("[yellow]⚠️  Watcher: Not running[/yellow]")
    
    # Check serve daemon status
    serve_pid_file = Path.home() / ".cbridge" / "cbridge.pid"
    if serve_pid_file.exists():
        try:
            pid = int(serve_pid_file.read_text().strip())
            if sys.platform == "win32":
                import subprocess
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True,
                    text=True
                )
                if str(pid) in result.stdout:
                    console.print(f"[green]✅ API Server: Running (PID {pid})[/green]")
                else:
                    console.print(f"[yellow]⚠️  API Server: Not running (stale PID {pid})[/yellow]")
            else:
                if os.kill(pid, 0) is None:
                    console.print(f"[green]✅ API Server: Running (PID {pid})[/green]")
        except (ProcessLookupError, ValueError):
            console.print("[yellow]⚠️  API Server: Not running[/yellow]")
    else:
        console.print("[yellow]⚠️  API Server: Not running[/yellow]")

@cli.command(help=t("logs_desc"))
@click.option('--lines', '-n', default=50, help=t("logs_lines_help"))
@click.option('--follow', '-f', is_flag=True, help=t("logs_follow_help"))
def logs(lines, follow):
    """查看 ContextBridge 日志"""
    from pathlib import Path
    import time
    
    log_file = Path.home() / ".cbridge" / "logs" / "cbridge-watcher.log"
    
    if not log_file.exists():
        console.print(t("logs_not_found", file=log_file))
        console.print(t("logs_hint"))
        return
    
    try:
        if follow:
            # 实时跟踪模式
            console.print(t("logs_follow_mode", file=log_file))
            console.print(t("logs_exit_hint"))
            console.print()
            
            # 先显示最后 N 行
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    print(line.rstrip())
            
            # 然后实时跟踪新内容
            with open(log_file, 'r', encoding='utf-8') as f:
                f.seek(0, 2)  # 移动到文件末尾
                while True:
                    line = f.readline()
                    if line:
                        print(line.rstrip())
                    else:
                        time.sleep(0.1)
        else:
            # 显示最后 N 行
            console.print(t("logs_file", file=log_file))
            console.print(t("logs_showing", lines=lines))
            console.print()
            
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    print(line.rstrip())
            
            console.print(t("logs_follow_hint"))
    except KeyboardInterrupt:
        console.print(t("logs_stopped"))
    except Exception as e:
        console.print(t("logs_error", error=e))

@cli.command(help=t("config_desc"))
def config():
    import os
    config_path = Path("config.yaml")
    console.print(t("config_title", path=config_path.absolute()))
    if config_path.exists():
        console.print(t("config_content"))
        with open(config_path, "r", encoding="utf-8") as f:
            console.print(f.read())
        console.print("-" * 40)
    else:
        console.print(t("config_not_found"))

@cli.command(help=t("mcp_desc"))
def mcp():
    console.print(t("mcp_start"))
    asyncio.run(mcp_main())

@cli.command(help=t("lang_desc"))
@click.argument("lang", type=click.Choice(['zh', 'en']))
def lang(lang):
    CONFIG["language"] = lang
    save_config(CONFIG)
    console.print(t("lang_success", lang=lang))

if __name__ == "__main__":
    cli()
