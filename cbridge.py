#!/usr/bin/env python3
import sys
import click
import asyncio
from pathlib import Path
from rich.console import Console

from core.factories import initialize_system
from core.config import init_workspace, CONFIG, WORKSPACE_DIR, CONFIG_PATH, save_config, get_watch_dirs, add_watch_dir, remove_watch_dir
from core.watcher import start_watching, index_all
from core.mcp_server import main as mcp_main
from core.i18n import t

console = Console(stderr=True)

@click.group(help=t("cli_desc"))
def cli():
    pass

@cli.command(help=t("init_desc"))
def init():
    console.print(t("init_welcome"))
    
    lang = click.prompt(t("choose_lang"), type=click.Choice(['zh', 'en']), default='zh')
    CONFIG["language"] = lang
    
    mode = click.prompt(t("choose_mode"), type=click.Choice(['embedded', 'external']), default='embedded')
    
    # Preserve existing watch_dirs if any
    existing_watch_dirs = CONFIG.get("watch_dirs", [])
    config_data = {"mode": mode, "language": lang}
    if existing_watch_dirs:
        config_data["watch_dirs"] = existing_watch_dirs
    
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
    
    workspace = click.prompt(t("workspace_dir"), default="~/ContextBridge_Workspace")
    config_data["workspace_dir"] = workspace
    
    save_config(config_data)
    console.print(t("config_saved", path=CONFIG_PATH.absolute()))
    init_workspace()

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
def start():
    console.print(t("start_init"))
    init_workspace()
    console.print(t("start_engine"))
    start_watching()

@cli.command(help=t("serve_desc"))
@click.option('--port', default=9790, help='Port to run the API server on')
@click.option('--host', default='127.0.0.1', help='Host to bind the API server to')
def serve(port, host):
    import uvicorn
    import socket
    
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

    console.print(t("serve_start", host=host, port=port))
    init_workspace()
    # Start the watcher in the background
    import threading
    watcher_thread = threading.Thread(target=start_watching, daemon=True)
    watcher_thread.start()
    
    uvicorn.run("core.api_server:app", host=host, port=port, log_level="info")

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
    console.print(t("status_title"))
    console.print(t("status_lang", lang=CONFIG.get('language', 'zh')))
    console.print(t("status_mode", mode=CONFIG.get('mode', 'embedded')))
    console.print(t("status_workspace", workspace=WORKSPACE_DIR))
    console.print(t("status_ov_mount", mount=CONFIG.get('openviking', {}).get('mount_path')))
    console.print(t("status_qmd_coll", coll=CONFIG.get('qmd', {}).get('collection')))
    console.print(t("status_mcp_port", port=CONFIG.get('mcp', {}).get('port', 4733)))

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
