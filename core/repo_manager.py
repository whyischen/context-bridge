import os
import time
import threading
import subprocess
from pathlib import Path
from rich.console import Console
from core.config import get_repos

console = Console(stderr=True)

def sync_repo(repo_info):
    url = repo_info.get("url")
    local_path = Path(repo_info.get("local_path"))
    
    if not url or not local_path:
        return False
        
    try:
        if (local_path / ".git").exists():
            # Repository exists, pull latest changes
            console.print(f"[dim]🔄 正在拉取仓库更新:[/dim] {url} -> {local_path}")
            result = subprocess.run(
                ["git", "-C", str(local_path), "pull"],
                capture_output=True,
                text=True,
                check=True
            )
            if "Already up to date." not in result.stdout:
                console.print(f"[green]✅ 仓库已更新:[/green] {local_path.name}")
        else:
            # Repository does not exist, clone it
            console.print(f"[dim]⬇️ 正在克隆仓库:[/dim] {url} -> {local_path}")
            local_path.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["git", "clone", url, str(local_path)],
                capture_output=True,
                text=True,
                check=True
            )
            console.print(f"[green]✅ 仓库克隆完成:[/green] {local_path.name}")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]❌ 同步仓库失败 {url}:[/bold red] {e.stderr.strip()}")
        return False
    except Exception as e:
        console.print(f"[bold red]❌ 同步仓库发生未知错误 {url}:[/bold red] {e}")
        return False

def sync_all_repos():
    repos = get_repos()
    if not repos:
        return
        
    console.print(f"[bold cyan]🔄 开始同步 {len(repos)} 个 GitHub 仓库...[/bold cyan]")
    for repo in repos:
        sync_repo(repo)

def _auto_sync_loop():
    while True:
        repos = get_repos()
        if not repos:
            time.sleep(60)
            continue
            
        # For simplicity, we just sleep for the minimum interval among all repos
        # A more robust implementation would track last_sync_time per repo
        min_interval = min([repo.get("sync_interval", 3600) for repo in repos])
        # Ensure minimum 60 seconds to avoid spamming
        sleep_time = max(60, min_interval)
        
        time.sleep(sleep_time)
        sync_all_repos()

def start_auto_sync():
    repos = get_repos()
    if repos:
        # Do an initial sync immediately
        sync_all_repos()
        
    # Start background thread
    thread = threading.Thread(target=_auto_sync_loop, daemon=True)
    thread.start()
    console.print("[dim]⏱️ 自动拉取 GitHub 仓库的后台任务已启动[/dim]")
