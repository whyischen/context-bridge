#!/usr/bin/env python3
import sys
import click
import asyncio
from pathlib import Path

from core.factories import initialize_system
from core.config import init_workspace, CONFIG, WORKSPACE_DIR, CONFIG_PATH, save_config, get_watch_dirs, add_watch_dir, remove_watch_dir
from core.watcher import start_watching, index_all
from core.mcp_server import main as mcp_main

@click.group()
def cli():
    """ContextBridge: An intelligent context management bridge."""
    pass

@cli.command()
def init():
    """Initialize ContextBridge configuration interactively."""
    click.echo("Welcome to ContextBridge Initialization!")
    
    mode = click.prompt("Choose mode (embedded/external)", type=click.Choice(['embedded', 'external']), default='embedded')
    
    # Preserve existing watch_dirs if any
    existing_watch_dirs = CONFIG.get("watch_dirs", [])
    config_data = {"mode": mode}
    if existing_watch_dirs:
        config_data["watch_dirs"] = existing_watch_dirs
    
    if mode == 'external':
        ov_endpoint = click.prompt("OpenViking Endpoint", default="http://localhost:8080")
        ov_mount = click.prompt("OpenViking Mount Path", default="viking://contextbridge/")
        qmd_endpoint = click.prompt("QMD Endpoint", default="http://localhost:9090")
        qmd_collection = click.prompt("QMD Collection", default="cb_documents")
        
        config_data["openviking"] = {
            "endpoint": ov_endpoint,
            "mount_path": ov_mount
        }
        config_data["qmd"] = {
            "endpoint": qmd_endpoint,
            "collection": qmd_collection
        }
    
    workspace = click.prompt("Workspace Directory", default="~/ContextBridge_Workspace")
    config_data["workspace_dir"] = workspace
    
    save_config(config_data)
    click.echo(f"Configuration saved to {CONFIG_PATH.absolute()}")
    init_workspace()

@cli.group()
def watch():
    """Manage monitored directories."""
    pass

@watch.command(name="list")
def watch_list():
    """List all monitored directories."""
    dirs = get_watch_dirs()
    click.echo("Currently monitored directories:")
    for d in dirs:
        click.echo(f"  - {d}")

@watch.command(name="add")
@click.argument("path")
def watch_add(path):
    """Add a directory to monitor."""
    if add_watch_dir(path):
        click.echo(f"Added '{path}' to monitored directories.")
    else:
        click.echo(f"'{path}' is already being monitored.")

@watch.command(name="remove")
@click.argument("path")
def watch_remove(path):
    """Remove a directory from monitoring."""
    if remove_watch_dir(path):
        click.echo(f"Removed '{path}' from monitored directories.")
    else:
        click.echo(f"'{path}' was not in the monitored list.")

@cli.command()
def index():
    """Run a one-time index of all monitored directories."""
    click.echo("Starting indexing process...")
    index_all()

@cli.command()
def start():
    """Start the ContextBridge document watcher."""
    click.echo("Initializing ContextBridge Workspace...")
    init_workspace()
    click.echo("Starting ContextBridge Engine...")
    start_watching()

@cli.command()
@click.argument('query')
@click.option('--top-k', default=5, help='Number of results to return')
def search(query, top_k):
    """Search the context database."""
    context_manager = initialize_system()
    results = context_manager.recursive_retrieve(query, top_k=top_k)
    
    if not results:
        click.echo("No results found.")
        return
        
    click.echo(f"\nSearch Results for: '{query}'\n" + "="*40)
    for res in results:
        source = res.get('uri', 'Unknown')
        content = res.get('content', '')
        score = res.get('score', 0.0)
        click.echo(f"\n📄 Source: {source} (Score: {score:.4f})\n{'-'*40}\n{content.strip()}\n")

@cli.command()
def status():
    """Show current configuration and workspace status."""
    click.echo("ContextBridge Status:")
    click.echo(f"  Mode: {CONFIG.get('mode', 'embedded')}")
    click.echo(f"  Workspace: {WORKSPACE_DIR}")
    click.echo(f"  OpenViking Mount: {CONFIG.get('openviking', {}).get('mount_path')}")
    click.echo(f"  QMD Collection: {CONFIG.get('qmd', {}).get('collection')}")
    click.echo(f"  MCP Port: {CONFIG.get('mcp', {}).get('port', 4733)}")

@cli.command()
def config():
    """Show the current configuration file path and contents."""
    import os
    config_path = Path("config.yaml")
    click.echo(f"Config File: {config_path.absolute()}")
    if config_path.exists():
        click.echo("\nContents:\n" + "-"*40)
        with open(config_path, "r", encoding="utf-8") as f:
            click.echo(f.read())
        click.echo("-" * 40)
    else:
        click.echo("No config.yaml found. Using default embedded settings.")

@cli.command()
def mcp():
    """Start the MCP Server."""
    click.echo("Starting ContextBridge MCP Server...")
    asyncio.run(mcp_main())

if __name__ == "__main__":
    cli()
