import os
import sys
import signal
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Any, Union
from core.utils.logger import get_logger
from core.i18n import t

logger = get_logger("process")

# Default PID file locations
WATCHER_PID_FILE = Path(os.path.expanduser("~/.cbridge/watcher.pid"))
SERVE_PID_FILE = Path(os.path.expanduser("~/.cbridge/serve.pid"))

def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    if pid <= 0:
        return False
        
    if sys.platform == "win32":
        try:
            # Use tasklist with specific PID filter
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                # tasklist returns "INFO: No tasks are running..." when process not found
                if output and "INFO:" not in output and str(pid) in output:
                    return True
            return False
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError):
            return False

def get_pid_from_file(pid_file: Path) -> Optional[int]:
    """Read PID from file and return it if file exists and content is valid."""
    if pid_file.exists():
        try:
            pid_str = pid_file.read_text().strip()
            if pid_str:
                return int(pid_str)
        except (ValueError, OSError):
            pass
    return None

def start_background_process(cmd_args: Union[str, List[str]], pid_file: Path, log_file: str) -> Optional[int]:
    """Start a command in background and save its PID."""
    # Ensure logs dir exists
    log_dir = Path(os.path.expanduser("~/.cbridge/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_path = log_dir / log_file
    
    # PID file dir
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Check for pythonw on Windows (specifically for hiding windows)
    if sys.platform == "win32" and isinstance(cmd_args, list):
        if cmd_args[0].endswith("python.exe"):
            pythonw = cmd_args[0].replace("python.exe", "pythonw.exe")
            if os.path.exists(pythonw):
                cmd_args[0] = pythonw

    with open(log_path, "a", encoding="utf-8") as f:
        try:
            if sys.platform == "win32":
                # Most robust way to start a truly invisible background process on Windows
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = 0 # SW_HIDE
                
                # If it's a list, shell=False is quieter
                use_shell = isinstance(cmd_args, str)
                
                process = subprocess.Popen(
                    cmd_args,
                    stdout=f,
                    stderr=f,
                    # Combine flags for maximum concealment and separation
                    creationflags=subprocess.CREATE_NO_WINDOW | 
                                 subprocess.DETACHED_PROCESS | 
                                 subprocess.CREATE_NEW_PROCESS_GROUP,
                    startupinfo=si,
                    shell=use_shell
                )
            else:
                process = subprocess.Popen(
                    cmd_args,
                    stdout=f,
                    stderr=f,
                    preexec_fn=os.setsid,
                    shell=isinstance(cmd_args, str)
                )
            
            pid = process.pid
            pid_file.write_text(str(pid))
            return pid
        except Exception as e:
            logger.error(f"Failed to start background process: {e}")
            return None

def stop_background_process(pid_file: Path) -> bool:
    """Stop a background process given its PID file."""
    pid = get_pid_from_file(pid_file)
    if not pid:
        if pid_file.exists():
            pid_file.unlink()
        return False
        
    if not is_process_running(pid):
        if pid_file.exists():
            pid_file.unlink()
        return False
        
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], 
                         capture_output=True, check=False)
        else:
            os.kill(pid, signal.SIGTERM)
            # Give it a second to terminate
            import time
            time.sleep(1)
            if is_process_running(pid):
                os.kill(pid, signal.SIGKILL)
        
        if pid_file.exists():
            pid_file.unlink()
        return True
    except Exception as e:
        logger.error(f"Error stopping process {pid}: {e}")
        return False

def get_process_status(pid_file: Path) -> Tuple[str, Optional[int]]:
    """Check if process is running and return its PID."""
    pid = get_pid_from_file(pid_file)
    if pid and is_process_running(pid):
        return "running", pid
    
    # Cleanup stale PID file if exists
    if pid_file.exists():
        return "stale", pid
        
    return "not_running", None
