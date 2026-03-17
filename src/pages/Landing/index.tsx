import React from 'react';
import { Database, FileText, Terminal, FolderSync, Settings, Activity, Zap, ArrowRight, Copy, Check, BookOpen } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

interface LandingPageProps {
  lang: 'en' | 'zh';
  t: any;
  copied: boolean;
  copyInstallCmd: () => void;
}

export default function LandingPage({ lang, t, copied, copyInstallCmd }: LandingPageProps) {
  const navigate = useNavigate();

  return (
    <main className="pt-20 sm:pt-32 pb-12 sm:pb-20 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-3xl sm:text-5xl md:text-7xl font-bold tracking-tight mb-4 sm:mb-6 leading-tight break-keep text-slate-900 dark:text-white"
          >
            {t.heroTitle}<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-cyan-600 dark:from-indigo-400 dark:to-cyan-400">{t.heroHighlight}</span>{t.heroSuffix}
          </motion.h1>

          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-base sm:text-lg md:text-xl text-slate-600 dark:text-gray-400 mb-6 sm:mb-10 max-w-2xl leading-relaxed"
          >
            {t.subtitle}
          </motion.p>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 w-full sm:w-auto"
          >
            <div className="flex items-center justify-between bg-slate-50 dark:bg-[#141414] border border-slate-200 dark:border-white/10 rounded-lg px-3 sm:px-4 py-2 sm:py-3 w-full sm:w-80 font-mono text-xs sm:text-sm">
              <span className="text-slate-600 dark:text-gray-300 truncate">$ pip install cbridge-agent</span>
              <button 
                onClick={copyInstallCmd}
                className="text-slate-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-white transition-colors ml-2 sm:ml-4 flex-shrink-0"
                title="Copy to clipboard"
              >
                {copied ? <Check size={16} className="text-green-600 dark:text-green-400" /> : <Copy size={16} />}
              </button>
            </div>
            <a 
              href="#quickstart"
              className="flex items-center justify-center gap-2 bg-indigo-600 dark:bg-white text-white dark:text-black px-4 sm:px-6 py-2 sm:py-3 rounded-lg font-medium hover:bg-indigo-700 dark:hover:bg-gray-200 transition-colors w-full sm:w-auto text-sm sm:text-base shadow-lg shadow-indigo-500/20 dark:shadow-none"
            >
              {t.quickStart}
              <ArrowRight size={18} />
            </a>
          </motion.div>
        </div>

        {/* Features Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mt-16 sm:mt-32">
          {t.features.map((feature: any, idx: number) => (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 * idx }}
              className="bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/5 p-6 sm:p-8 rounded-2xl hover:border-indigo-500/30 dark:hover:border-white/10 transition-all hover:shadow-xl hover:shadow-indigo-500/5"
            >
              <div className="w-10 sm:w-12 h-10 sm:h-12 rounded-xl bg-indigo-50 dark:bg-white/5 flex items-center justify-center mb-4 sm:mb-6">
                <feature.icon className="w-5 sm:w-6 h-5 sm:h-6 text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3 text-slate-900 dark:text-white">{feature.title}</h3>
              <p className="text-sm sm:text-base text-slate-600 dark:text-gray-400 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>

        {/* Documentation Section */}
        <div id="docs-center" className="mt-16 sm:mt-32">
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-2xl sm:text-3xl font-bold mb-8 sm:mb-12 text-center"
          >
            {t.docsSection}
          </motion.h2>
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 max-w-4xl mx-auto">
            {t.docCards.map((card: any, idx: number) => (
              <motion.button
                key={idx}
                onClick={() => {
                  const docType = idx === 0 ? 'guide' : 'openclaw';
                  navigate(`/docs/${docType}`);
                }}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.1 * idx }}
                className="bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/5 p-6 sm:p-8 rounded-2xl hover:border-indigo-500/30 dark:hover:border-white/10 transition-all text-left hover:shadow-xl hover:shadow-indigo-500/5"
              >
                <div className="w-10 sm:w-12 h-10 sm:h-12 rounded-xl bg-indigo-50 dark:bg-white/5 flex items-center justify-center mb-4 sm:mb-6">
                  <card.icon className="w-5 sm:w-6 h-5 sm:h-6 text-indigo-600 dark:text-indigo-400" />
                </div>
                <h4 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3 text-slate-900 dark:text-white">{card.title}</h4>
                <p className="text-sm sm:text-base text-slate-600 dark:text-gray-400 leading-relaxed">{card.desc}</p>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Quick Start Section */}
        <div id="quickstart" className="mt-16 sm:mt-32 max-w-3xl mx-auto">
          <div className="bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-2xl overflow-hidden shadow-xl shadow-black/5">
            <div className="flex items-center px-3 sm:px-4 py-2 sm:py-3 border-b border-slate-200 dark:border-white/10 bg-white/50 dark:bg-black/50">
              <Terminal className="w-4 sm:w-5 h-4 sm:h-5 text-slate-400 dark:text-gray-500 mr-2 sm:mr-3" />
              <span className="text-xs sm:text-sm font-mono text-slate-500 dark:text-gray-400">{t.quickStart}</span>
            </div>
            <div className="p-4 sm:p-6 font-mono text-xs sm:text-sm text-slate-700 dark:text-gray-300 overflow-x-auto space-y-3 sm:space-y-4">
              {t.steps.map((step: any, idx: number) => (
                <div key={idx}>
                  <p className="text-slate-400 dark:text-gray-500 mb-1">{step.comment}</p>
                  <p className="text-indigo-600 dark:text-indigo-300 break-all sm:break-normal">{step.cmd}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
