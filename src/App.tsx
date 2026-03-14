/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Brain, Database, FileText, Terminal, FolderSync, Settings, Activity, Languages } from 'lucide-react';

export default function App() {
  const [lang, setLang] = useState<'en' | 'zh'>('zh');

  const content = {
    en: {
      title: "ContextBridge",
      badge: "Beta",
      subtitle: "The All-in-One Local Memory Bridge for AI Agents. Feed your local AI Agents with Office documents, instantly. Batteries included.",
      features: [
        {
          icon: Settings,
          title: "Interactive Setup",
          desc: <>Run <code className="text-emerald-300">cbridge init</code> for a guided setup. Choose between embedded mode or connect to external OpenViking and QMD instances instantly.</>
        },
        {
          icon: FolderSync,
          title: "Dynamic Monitoring",
          desc: <>Easily add, list, or remove watched directories on the fly using the <code className="text-emerald-300">cbridge watch</code> commands. No manual config editing needed.</>
        },
        {
          icon: Activity,
          title: "Real-time CRUD Sync",
          desc: "Instantly detects file creations, modifications, and deletions. ContextBridge automatically parses and updates your vector index in real-time."
        },
        {
          icon: Terminal,
          title: "Visual Indexing",
          desc: <>Run <code className="text-emerald-300">cbridge index</code> to batch process your documents with a beautiful, real-time progress bar powered by tqdm.</>
        },
        {
          icon: Database,
          title: "Batteries Included",
          desc: "Comes with an embedded QMD search runtime. No need to manually install Bun, configure PATHs, or initialize indexes."
        },
        {
          icon: FileText,
          title: "High-Fidelity Parsing",
          desc: "Drop a Word, Excel, or PDF file into the watched folder. ContextBridge automatically parses it to high-fidelity Markdown."
        }
      ],
      quickStart: "Quick Start",
      steps: [
        { comment: "# 1. Install ContextBridge globally", cmd: "pip install -e ." },
        { comment: "# 2. Interactive Initialization", cmd: "cbridge init" },
        { comment: "# 3. Add folders to monitor", cmd: "cbridge watch add ~/Documents/MyProjects" },
        { comment: "# 4. Build initial index with progress bar", cmd: "cbridge index" },
        { comment: "# 5. Start the real-time watcher", cmd: "cbridge start" },
        { comment: "# 6. Test the Magic", cmd: 'cbridge search "Summarize the Q3 revenue"' }
      ]
    },
    zh: {
      title: "ContextBridge",
      badge: "Beta",
      subtitle: "专为 AI 智能体打造的一站式本地记忆桥梁。让您的本地 AI 智能体瞬间读取 Office 文档。开箱即用。",
      features: [
        {
          icon: Settings,
          title: "交互式配置",
          desc: <>运行 <code className="text-emerald-300">cbridge init</code> 进行引导式设置。可选择内嵌模式或一键接入外部 OpenViking 和 QMD 服务。</>
        },
        {
          icon: FolderSync,
          title: "动态目录监控",
          desc: <>使用 <code className="text-emerald-300">cbridge watch</code> 命令随时添加、查看或移除监控目录，无需手动修改配置文件。</>
        },
        {
          icon: Activity,
          title: "实时增删改同步",
          desc: "瞬间感知文件的创建、修改和删除。ContextBridge 会自动解析并在后台实时更新向量索引。"
        },
        {
          icon: Terminal,
          title: "可视化索引",
          desc: <>运行 <code className="text-emerald-300">cbridge index</code> 批量处理文档，内置基于 tqdm 的美观实时进度条。</>
        },
        {
          icon: Database,
          title: "开箱即用",
          desc: "内置 QMD 检索运行时。无需手动安装 Bun、配置环境变量或初始化索引。"
        },
        {
          icon: FileText,
          title: "高保真解析",
          desc: "将 Word、Excel 或 PDF 文件拖入监控目录，ContextBridge 会自动将其解析为高保真 Markdown。"
        }
      ],
      quickStart: "快速开始",
      steps: [
        { comment: "# 1. 全局安装 ContextBridge", cmd: "pip install -e ." },
        { comment: "# 2. 交互式初始化", cmd: "cbridge init" },
        { comment: "# 3. 添加监控目录", cmd: "cbridge watch add ~/Documents/MyProjects" },
        { comment: "# 4. 构建初始索引（带进度条）", cmd: "cbridge index" },
        { comment: "# 5. 启动实时监控", cmd: "cbridge start" },
        { comment: "# 6. 见证奇迹的时刻", cmd: 'cbridge search "Q3的营收是多少？"' }
      ]
    }
  };

  const t = content[lang];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 font-sans selection:bg-emerald-500/30 relative">
      <button 
        onClick={() => setLang(lang === 'en' ? 'zh' : 'en')}
        className="absolute top-6 right-6 flex items-center gap-2 px-4 py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-full transition-colors text-sm font-medium text-zinc-300 hover:text-white"
      >
        <Languages className="w-4 h-4" />
        {lang === 'en' ? '中文' : 'English'}
      </button>

      <div className="max-w-5xl mx-auto px-6 py-20">
        <header className="mb-16 text-center">
          <div className="inline-flex items-center justify-center p-4 bg-zinc-900 rounded-2xl mb-6 shadow-lg shadow-black/50 border border-zinc-800">
            <Brain className="w-12 h-12 text-emerald-400" />
          </div>
          <h1 className="text-5xl font-bold tracking-tight mb-6">{t.title} <span className="text-emerald-400">{t.badge}</span></h1>
          <p className="text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
            {t.subtitle}
          </p>
        </header>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {t.features.map((feature, idx) => (
            <div key={idx} className="bg-zinc-900/50 border border-zinc-800 p-8 rounded-2xl">
              <feature.icon className="w-8 h-8 text-emerald-400 mb-4" />
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-zinc-400">{feature.desc}</p>
            </div>
          ))}
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
          <div className="flex items-center px-4 py-3 border-b border-zinc-800 bg-zinc-950/50">
            <Terminal className="w-5 h-5 text-zinc-500 mr-3" />
            <span className="text-sm font-mono text-zinc-400">{t.quickStart}</span>
          </div>
          <div className="p-6 font-mono text-sm text-zinc-300 overflow-x-auto">
            {t.steps.map((step, idx) => (
              <React.Fragment key={idx}>
                <p className="text-zinc-500 mb-2">{step.comment}</p>
                <p className="mb-4">{step.cmd}</p>
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
