/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Brain, Database, FileText, Terminal, FolderSync, Settings, Activity, Languages, Zap, ArrowRight, Github, Copy, Check } from 'lucide-react';
import { motion } from 'framer-motion';

export default function App() {
  const [lang, setLang] = useState<'en' | 'zh'>('zh');
  const [copied, setCopied] = useState(false);

  const copyInstallCmd = () => {
    navigator.clipboard.writeText('pip install cbridge-agent');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const content = {
    en: {
      title: "ContextBridge",
      badge: "v0.1.1",
      heroTitle: "Give ",
      heroHighlight: "AI Agents",
      heroSuffix: " Instant Access to Your Local Documents",
      subtitle: "A lightweight Knowledge Base plugin for openclaw, Cursor and other AI agents. Let your AI assistants directly read and understand your local Word, Excel, and PDF files.",
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
        { comment: "# 6. Test the Magic", cmd: 'cbridge search "Summarize the Q3 revenue"' }
      ]
    },
    zh: {
      title: "ContextBridge",
      badge: "v0.1.1",
      heroTitle: "让 ",
      heroHighlight: "AI 智能体",
      heroSuffix: <> 瞬间读懂你的<span className="whitespace-nowrap">本地文档</span></>,
      subtitle: "专为 openclaw、Cursor 等智能体设计的极速知识库外挂。让你的 AI 助手直接读取、理解本地的 Word、Excel 和 PDF 文件，无需上传，隐私安全。",
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
        { comment: "# 6. 见证奇迹的时刻", cmd: 'cbridge search "Q3的营收是多少？"' }
      ]
    }
  };

  const t = content[lang];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans selection:bg-indigo-500/30">
      {/* Navigation */}
      <nav className="fixed top-0 w-full border-b border-white/10 bg-black/50 backdrop-blur-md z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-mono font-bold text-lg">
            <div className="w-8 h-8 rounded bg-indigo-500 flex items-center justify-center">
              <Zap size={18} className="text-white" />
            </div>
            cbridge-agent
          </div>
          <div className="flex items-center gap-6">
            <button 
              onClick={() => setLang(lang === 'en' ? 'zh' : 'en')}
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors text-sm font-medium"
            >
              <Languages size={18} />
              {lang === 'en' ? '中文' : 'English'}
            </button>
            <a href="https://github.com/whyischen/ContextBridge" target="_blank" rel="noreferrer" className="text-gray-400 hover:text-white transition-colors flex items-center gap-2 text-sm font-medium">
              <Github size={18} />
              GitHub
            </a>
            <a href="https://pypi.org/project/cbridge-agent/" target="_blank" rel="noreferrer" className="text-gray-400 hover:text-white transition-colors text-sm font-medium">
              PyPI
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-sm font-medium mb-8 border border-indigo-500/20"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
              </span>
              {t.badge} is now live on PyPI
            </motion.div>

            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight break-keep"
            >
              {t.heroTitle}<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">{t.heroHighlight}</span>{t.heroSuffix}
            </motion.h1>

            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-xl text-gray-400 mb-10 max-w-2xl leading-relaxed"
            >
              {t.subtitle}
            </motion.p>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto"
            >
              <div className="flex items-center justify-between bg-[#141414] border border-white/10 rounded-lg px-4 py-3 w-full sm:w-80 font-mono text-sm">
                <span className="text-gray-300">$ pip install cbridge-agent</span>
                <button 
                  onClick={copyInstallCmd}
                  className="text-gray-500 hover:text-white transition-colors ml-4"
                  title="Copy to clipboard"
                >
                  {copied ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
                </button>
              </div>
              <a 
                href="#quickstart"
                className="flex items-center justify-center gap-2 bg-white text-black px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors w-full sm:w-auto"
              >
                {t.quickStart}
                <ArrowRight size={18} />
              </a>
            </motion.div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-32">
            {t.features.map((feature, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.1 * idx }}
                className="bg-[#111] border border-white/5 p-8 rounded-2xl hover:border-white/10 transition-colors"
              >
                <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-6">
                  <feature.icon className="w-6 h-6 text-indigo-400" />
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-gray-400 leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>

          {/* Quick Start Section */}
          <div id="quickstart" className="mt-32 max-w-3xl mx-auto">
            <div className="bg-[#111] border border-white/10 rounded-2xl overflow-hidden">
              <div className="flex items-center px-4 py-3 border-b border-white/10 bg-black/50">
                <Terminal className="w-5 h-5 text-gray-500 mr-3" />
                <span className="text-sm font-mono text-gray-400">{t.quickStart}</span>
              </div>
              <div className="p-6 font-mono text-sm text-gray-300 overflow-x-auto space-y-4">
                {t.steps.map((step, idx) => (
                  <div key={idx}>
                    <p className="text-gray-500 mb-1">{step.comment}</p>
                    <p className="text-indigo-300">{step.cmd}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 mt-20">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between text-gray-500 text-sm">
          <p>© {new Date().getFullYear()} ContextBridge. Open source under MIT License.</p>
          <div className="flex items-center gap-4 mt-4 md:mt-0">
            <a href="https://github.com/whyischen/cbridge" className="hover:text-white transition-colors">GitHub</a>
            <a href="https://pypi.org/project/cbridge-agent/" className="hover:text-white transition-colors">PyPI</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
