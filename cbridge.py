#!/usr/bin/env python3
import sys
import click
import asyncio
from pathlib import Path

from core.factories import initialize_system
from core.config import init_workspace, CONFIG, WORKSPACE_DIR, CONFIG_PATH, save_config, get_watch_dirs, add_watch_dir, remove_watch_dir
from core.watcher import start_watching, index_all
from core.mcp_server import main as mcp_main
from core.i18n import i18n

@click.group()
def cli():
    """ContextBridge: An intelligent context management bridge."""
    pass

@cli.command()
def init():
    """Initialize ContextBridge configuration interactively."""
    lang = click.prompt(i18n.get("choose_lang"), type=click.Choice(['en', 'zh']), default='zh')
    i18n.set_lang(lang)
    if lang == 'en':
        i18n.print("lang_set")  # this is English version
    else:
        i18n.print("lang_set")  # this is Chinese version
    
    i18n.print("welcome_init")
    
    mode = click.prompt(i18n.get("choose_mode"), type=click.Choice(['embedded', 'external']), default='embedded')
    
    # Preserve existing watch_dirs if any
    existing_watch_dirs = CONFIG.get("watch_dirs", [])
    config_data = {"mode": mode}
    if existing_watch_dirs:
        config_data["watch_dirs"] = existing_watch_dirs
    
    if mode == 'external':
        ov_endpoint = click.prompt(i18n.get("ov_endpoint"), default="http://localhost:8080")
        ov_mount = click.prompt(i18n.get("ov_mount"), default="viking://contextbridge/")
        qmd_endpoint = click.prompt(i18n.get("qmd_endpoint"), default="http://localhost:9090")
        qmd_collection = click.prompt(i18n.get("qmd_collection"), default="cb_documents")
        
        config_data["openviking"] = {
            "endpoint": ov_endpoint,
            "mount_path": ov_mount
        }
        config_data["qmd"] = {
            "endpoint": qmd_endpoint,
            "collection": qmd_collection
        }
    
    workspace = click.prompt(i18n.get("workspace_dir"), default="~/ContextBridge_Workspace")
    config_data["workspace_dir"] = workspace
    
    save_config(config_data)
    i18n.print("config_saved", path=CONFIG_PATH.absolute())
    init_workspace()

@cli.group()
def watch():
    """Manage monitored directories."""
    pass

@watch.command(name="list")
def watch_list():
    """List all monitored directories."""
    dirs = get_watch_dirs()
    i18n.print("monitored_dirs")
    for d in dirs:
        i18n.print("dir_item", path=d)

@watch.command(name="add")
@click.argument("path")
def watch_add(path):
    """Add a directory to monitor."""
    if add_watch_dir(path):
        i18n.print("dir_added", path=path)
    else:
        i18n.print("dir_already_monitored", path=path)

@watch.command(name="remove")
@click.argument("path")
def watch_remove(path):
    """Remove a directory from monitoring."""
    if remove_watch_dir(path):
        i18n.print("dir_removed", path=path)
    else:
        i18n.print("dir_not_in_list", path=path)

@cli.command()
def index():
    """Run a one-time index of all monitored directories."""
    i18n.print("start_indexing")
    index_all()

@cli.command()
def start():
    """Start the ContextBridge document watcher."""
    i18n.print("init_workspace")
    init_workspace()
    i18n.print("start_engine")
    start_watching()

@cli.command()
@click.argument('query')
@click.option('--top-k', default=5, help='Number of results to return')
def search(query, top_k):
    """Search the context database."""
    context_manager = initialize_system()
    results = context_manager.recursive_retrieve(query, top_k=top_k)
    
    if not results:
        i18n.print("no_results")
        return
        
    i18n.print("search_results_title", query=query, divider="="*40)
    for res in results:
        source = res.get('uri', 'Unknown')
        content = res.get('content', '')
        score = res.get('score', 0.0)
        i18n.print("search_result_item", source=source, score=score, divider="-"*40, content=content.strip())

@cli.command()
def status():
    """Show current configuration and workspace status."""
    i18n.print("status_title")
    i18n.print("status_mode", mode=CONFIG.get('mode', 'embedded'))
    i18n.print("status_workspace", workspace=WORKSPACE_DIR)
    i18n.print("status_ov_mount", ov_mount=CONFIG.get('openviking', {}).get('mount_path'))
    i18n.print("status_qmd_coll", qmd_collection=CONFIG.get('qmd', {}).get('collection'))
    i18n.print("status_mcp_port", mcp_port=CONFIG.get('mcp', {}).get('port', 4733))
    i18n.print("status_lang", lang=i18n.lang)

@cli.command()
def config():
    """Show the current configuration file path and contents."""
    import os
    from rich.syntax import Syntax
    from core.i18n import console
    config_path = Path("config.yaml")
    i18n.print("config_file", path=config_path.absolute())
    if config_path.exists():
        i18n.print("config_contents", divider="-"*40)
        with open(config_path, "r", encoding="utf-8") as f:
            yaml_content = f.read()
            syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True)
            console.print(syntax)
        console.print("[dim]" + "-" * 40 + "[/]")
    else:
        i18n.print("no_config")

@cli.command()
def mcp():
    """Start the MCP Server."""
    i18n.print("start_mcp")
    asyncio.run(mcp_main())

@cli.command()
@click.argument('language', required=False, type=click.Choice(['en', 'zh']))
def lang(language):
    """Switch the interface language (en or zh)."""
    if not language:
        language = click.prompt(i18n.get("choose_lang"), type=click.Choice(['en', 'zh']), default=i18n.lang)
    
    i18n.set_lang(language)
    i18n.print("lang_set")

if __name__ == "__main__":
    cli()
