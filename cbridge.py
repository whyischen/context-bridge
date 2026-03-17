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
    import subprocess
    
    try:
        # Use subprocess to call 'cbridge start --daemon'
        cmd = [sys.executable, sys.argv[0], "start", "--daemon"]
        subprocess.run(cmd, check=True)
        console.print(t("init_complete"))
    except subprocess.CalledProcessError as e:
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
def watch_add(path):
    if add_watch_dir(path):
        console.print(t("watch_add_success", path=path))
        index_dir(Path(path))
    else:
        console.print(t("watch_add_exists", path=path))

@watch.command(name="remove", help=t("watch_remove_desc"))
@click.argument("path")
def watch_remove(path):
    if remove_watch_dir(path):
        console.print(t("watch_remove_success", path=path))
    else:
        console.print(t("watch_remove_not_found", path=path))

@cli.command(help=t("index_desc"))
def index():
    console.print(t("index_start"))
    index_all()

@cli.command(help=t("start_desc"))
@click.option('--daemon', is_flag=True, help='Run as background daemon')
def start(daemon):
    import subprocess
    import sys
    import os
    from pathlib import Path
    from core.utils.logger import setup_logger
    
    if daemon:
        # 后台运行模式
        if sys.platform == "win32":
            # Windows: spawn a detached subprocess
            pid_file = Path.home() / ".cbridge" / "cbridge_watcher.pid"
            cmd = [sys.executable, sys.argv[0], "start"]
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
            console.print(f"[green]✅ ContextBridge watcher started (PID {proc.pid})[/green]")
            console.print(f"[dim]📝 Logs: {Path.home() / '.cbridge' / 'logs' / 'cbridge-watcher.log'}[/dim]")
            return
        else:
            # Unix: traditional double-fork daemonize
            pid = os.fork()
            if pid > 0:
                pid_file = Path.home() / ".cbridge" / "cbridge_watcher.pid"
                pid_file.parent.mkdir(parents=True, exist_ok=True)
                pid_file.write_text(str(pid))
                console.print(f"[green]✅ ContextBridge watcher started (PID {pid})[/green]")
                console.print(f"[dim]📝 Logs: {Path.home() / '.cbridge' / 'logs' / 'cbridge-watcher.log'}[/dim]")
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
        console.print("[green]✅ ContextBridge watcher is running...[/green]")
        console.print()
        console.print("[yellow]💡 Tip: To run in background, use:[/yellow]")
        console.print("[cyan]   cbridge start --daemon[/cyan]")
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
@click.option('--top-k', default=5, help='Returns top K results')
def search(query, top_k):
    context_manager = initialize_system()
    results = context_manager.recursive_retrieve(query, top_k=top_k)
    
    if not results:
        console.print(t("search_empty"))
        return
        
    console.print(t("search_results_title", query=query))
    for res in results:
        source = res.get('uri', 'Unknown')
        content = res.get('content', '')
        score = res.get('score', 0.0)
        console.print(t("search_result_item", source=source, score=score, line="-"*40, content=content.strip()))

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
