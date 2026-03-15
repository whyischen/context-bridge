import sys
from rich.console import Console
from core.config import CONFIG, save_config

console = Console()

class I18nManager:
    def __init__(self):
        self.lang = CONFIG.get("lang", "zh")  # default to zh maybe or en, let's say zh for user ? No, let's default to en but user can change it. Actually, since user requested Chinese/English switch, let's default to "zh" if we detect Chinese or keep "en". Wait, "zh" makes more sense to the user who asked in Chinese. Let's make "zh" default.
        
        self.texts = {
            "en": {
                "welcome_init": "[bold magenta]🌟 Welcome to ContextBridge Initialization! 🌟[/]",
                "choose_mode": "Choose mode (embedded/external)",
                "ov_endpoint": "OpenViking Endpoint",
                "ov_mount": "OpenViking Mount Path",
                "qmd_endpoint": "QMD Endpoint",
                "qmd_collection": "QMD Collection",
                "workspace_dir": "Workspace Directory",
                "config_saved": "[green]✨ Configuration saved to {path}[/]",
                "monitored_dirs": "[cyan]📂 Currently monitored directories:[/]",
                "dir_item": "  [yellow]- {path}[/]",
                "dir_added": "[green]✅ Added '{path}' to monitored directories.[/]",
                "dir_already_monitored": "[yellow]⚠️ '{path}' is already being monitored.[/]",
                "dir_removed": "[green]🗑️ Removed '{path}' from monitored directories.[/]",
                "dir_not_in_list": "[yellow]⚠️ '{path}' was not in the monitored list.[/]",
                "start_indexing": "[cyan]🚀 Starting indexing process...[/]",
                "init_workspace": "[cyan]🔮 Initializing ContextBridge Workspace...[/]",
                "start_engine": "[bold green]🚀 Starting ContextBridge Engine...[/]",
                "no_results": "[yellow]📭 No results found.[/]",
                "search_results_title": "\n[bold cyan]🔍 Search Results for: '{query}'[/]\n[cyan]{divider}[/]",
                "search_result_item": "\n[bold green]📄 Source: {source} (Score: {score:.4f})[/]\n[dim]{divider}[/]\n{content}\n",
                "status_title": "[bold cyan]📊 ContextBridge Status:[/]",
                "status_mode": "  [yellow]Mode:[/] {mode}",
                "status_workspace": "  [yellow]Workspace:[/] {workspace}",
                "status_ov_mount": "  [yellow]OpenViking Mount:[/] {ov_mount}",
                "status_qmd_coll": "  [yellow]QMD Collection:[/] {qmd_collection}",
                "status_mcp_port": "  [yellow]MCP Port:[/] {mcp_port}",
                "status_lang": "  [yellow]Language:[/] {lang}",
                "config_file": "[cyan]📝 Config File: {path}[/]",
                "config_contents": "\n[bold]Contents:[/]\n[dim]{divider}[/]",
                "no_config": "[yellow]⚠️ No config.yaml found. Using default embedded settings.[/]",
                "start_mcp": "[bold green]🔌 Starting ContextBridge MCP Server...[/]",
                "file_deleted": "[yellow]❌ File deleted:[/] {name}",
                "file_event": "[cyan]📝 File {event_type}:[/] {name}",
                "no_files_index": "[yellow]📭 No files found to index.[/]",
                "found_files_index": "[cyan]🔎 Found {count} files. Starting initial indexing...[/]",
                "index_complete": "[bold green]✅ Indexing complete![/]",
                "indexing_files": "Indexing files...",
                "watching_dirs": "[cyan]👀 Watching for document changes in {dir}...[/]",
                "workspace_initialized": "[green]✨ Workspace initialized at {workspace} in {mode} mode[/]",
                "choose_lang": "Language (en/zh)",
                "lang_set": "[green]🗣️ Language set to English![/]",
                "qmd_init_embedded": "\n[dim cyan]⚙️  Initializing Embedded QMD Engine (ChromaDB)...[/]",
                "qmd_init_external": "\n[dim cyan]⚙️  Connecting to External QMD Service: {endpoint}, Collection: {collection}[/]",
                "ov_init_embedded": "[dim cyan]⚙️  Initializing Embedded OpenViking Manager, Mount: {mount_path}[/]\n",
                "ov_init_external": "[dim cyan]⚙️  Connecting to External OpenViking Service: {endpoint}, Mount: {mount_path}[/]\n",
                "ov_proc_ctx": "[dim]↳ Processing context: {uri}[/]",
                "ov_proc_ctx_ext": "[dim]↳ API Request to write context: {uri}[/]",
                "ov_del_ctx": "[dim]↳ Deleting context: {uri}[/]",
                "ov_del_ctx_ext": "[dim]↳ API Request to delete context: {uri}[/]",
                "ov_recursive_ret": "[dim]↳ Recursive Retrieval Strategy: {query}[/]",
                "ov_recursive_ret_ext": "[dim]↳ API Request for Recursive Retrieval: {query}[/]",
                "qmd_write_ext": "[dim]↳ Ext QMD API Request write document: {doc_id}[/]",
                "qmd_del_ext": "[dim]↳ Ext QMD API Request delete URI: {uri}[/]",
                "qmd_ret_ext": "[dim]↳ Ext QMD API Request hybrid search: {query}[/]"
            },
            "zh": {
                "welcome_init": "[bold magenta]🌟 欢迎来到 ContextBridge 初始化向导！🌟[/]",
                "choose_mode": "请选择运行模式 (embedded-内置/external-外置)",
                "ov_endpoint": "OpenViking 节点地址",
                "ov_mount": "OpenViking 挂载路径",
                "qmd_endpoint": "QMD 节点地址",
                "qmd_collection": "QMD 数据库集名",
                "workspace_dir": "工作区目录",
                "config_saved": "[green]✨ 配置已成功保存至 {path}[/]",
                "monitored_dirs": "[cyan]📂 当前正在监控的目录:[/]",
                "dir_item": "  [yellow]📍 {path}[/]",
                "dir_added": "[green]✅ 已成功将 '{path}' 添加到监控目录中。[/]",
                "dir_already_monitored": "[yellow]⚠️ 目录 '{path}' 已经在监控列表中。[/]",
                "dir_removed": "[green]🗑️ 已成功从监控目录中移除 '{path}'。[/]",
                "dir_not_in_list": "[yellow]⚠️ 目录 '{path}' 不在当前的监控列表中。[/]",
                "start_indexing": "[cyan]🚀 正在启动索引流程...[/]",
                "init_workspace": "[cyan]🔮 正在初始化 ContextBridge 工作区...[/]",
                "start_engine": "[bold green]🚀 正在启动 ContextBridge 核心引擎...[/]",
                "no_results": "[yellow]📭 未找到相关结果。[/]",
                "search_results_title": "\n[bold cyan]🔍 搜索 '{query}' 的相关结果：[/]\n[cyan]{divider}[/]",
                "search_result_item": "\n[bold green]📄 来源: {source} (评分: {score:.4f})[/]\n[dim]{divider}[/]\n{content}\n",
                "status_title": "[bold cyan]📊 ContextBridge 当前状态:[/]",
                "status_mode": "  [yellow]运行模式:[/] {mode}",
                "status_workspace": "  [yellow]工作区目录:[/] {workspace}",
                "status_ov_mount": "  [yellow]OpenViking 挂载点:[/] {ov_mount}",
                "status_qmd_coll": "  [yellow]QMD 数据库集名:[/] {qmd_collection}",
                "status_mcp_port": "  [yellow]MCP 端口:[/] {mcp_port}",
                "status_lang": "  [yellow]当前语言:[/] {lang}",
                "config_file": "[cyan]📝 配置文件路径: {path}[/]",
                "config_contents": "\n[bold]配置内容如下:[/]\n[dim]{divider}[/]",
                "no_config": "[yellow]⚠️ 未找到 config.yaml 配置文件。正在使用默认的内置设置。[/]",
                "start_mcp": "[bold green]🔌 正在启动 ContextBridge MCP 服务界面...[/]",
                "file_deleted": "[yellow]❌ 发现文件已被删除:[/] {name}",
                "file_event": "[cyan]📝 发现文件已被{event_type}:[/] {name}",
                "no_files_index": "[yellow]📭 未找到需要索引的文件。[/]",
                "found_files_index": "[cyan]🔎 共找到 {count} 个文件。开始执行初次索引...[/]",
                "index_complete": "[bold green]✅ 索引构建完成！[/]",
                "indexing_files": "正在构建文件索引...",
                "watching_dirs": "[cyan]👀 正在监控 {dir} 目录下的文档变化...[/]",
                "workspace_initialized": "[green]✨ 工作区已在 {workspace} 成功初始化 (模式: {mode})[/]",
                "choose_lang": "选择语言 (en/zh)",
                "lang_set": "[green]🗣️ 界面语言已切换为中文！[/]",
                "qmd_init_embedded": "\n[dim cyan]⚙️  初始化内嵌 QMD 引擎 (基于 ChromaDB 模拟)...[/]",
                "qmd_init_external": "\n[dim cyan]⚙️  接入外部 QMD 服务: {endpoint}, 数据库集: {collection}[/]",
                "ov_init_embedded": "[dim cyan]⚙️  初始化内嵌 OpenViking 管理器, 挂载路径: {mount_path}[/]\n",
                "ov_init_external": "[dim cyan]⚙️  接入外部 OpenViking 服务: {endpoint}, 挂载路径: {mount_path}[/]\n",
                "ov_proc_ctx": "[dim]↳ 正在处理上下文: {uri}[/]",
                "ov_proc_ctx_ext": "[dim]↳ 模拟通过 API 将上下文写入 {uri}[/]",
                "ov_del_ctx": "[dim]↳ 正在删除上下文: {uri}[/]",
                "ov_del_ctx_ext": "[dim]↳ 模拟通过 API 删除上下文 {uri}[/]",
                "ov_recursive_ret": "[dim]↳ 执行目录递归检索策略: {query}[/]",
                "ov_recursive_ret_ext": "[dim]↳ 模拟向外部服务发起递归检索: {query}[/]",
                "qmd_write_ext": "[dim]↳ 外部 QMD 模拟写入文档 {doc_id}[/]",
                "qmd_del_ext": "[dim]↳ 外部 QMD 模拟删除 URI: {uri}[/]",
                "qmd_ret_ext": "[dim]↳ 外部 QMD 模拟进行混合检索: {query}[/]"
            }
        }
        
    def set_lang(self, lang):
        if lang in self.texts:
            self.lang = lang
            CONFIG["lang"] = lang
            save_config(CONFIG)

    def get(self, key, **kwargs):
        text = self.texts.get(self.lang, self.texts["en"]).get(key, key)
        return text.format(**kwargs)

    def print(self, key, **kwargs):
        console.print(self.get(key, **kwargs))

    def raw_print(self, text):
        console.print(text)

i18n = I18nManager()
