import os
from core.config import CONFIG

MESSAGES = {
    "zh": {
        # cbridge.py
        "cli_desc": "ContextBridge: 智能体本地记忆桥梁",
        "init_desc": "交互式初始化 ContextBridge 配置",
        "init_welcome": "[bold cyan]✨ 欢迎使用 ContextBridge 初始化向导！[/bold cyan]",
        "choose_lang": "请选择语言 / Choose language (zh/en)",
        "choose_mode": "请选择运行模式 (embedded/external)",
        "ov_endpoint": "OpenViking 服务地址",
        "ov_mount": "OpenViking 挂载路径",
        "qmd_endpoint": "QMD 服务地址",
        "qmd_collection": "QMD 集合名称",
        "workspace_dir": "工作区目录",
        "config_saved": "[bold green]✅ 配置已保存至 {path}[/bold green]",
        "watch_desc": "管理监控目录",
        "watch_list_desc": "列出所有正在监控的目录",
        "watch_list_title": "[bold cyan]👀 当前正在监控的目录:[/bold cyan]",
        "watch_add_desc": "添加新的监控目录",
        "watch_add_success": "[bold green]✅ 已将 '{path}' 加入监控列表。[/bold green]",
        "watch_add_exists": "[yellow]⚠️ '{path}' 已经在监控列表中了。[/yellow]",
        "watch_remove_desc": "移除指定的监控目录",
        "watch_remove_success": "[bold green]✅ 已将 '{path}' 从监控列表中移除。[/bold green]",
        "watch_remove_not_found": "[yellow]⚠️ '{path}' 不在监控列表中。[/yellow]",
        "index_desc": "对所有监控目录进行一次性全量索引",
        "index_start": "[bold cyan]🚀 开始全量构建索引...[/bold cyan]",
        "start_desc": "启动 ContextBridge 实时监控服务",
        "start_init": "[bold cyan]🔧 正在初始化 ContextBridge 工作区...[/bold cyan]",
        "start_engine": "[bold green]🚀 正在启动 ContextBridge 核心引擎...[/bold green]",
        "serve_desc": "启动 ContextBridge API 服务供 AI Agent 调用",
        "serve_start": "[bold cyan]🚀 正在启动 ContextBridge API 服务 (http://{host}:{port})...[/bold cyan]",
        "search_desc": "在知识库中进行语义检索",
        "search_empty": "[yellow]📭 未找到相关结果。[/yellow]",
        "search_results_title": "\n[bold cyan]🔍 检索结果: '{query}'[/bold cyan]\n" + "="*40,
        "search_result_item": "\n[bold green]📄 来源:[/bold green] {source} [dim](相似度: {score:.4f})[/dim]\n{line}\n{content}\n",
        "status_desc": "查看当前配置和运行状态",
        "status_title": "[bold cyan]📊 ContextBridge 运行状态:[/bold cyan]",
        "status_lang": "  [bold]当前语言:[/bold] {lang}",
        "status_mode": "  [bold]运行模式:[/bold] {mode}",
        "status_workspace": "  [bold]工作区:[/bold] {workspace}",
        "status_ov_mount": "  [bold]OpenViking 挂载点:[/bold] {mount}",
        "status_qmd_coll": "  [bold]QMD 集合:[/bold] {coll}",
        "status_mcp_port": "  [bold]MCP 端口:[/bold] {port}",
        "config_desc": "查看当前配置文件路径及内容",
        "config_title": "[bold cyan]⚙️ 配置文件:[/bold cyan] {path}",
        "config_content": "\n[bold]内容:[/bold]\n" + "-"*40,
        "config_not_found": "[yellow]⚠️ 未找到 config.yaml，当前使用默认内嵌配置。[/yellow]",
        "mcp_desc": "启动 MCP Server 供 Claude 接入",
        "mcp_start": "[bold cyan]🔌 正在启动 ContextBridge MCP 服务...[/bold cyan]",
        "lang_desc": "切换显示语言 / Switch display language",
        "lang_success": "[bold green]✅ 语言已切换为: {lang}[/bold green]",
        "workspace_init": "[dim]工作区已初始化于 {dir} (模式: {mode})[/dim]",
        
        # model_downloader.py
        "mdl_first_run": "\n[bold cyan]✨ 首次运行: 正在为您准备本地 AI 向量模型 ({model_name})[/bold cyan]",
        "mdl_desc": "[dim]该模型用于将您的文档转换为 AI 可理解的数学向量，仅需下载一次。[/dim]",
        "mdl_downloading": "下载模型中...",
        "mdl_extracting": "[bold green]✅ 下载完成！正在解压模型...[/bold green]",
        "mdl_ready": "[bold green]🎉 模型准备就绪！[/bold green]\n",
        "mdl_failed": "\n[bold red]❌ 模型下载失败: {error}[/bold red]",
        "mdl_hint": "[yellow]💡 提示: 这通常是因为网络连接 AWS S3 较慢。[/yellow]",
        "mdl_manual": "[yellow]请尝试开启代理，或者手动下载以下链接并解压到 {cache_dir} 目录下：[/yellow]",
        
        # openviking_manager.py
        "ov_init_embed": "[dim]⚙️ 初始化内嵌 OpenViking 管理器, 挂载路径: {mount_path}[/dim]",
        "ov_init_ext": "[dim]🔗 接入外部 OpenViking 服务: {endpoint}, 挂载路径: {mount_path}[/dim]",
        "ov_write_embed": "[cyan]📝 [OpenViking] 正在处理上下文:[/cyan] {uri}",
        "ov_write_ext": "[cyan]📝 [外部 OpenViking] 模拟通过 API 将上下文写入[/cyan] {uri}",
        "ov_del_embed": "[yellow]🗑️ [OpenViking] 正在删除上下文:[/yellow] {uri}",
        "ov_del_ext": "[yellow]🗑️ [外部 OpenViking] 模拟通过 API 删除上下文[/yellow] {uri}",
        "ov_ret_embed": "[magenta]🧠 [OpenViking] 执行目录递归检索策略:[/magenta] '{query}'",
        "ov_ret_ext": "[magenta]🧠 [外部 OpenViking] 模拟向 {endpoint} 发起递归检索:[/magenta] '{query}'",
        
        # qmd_runtime.py
        "qmd_init_embed": "[dim]⚙️ 初始化内嵌 QMD 引擎 (基于 ChromaDB)...[/dim]",
        "qmd_init_ext": "[dim]🔗 接入外部 QMD 服务: {endpoint}, 集合: {collection}[/dim]",
        "qmd_write_ext": "[cyan]📝 [外部 QMD] 模拟向 {endpoint}/{collection} 写入文档[/cyan] {doc_id}",
        "qmd_del_ext": "[yellow]🗑️ [外部 QMD] 模拟向 {endpoint}/{collection} 发起删除 URI:[/yellow] {uri}",
        "qmd_search_ext": "[magenta]🔍 [外部 QMD] 模拟向 {endpoint}/{collection} 发起混合检索:[/magenta] '{query}'",
        
        # parser.py
        "parse_start": "[dim]📄 正在解析文档:[/dim] {file_path}",
        "parse_failed": "[bold red]❌ 解析失败 {file_path}:[/bold red] {error}",
        
        # watcher.py
        "watch_del": "[yellow]🗑️ 文件已删除:[/yellow] {name}",
        "watch_event": "[green]📄 文件已{event}:[/green] {name}",
        "watch_ev_create": "创建",
        "watch_ev_modify": "修改",
        "watch_ev_delete": "删除",
        "idx_no_files": "[yellow]📭 未找到需要索引的文件。[/yellow]",
        "idx_found": "[bold cyan]📦 找到 {count} 个文件，开始构建索引...[/bold cyan]",
        "idx_ghost_clean": "[yellow]🧹 发现 {count} 个已删除的幽灵文件，正在清理...[/yellow]",
        "idx_progress": "正在解析并向量化...",
        "idx_file_count": "{completed}/{total} 文件",
        "idx_complete": "[bold green]✅ 索引构建完成！[/bold green]",
        "watch_dir": "[bold cyan]👀 正在监控目录变更:[/bold cyan] {dir}",
    },
    "en": {
        # cbridge.py
        "cli_desc": "ContextBridge: An intelligent context management bridge",
        "init_desc": "Interactively initialize ContextBridge configuration",
        "init_welcome": "[bold cyan]✨ Welcome to ContextBridge Initialization Wizard![/bold cyan]",
        "choose_lang": "请选择语言 / Choose language (zh/en)",
        "choose_mode": "Choose mode (embedded/external)",
        "ov_endpoint": "OpenViking Endpoint",
        "ov_mount": "OpenViking Mount Path",
        "qmd_endpoint": "QMD Endpoint",
        "qmd_collection": "QMD Collection Name",
        "workspace_dir": "Workspace Directory",
        "config_saved": "[bold green]✅ Configuration saved to {path}[/bold green]",
        "watch_desc": "Manage monitored directories",
        "watch_list_desc": "List all monitored directories",
        "watch_list_title": "[bold cyan]👀 Currently monitored directories:[/bold cyan]",
        "watch_add_desc": "Add a new directory to monitor",
        "watch_add_success": "[bold green]✅ Added '{path}' to monitored list.[/bold green]",
        "watch_add_exists": "[yellow]⚠️ '{path}' is already in the monitored list.[/yellow]",
        "watch_remove_desc": "Remove a monitored directory",
        "watch_remove_success": "[bold green]✅ Removed '{path}' from monitored list.[/bold green]",
        "watch_remove_not_found": "[yellow]⚠️ '{path}' is not in the monitored list.[/yellow]",
        "index_desc": "Run a one-time full index on all monitored directories",
        "index_start": "[bold cyan]🚀 Starting full index build...[/bold cyan]",
        "start_desc": "Start ContextBridge real-time monitoring service",
        "start_init": "[bold cyan]🔧 Initializing ContextBridge workspace...[/bold cyan]",
        "start_engine": "[bold green]🚀 Starting ContextBridge core engine...[/bold green]",
        "serve_desc": "Start ContextBridge API service for AI Agents",
        "serve_start": "[bold cyan]🚀 Starting ContextBridge API service (http://{host}:{port})...[/bold cyan]",
        "search_desc": "Perform semantic search in the knowledge base",
        "search_empty": "[yellow]📭 No relevant results found.[/yellow]",
        "search_results_title": "\n[bold cyan]🔍 Search Results: '{query}'[/bold cyan]\n" + "="*40,
        "search_result_item": "\n[bold green]📄 Source:[/bold green] {source} [dim](Score: {score:.4f})[/dim]\n{line}\n{content}\n",
        "status_desc": "View current configuration and running status",
        "status_title": "[bold cyan]📊 ContextBridge Status:[/bold cyan]",
        "status_lang": "  [bold]Language:[/bold] {lang}",
        "status_mode": "  [bold]Mode:[/bold] {mode}",
        "status_workspace": "  [bold]Workspace:[/bold] {workspace}",
        "status_ov_mount": "  [bold]OpenViking Mount:[/bold] {mount}",
        "status_qmd_coll": "  [bold]QMD Collection:[/bold] {coll}",
        "status_mcp_port": "  [bold]MCP Port:[/bold] {port}",
        "config_desc": "View current configuration file path and content",
        "config_title": "[bold cyan]⚙️ Config File:[/bold cyan] {path}",
        "config_content": "\n[bold]Content:[/bold]\n" + "-"*40,
        "config_not_found": "[yellow]⚠️ config.yaml not found, using default embedded configuration.[/yellow]",
        "mcp_desc": "Start MCP Server for Claude integration",
        "mcp_start": "[bold cyan]🔌 Starting ContextBridge MCP Service...[/bold cyan]",
        "lang_desc": "切换显示语言 / Switch display language",
        "lang_success": "[bold green]✅ Language switched to: {lang}[/bold green]",
        "workspace_init": "[dim]Workspace initialized at {dir} (mode: {mode})[/dim]",
        
        # model_downloader.py
        "mdl_first_run": "\n[bold cyan]✨ First run: Preparing local AI vector model ({model_name})[/bold cyan]",
        "mdl_desc": "[dim]This model converts your documents into AI-understandable mathematical vectors. It only needs to be downloaded once.[/dim]",
        "mdl_downloading": "Downloading model...",
        "mdl_extracting": "[bold green]✅ Download complete! Extracting model...[/bold green]",
        "mdl_ready": "[bold green]🎉 Model is ready![/bold green]\n",
        "mdl_failed": "\n[bold red]❌ Model download failed: {error}[/bold red]",
        "mdl_hint": "[yellow]💡 Hint: This is usually due to slow network connection to AWS S3.[/yellow]",
        "mdl_manual": "[yellow]Please try using a proxy, or manually download the following link and extract it to {cache_dir}:[/yellow]",
        
        # openviking_manager.py
        "ov_init_embed": "[dim]⚙️ Initializing embedded OpenViking manager, mount path: {mount_path}[/dim]",
        "ov_init_ext": "[dim]🔗 Connecting to external OpenViking service: {endpoint}, mount path: {mount_path}[/dim]",
        "ov_write_embed": "[cyan]📝 [OpenViking] Processing context:[/cyan] {uri}",
        "ov_write_ext": "[cyan]📝 [External OpenViking] Simulating context write via API[/cyan] {uri}",
        "ov_del_embed": "[yellow]🗑️ [OpenViking] Deleting context:[/yellow] {uri}",
        "ov_del_ext": "[yellow]🗑️ [External OpenViking] Simulating context deletion via API[/yellow] {uri}",
        "ov_ret_embed": "[magenta]🧠 [OpenViking] Executing directory recursive retrieval strategy:[/magenta] '{query}'",
        "ov_ret_ext": "[magenta]🧠 [External OpenViking] Simulating recursive retrieval to {endpoint}:[/magenta] '{query}'",
        
        # qmd_runtime.py
        "qmd_init_embed": "[dim]⚙️ Initializing embedded QMD engine (based on ChromaDB)...[/dim]",
        "qmd_init_ext": "[dim]🔗 Connecting to external QMD service: {endpoint}, collection: {collection}[/dim]",
        "qmd_write_ext": "[cyan]📝 [External QMD] Simulating document write to {endpoint}/{collection}[/cyan] {doc_id}",
        "qmd_del_ext": "[yellow]🗑️ [External QMD] Simulating URI deletion to {endpoint}/{collection}:[/yellow] {uri}",
        "qmd_search_ext": "[magenta]🔍 [External QMD] Simulating hybrid search to {endpoint}/{collection}:[/magenta] '{query}'",
        
        # parser.py
        "parse_start": "[dim]📄 Parsing document:[/dim] {file_path}",
        "parse_failed": "[bold red]❌ Parsing failed {file_path}:[/bold red] {error}",
        
        # watcher.py
        "watch_del": "[yellow]🗑️ File deleted:[/yellow] {name}",
        "watch_event": "[green]📄 File {event}:[/green] {name}",
        "watch_ev_create": "created",
        "watch_ev_modify": "modified",
        "watch_ev_delete": "deleted",
        "idx_no_files": "[yellow]📭 No files found to index.[/yellow]",
        "idx_found": "[bold cyan]📦 Found {count} files, starting index build...[/bold cyan]",
        "idx_ghost_clean": "[yellow]🧹 Found {count} deleted ghost files, cleaning up...[/yellow]",
        "idx_progress": "Parsing and vectorizing...",
        "idx_file_count": "{completed}/{total} files",
        "idx_complete": "[bold green]✅ Index build complete![/bold green]",
        "watch_dir": "[bold cyan]👀 Monitoring directory changes:[/bold cyan] {dir}",
    }
}

def t(key, **kwargs):
    lang = CONFIG.get("language", "zh")
    if lang not in MESSAGES:
        lang = "zh"
    text = MESSAGES[lang].get(key, MESSAGES["zh"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text
