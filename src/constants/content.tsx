import React from 'react';
import { Database, Terminal, FolderSync, Settings, Activity, Zap, BookOpen, FileText } from 'lucide-react';

export const APP_CONTENT = {
  en: {
    title: "ContextBridge",
    badgeText: "Now live on PyPI",
    heroTitle: "Give ",
    heroHighlight: "AI Agents",
    heroSuffix: " Instant Access to Your Local Documents",
    subtitle: "A lightweight Knowledge Base plugin for openclaw, Cursor and other AI agents. Let your AI assistants directly read and understand your local Word, Excel, and PDF files.",
    docsSection: "Documentation",
    docCards: [
      {
        icon: BookOpen,
        title: "User Guide",
        desc: "Complete setup and usage instructions for ContextBridge"
      },
      {
        icon: Zap,
        title: "OpenClaw Integration",
        desc: "Install and use ContextBridge as an OpenClaw Skill"
      }
    ],
    features: [
      {
        icon: Settings,
        title: "Interactive Setup",
        desc: <>Run <code className="text-indigo-300">cbridge init</code> for a guided setup. Choose between embedded mode or connect to external instances instantly.</>
      },
      {
        icon: FolderSync,
        title: "Smart Folder Watcher",
        desc: <>Effortlessly track project directories with <code className="text-indigo-300">cbridge watch</code>. Add or remove context sources instantly without restarts.</>
      },
      {
        icon: Activity,
        title: "Real-time CRUD Sync",
        desc: "Instantly detects file creations, modifications, and deletions. ContextBridge automatically parses and updates your vector index in real-time."
      },
      {
        icon: Terminal,
        title: "Visual Indexing",
        desc: <>Run <code className="text-indigo-300">cbridge index</code> to batch process your documents with a beautiful, real-time progress bar powered by tqdm.</>
      },
      {
        icon: Database,
        title: "Batteries Included",
        desc: "Comes with an embedded ChromaDB search runtime. No need to manually install external databases or initialize indexes."
      },
      {
        icon: FileText,
        title: "Multi-Format Support",
        desc: "Seamlessly handles Word, Excel, PDF, and Markdown. ContextBridge automatically parses your diverse local documents into high-fidelity context for your agents."
      }
    ],
    quickStart: "Quick Start",
    steps: [
      { comment: "# 1. Install ContextBridge globally", cmd: "pip install cbridge-agent" },
      { comment: "# 2. Interactive Initialization", cmd: "cbridge init" },
      { comment: "# 3. Add folders to monitor", cmd: "cbridge watch add ~/Documents/MyProjects" },
      { comment: "# 4. Build initial index with progress bar", cmd: "cbridge index" },
      { comment: "# 5. Start the real-time watcher & MCP Server", cmd: "cbridge start" },
      { comment: "# 6. Test with the demo document", cmd: 'cbridge search "ContextBridge"' }
    ]
  },
  zh: {
    title: "ContextBridge",
    badgeText: "已在 PyPI 发布",
    heroTitle: "让 ",
    heroHighlight: "AI 智能体",
    heroSuffix: <> 瞬间读懂你的<span className="whitespace-nowrap">本地文档</span></>,
    subtitle: "专为 Openclaw、Cursor 等智能体设计的极速知识库外挂。让你的 AI 助手直接读取、理解本地的 Word、Excel 和 PDF 文件，无需上传，隐私安全。",
    docsSection: "文档中心",
    docCards: [
      {
        icon: BookOpen,
        title: "使用指南",
        desc: "ContextBridge 的完整设置和使用说明"
      },
      {
        icon: Zap,
        title: "OpenClaw 集成",
        desc: "将 ContextBridge 作为 OpenClaw Skill 安装和使用"
      }
    ],
    features: [
      {
        icon: Settings,
        title: "交互式配置",
        desc: <>运行 <code className="text-indigo-300">cbridge init</code> 进行引导式设置。可选择内嵌模式或一键接入外部服务。</>
      },
      {
        icon: FolderSync,
        title: "智能目录监控",
        desc: <>使用 <code className="text-indigo-300">cbridge watch</code> 命令轻松追踪项目目录。无需重启，即可实时动态增减上下文来源。</>
      },
      {
        icon: Activity,
        title: "毫秒级增量同步",
        desc: "精准捕捉文件创建、修改及删除。ContextBridge 会在后台自动完成毫秒级解析并同步更新向量索引。"
      },
      {
        icon: Terminal,
        title: "可视化索引",
        desc: <>运行 <code className="text-indigo-300">cbridge index</code> 批量处理文档，内置基于 tqdm 的美观实时进度条。</>
      },
      {
        icon: Database,
        title: "开箱即用",
        desc: "内置 ChromaDB 检索运行时。无需手动安装外部数据库或初始化索引。"
      },
      {
        icon: FileText,
        title: "多格式支持",
        desc: "完美支持 Word、Excel、PDF 及 Markdown。ContextBridge 会自动将多种格式的本地文档解析为高保真 Markdown，为智能体提供精准上下文。"
      }
    ],
    quickStart: "快速开始",
    steps: [
      { comment: "# 1. 全局安装 ContextBridge", cmd: "pip install cbridge-agent" },
      { comment: "# 2. 交互式初始化", cmd: "cbridge init" },
      { comment: "# 3. 添加监控目录", cmd: "cbridge watch add ~/Documents/MyProjects" },
      { comment: "# 4. 构建初始索引（带进度条）", cmd: "cbridge index" },
      { comment: "# 5. 启动实时监控与 MCP 服务", cmd: "cbridge start" },
      { comment: "# 6. 使用内置 Demo 文档进行测试", cmd: 'cbridge search "ContextBridge"' }
    ]
  }
};
