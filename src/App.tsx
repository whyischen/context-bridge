/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Brain, Database, FileText, Terminal, FolderSync, Settings, Activity, Languages, Zap, ArrowRight, Github, Copy, Check, Blocks, BookOpen } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import enDocs from '../docs/usage_en.md?raw';
import zhDocs from '../docs/usage_zh.md?raw';
import enOpenClawDocs from '../docs/openclaw_integration_en.md?raw';
import zhOpenClawDocs from '../docs/openclaw_integration_zh.md?raw';

const DocsViewer = React.memo(({ lang, activeDoc, onClose }: { lang: 'en' | 'zh', activeDoc: 'guide' | 'openclaw', onClose: () => void }) => {
  const getContent = () => {
    if (activeDoc === 'openclaw') {
      return lang === 'en' ? enOpenClawDocs : zhOpenClawDocs;
    }
    return lang === 'en' ? enDocs : zhDocs;
  };

  const content = getContent();

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    
    window.addEventListener('keydown', handleEsc);
    return () => {
      document.body.style.overflow = 'auto';
      window.removeEventListener('keydown', handleEsc);
    };
  }, [onClose]);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      className="fixed inset-0 z-[100] bg-[#0a0a0a] overflow-y-auto"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        <button 
          onClick={onClose}
          className="mb-8 flex items-center gap-2 text-gray-400 hover:text-white transition-colors group"
        >
          <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-white/10 transition-colors">
            <ArrowRight className="rotate-180" size={18} />
          </div>
          <span className="text-sm sm:text-base">{lang === 'en' ? 'Back to Home' : '返回首页'}</span>
        </button>
        <div className="prose prose-invert prose-indigo max-w-none prose-sm sm:prose-base prose-pre:bg-[#111] prose-pre:border prose-pre:border-white/10 prose-pre:text-xs sm:prose-pre:text-sm prose-headings:text-indigo-100 prose-a:text-indigo-400 hover:prose-a:text-indigo-300">
          <ReactMarkdown rehypePlugins={[rehypeRaw]}>{content}</ReactMarkdown>
        </div>
      </div>
    </motion.div>
  );
});

export default function App() {
  const [lang, setLang] = useState<'en' | 'zh'>('zh');
  const [copied, setCopied] = useState(false);
  const [showDocs, setShowDocs] = useState(false);
  const [activeDoc, setActiveDoc] = useState<'guide' | 'openclaw'>('guide');

  const copyInstallCmd = useCallback(() => {
    navigator.clipboard.writeText('pip install cbridge-agent');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, []);

  const content = useMemo(() => ({
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
      subtitle: "专为 openclaw、Cursor 等智能体设计的极速知识库外挂。让你的 AI 助手直接读取、理解本地的 Word、Excel 和 PDF 文件，无需上传，隐私安全。",
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
  }), []);

  const t = content[lang];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans selection:bg-indigo-500/30">
      {/* Navigation */}
      <nav className="fixed top-0 w-full border-b border-white/10 bg-black/50 backdrop-blur-md z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3 font-bold text-lg sm:text-xl group cursor-pointer selection:bg-transparent" onClick={() => setShowDocs(false)}>
            <div className="relative w-8 sm:w-9 h-8 sm:h-9 flex items-center justify-center transition-transform duration-300 group-hover:scale-105">
              <div className="absolute inset-0 bg-gradient-to-tr from-indigo-500 via-purple-500 to-cyan-400 rounded-xl blur-md opacity-50 group-hover:opacity-80 transition-opacity duration-300"></div>
              <div className="relative w-full h-full bg-gradient-to-tr from-indigo-600 to-cyan-500 rounded-xl flex items-center justify-center shadow-[inset_0_1px_1px_rgba(255,255,255,0.4)] border border-white/20">
                <Blocks size={18} className="sm:w-5 sm:h-5 text-white drop-shadow-md" />
              </div>
            </div>
            <span className="hidden sm:inline bg-clip-text text-transparent bg-gradient-to-r from-white via-indigo-100 to-gray-300 tracking-tight font-sans">ContextBridge</span>
          </div>
          <div className="flex items-center gap-3 sm:gap-6">
            <button 
              onClick={() => setShowDocs(true)}
              className="text-gray-400 hover:text-white transition-colors flex items-center gap-1 sm:gap-2 text-xs sm:text-sm font-medium"
            >
              <FileText size={16} className="sm:w-[18px] sm:h-[18px]" />
              <span className="hidden sm:inline">Docs</span>
            </button>
            <a href="https://github.com/whyischen/ContextBridge" target="_blank" rel="noreferrer" className="text-gray-400 hover:text-white transition-colors flex items-center gap-1 sm:gap-2 text-xs sm:text-sm font-medium">
              <Github size={16} className="sm:w-[18px] sm:h-[18px]" />
              <span className="hidden sm:inline">GitHub</span>
            </a>
            <button 
              onClick={() => setLang(lang === 'en' ? 'zh' : 'en')}
              className="flex items-center gap-1 sm:gap-2 text-gray-400 hover:text-white transition-colors text-xs sm:text-sm font-medium"
            >
              <Languages size={16} className="sm:w-[18px] sm:h-[18px]" />
              <span className="hidden sm:inline">{lang === 'en' ? '中文' : 'English'}</span>
              <span className="sm:hidden">{lang === 'en' ? 'ZH' : 'EN'}</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="pt-20 sm:pt-32 pb-12 sm:pb-20 px-4 sm:px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-3xl sm:text-5xl md:text-7xl font-bold tracking-tight mb-4 sm:mb-6 leading-tight break-keep"
            >
              {t.heroTitle}<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">{t.heroHighlight}</span>{t.heroSuffix}
            </motion.h1>

            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-base sm:text-lg md:text-xl text-gray-400 mb-6 sm:mb-10 max-w-2xl leading-relaxed"
            >
              {t.subtitle}
            </motion.p>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 w-full sm:w-auto"
            >
              <div className="flex items-center justify-between bg-[#141414] border border-white/10 rounded-lg px-3 sm:px-4 py-2 sm:py-3 w-full sm:w-80 font-mono text-xs sm:text-sm">
                <span className="text-gray-300 truncate">$ pip install cbridge-agent</span>
                <button 
                  onClick={copyInstallCmd}
                  className="text-gray-500 hover:text-white transition-colors ml-2 sm:ml-4 flex-shrink-0"
                  title="Copy to clipboard"
                >
                  {copied ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
                </button>
              </div>
              <a 
                href="#quickstart"
                className="flex items-center justify-center gap-2 bg-white text-black px-4 sm:px-6 py-2 sm:py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors w-full sm:w-auto text-sm sm:text-base"
              >
                {t.quickStart}
                <ArrowRight size={18} />
              </a>
            </motion.div>
          </div>

          {/* Features Grid */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mt-16 sm:mt-32">
            {t.features.map((feature, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.1 * idx }}
                className="bg-[#111] border border-white/5 p-6 sm:p-8 rounded-2xl hover:border-white/10 transition-colors"
              >
                <div className="w-10 sm:w-12 h-10 sm:h-12 rounded-xl bg-white/5 flex items-center justify-center mb-4 sm:mb-6">
                  <feature.icon className="w-5 sm:w-6 h-5 sm:h-6 text-indigo-400" />
                </div>
                <h3 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3">{feature.title}</h3>
                <p className="text-sm sm:text-base text-gray-400 leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>

          {/* Documentation Section */}
          <div className="mt-16 sm:mt-32">
            <motion.h2 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-2xl sm:text-3xl font-bold mb-8 sm:mb-12 text-center"
            >
              {t.docsSection}
            </motion.h2>
            
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 max-w-4xl mx-auto">
              {t.docCards.map((card, idx) => (
                <motion.button
                  key={idx}
                  onClick={() => {
                    setActiveDoc(idx === 0 ? 'guide' : 'openclaw');
                    setShowDocs(true);
                  }}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: 0.1 * idx }}
                  className="bg-[#111] border border-white/5 p-6 sm:p-8 rounded-2xl hover:border-white/10 transition-colors text-left"
                >
                  <div className="w-10 sm:w-12 h-10 sm:h-12 rounded-xl bg-white/5 flex items-center justify-center mb-4 sm:mb-6">
                    <card.icon className="w-5 sm:w-6 h-5 sm:h-6 text-indigo-400" />
                  </div>
                  <h4 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3">{card.title}</h4>
                  <p className="text-sm sm:text-base text-gray-400 leading-relaxed">{card.desc}</p>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Quick Start Section */}
          <div id="quickstart" className="mt-16 sm:mt-32 max-w-3xl mx-auto">
            <div className="bg-[#111] border border-white/10 rounded-2xl overflow-hidden">
              <div className="flex items-center px-3 sm:px-4 py-2 sm:py-3 border-b border-white/10 bg-black/50">
                <Terminal className="w-4 sm:w-5 h-4 sm:h-5 text-gray-500 mr-2 sm:mr-3" />
                <span className="text-xs sm:text-sm font-mono text-gray-400">{t.quickStart}</span>
              </div>
              <div className="p-4 sm:p-6 font-mono text-xs sm:text-sm text-gray-300 overflow-x-auto space-y-3 sm:space-y-4">
                {t.steps.map((step, idx) => (
                  <div key={idx}>
                    <p className="text-gray-500 mb-1">{step.comment}</p>
                    <p className="text-indigo-300 break-all sm:break-normal">{step.cmd}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 sm:py-12 mt-16 sm:mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col md:flex-row items-center justify-between text-gray-500 text-xs sm:text-sm gap-4">
          <p>© {new Date().getFullYear()} ContextBridge. Open source under MIT License.</p>
          <div className="flex items-center gap-4">
            <a href="https://github.com/whyischen/ContextBridge" className="hover:text-white transition-colors">GitHub</a>
          </div>
        </div>
      </footer>

      <AnimatePresence>
        {showDocs && <DocsViewer lang={lang} activeDoc={activeDoc} onClose={() => setShowDocs(false)} />}
      </AnimatePresence>
    </div>
  );
}
