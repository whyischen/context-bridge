import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Terminal, ArrowRight, Copy, Check, BookOpen, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import usageEn from '../../../docs/usage_en.md?raw';
import usageZh from '../../../docs/usage_zh.md?raw';
import openclawEn from '../../../docs/openclaw_integration_en.md?raw';
import openclawZh from '../../../docs/openclaw_integration_zh.md?raw';

interface LandingPageProps {
  lang: 'en' | 'zh';
  t: any;
  copied: boolean;
  copyInstallCmd: () => void;
}

type DocType = 'guide' | 'openclaw' | null;

const DOC_MAP = {
  guide:    { en: usageEn,    zh: usageZh },
  openclaw: { en: openclawEn, zh: openclawZh },
} as const;

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 18 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, delay, ease: 'easeOut' as const },
});

const fadeUpView = (delay = 0) => ({
  initial: { opacity: 0, y: 18 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true },
  transition: { duration: 0.5, delay, ease: 'easeOut' as const },
});

export default function LandingPage({ lang, t, copied, copyInstallCmd }: LandingPageProps) {
  const [activeDoc, setActiveDoc] = useState<DocType>(null);
  const location = useLocation();

  useEffect(() => {
    if (location.hash === '#docs-center') {
      setTimeout(() => {
        document.getElementById('docs-center')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }, [location.hash]);


  const docCards = [
    { id: 'guide'    as const, icon: BookOpen, title: t.docCards[0].title, desc: t.docCards[0].desc },
    { id: 'openclaw' as const, icon: Zap,      title: t.docCards[1].title, desc: t.docCards[1].desc },
  ];

  return (
    <main className="min-h-screen">

      {/* Hero */}
      <section className="relative flex flex-col items-center text-center px-4 pt-28 sm:pt-36 pb-20 sm:pb-28 overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute left-1/2 top-0 -translate-x-1/2 w-[800px] h-[500px] bg-gradient-to-b from-indigo-500/10 via-violet-500/5 to-transparent rounded-full blur-3xl" />
        </div>

        <motion.h1
          {...fadeUp(0.08)}
          className="max-w-3xl text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight leading-[1.25] text-slate-900 dark:text-white mb-5 [font-family:'Noto_Sans_SC',sans-serif] font-black"
        >
          {t.heroTitle}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-cyan-400">
            {t.heroHighlight}
          </span>
          {t.heroSuffix}
        </motion.h1>

        <motion.p
          {...fadeUp(0.16)}
          className="max-w-xl text-base sm:text-lg text-slate-500 dark:text-slate-400 leading-relaxed mb-10"
        >
          {t.subtitle}
        </motion.p>

        <motion.div {...fadeUp(0.24)} className="flex flex-col sm:flex-row items-center gap-3 w-full max-w-md">
          <div className="flex items-center justify-between w-full sm:flex-1 bg-white dark:bg-[#25282c] border border-slate-200 dark:border-white/10 rounded-xl px-4 py-2.5 font-mono text-sm shadow-sm">
            <span className="text-slate-500 dark:text-slate-400 select-all truncate">pip install cbridge-agent</span>
            <button
              onClick={copyInstallCmd}
              className="ml-3 flex-shrink-0 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
              title="Copy"
            >
              {copied ? <Check size={15} className="text-emerald-500" /> : <Copy size={15} />}
            </button>
          </div>
          <a
            href="#quickstart"
            className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 text-white text-sm font-medium transition-colors shadow-lg shadow-indigo-500/25 whitespace-nowrap w-full sm:w-auto"
          >
            {t.quickStart}
            <ArrowRight size={15} />
          </a>
        </motion.div>
      </section>

      {/* Features */}
      <section className="px-4 sm:px-6 pb-20 sm:pb-28">
        <div className="max-w-5xl mx-auto grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {t.features.map((feature: any, idx: number) => (
            <motion.div
              key={idx}
              {...fadeUpView(0.05 * idx)}
              className="group bg-white dark:bg-[#25282c] border border-slate-200 dark:border-white/[0.07] rounded-2xl p-6 hover:border-indigo-300 dark:hover:border-indigo-500/30 hover:shadow-lg hover:shadow-indigo-500/5 transition-all duration-300"
            >
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-50 to-violet-50 dark:from-indigo-500/10 dark:to-violet-500/10 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform duration-300">
                <feature.icon size={18} className="text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-1.5">{feature.title}</h3>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Docs */}
      <section id="docs-center" className="px-4 sm:px-6 pb-20 sm:pb-28">
        <div className="max-w-5xl mx-auto">
          <motion.h2 {...fadeUpView(0)} className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-8 text-center">
            {t.docsSection}
          </motion.h2>

          <AnimatePresence mode="wait" initial={false}>
            {/* ── Collapsed: horizontal card grid ── */}
            {!activeDoc ? (
              <motion.div
                key="grid"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25, ease: 'easeOut' }}
                className="grid sm:grid-cols-2 gap-4 max-w-3xl mx-auto"
              >
                {docCards.map(({ id, icon: Icon, title, desc }, idx) => (
                  <motion.button
                    key={id}
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.35, delay: 0.06 * idx, ease: 'easeOut' }}
                    onClick={() => setActiveDoc(id)}
                    className="group text-left bg-white dark:bg-[#25282c] border border-slate-200 dark:border-white/[0.07] rounded-2xl p-6 hover:border-indigo-300 dark:hover:border-indigo-500/30 hover:shadow-lg hover:shadow-indigo-500/5 transition-all duration-300"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-50 to-violet-50 dark:from-indigo-500/10 dark:to-violet-500/10 flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                        <Icon size={18} className="text-indigo-600 dark:text-indigo-400" />
                      </div>
                      <ArrowRight size={15} className="text-slate-300 dark:text-slate-600 group-hover:text-indigo-500 group-hover:translate-x-0.5 transition-all duration-200 mt-1" />
                    </div>
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-1.5">{title}</h4>
                    <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed">{desc}</p>
                  </motion.button>
                ))}
              </motion.div>
            ) : (
              /* ── Expanded: sidebar + content ── */
              <motion.div
                key="expanded"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                className="flex flex-col lg:flex-row gap-4 items-start"
              >
                {/* Sidebar */}
                <div className="w-full lg:w-52 shrink-0 lg:sticky lg:top-20 flex flex-row lg:flex-col gap-2">
                  {docCards.map(({ id, icon: Icon, title }) => {
                    const isActive = activeDoc === id;
                    return (
                      <button
                        key={id}
                        onClick={() => setActiveDoc(id)}
                        className={`flex-1 lg:flex-none flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium text-left transition-all duration-200 ${
                          isActive
                            ? 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/30'
                            : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-white/[0.05] hover:text-slate-900 dark:hover:text-white border border-transparent'
                        }`}
                      >
                        <Icon size={15} className="shrink-0" />
                        <span className="truncate">{title}</span>
                      </button>
                    );
                  })}
                  {/* Close button */}
                  <button
                    onClick={() => setActiveDoc(null)}
                    className="lg:mt-2 flex-none flex items-center gap-2 px-3 py-2 rounded-xl text-xs text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/[0.05] transition-colors border border-transparent"
                  >
                    <ArrowRight size={13} className="rotate-180 shrink-0" />
                    {lang === 'en' ? 'Back' : '收起'}
                  </button>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeDoc}
                      initial={{ opacity: 0, x: 8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -8 }}
                      transition={{ duration: 0.2, ease: 'easeOut' }}
                      className="bg-white dark:bg-[#25282c] border border-slate-200 dark:border-white/[0.07] rounded-2xl px-6 sm:px-8 py-8"
                    >
                      <div className="prose prose-slate dark:prose-invert max-w-none
                        prose-headings:font-semibold prose-headings:tracking-tight
                        prose-h1:text-xl prose-h1:mb-5 prose-h1:pb-4 prose-h1:border-b prose-h1:border-slate-200 dark:prose-h1:border-white/10
                        prose-h2:text-lg prose-h2:mt-8 prose-h2:mb-3
                        prose-h3:text-base prose-h3:mt-6 prose-h3:mb-2
                        prose-p:text-slate-600 dark:prose-p:text-slate-400 prose-p:leading-7 prose-p:text-sm
                        prose-li:text-slate-600 dark:prose-li:text-slate-400 prose-li:text-sm
                        prose-a:text-indigo-600 dark:prose-a:text-indigo-400 prose-a:no-underline hover:prose-a:underline
                        prose-strong:text-slate-800 dark:prose-strong:text-slate-200
                        prose-code:text-indigo-600 dark:prose-code:text-indigo-400 prose-code:bg-indigo-50 dark:prose-code:bg-indigo-500/10 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md prose-code:text-[0.8em] prose-code:font-normal prose-code:before:content-none prose-code:after:content-none
                        prose-pre:bg-slate-50 dark:prose-pre:bg-[#1e2124] prose-pre:border prose-pre:border-slate-200 dark:prose-pre:border-white/[0.07] prose-pre:rounded-xl prose-pre:text-xs
                      ">
                        <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                          {DOC_MAP[activeDoc][lang]}
                        </ReactMarkdown>
                      </div>
                    </motion.div>
                  </AnimatePresence>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </section>

      {/* Quick Start */}
      <section id="quickstart" className="px-4 sm:px-6 pb-24 sm:pb-32">
        <div className="max-w-2xl mx-auto">
          <motion.h2 {...fadeUpView(0)} className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-8 text-center">
            {t.quickStart}
          </motion.h2>
          <motion.div
            {...fadeUpView(0.08)}
            className="rounded-2xl overflow-hidden border border-slate-200 dark:border-white/[0.07] shadow-xl shadow-black/5 dark:shadow-black/30"
          >
            <div className="flex items-center gap-2 px-4 py-3 bg-slate-100 dark:bg-[#2a2d31] border-b border-slate-200 dark:border-white/[0.07]">
              <span className="w-3 h-3 rounded-full bg-red-400/80" />
              <span className="w-3 h-3 rounded-full bg-amber-400/80" />
              <span className="w-3 h-3 rounded-full bg-emerald-400/80" />
              <div className="flex items-center gap-1.5 ml-3">
                <Terminal size={12} className="text-slate-400 dark:text-slate-500" />
                <span className="text-xs font-mono text-slate-400 dark:text-slate-500">bash</span>
              </div>
            </div>
            <div className="bg-white dark:bg-[#1e2124] px-5 py-5 font-mono text-xs sm:text-sm space-y-4">
              {t.steps.map((step: any, idx: number) => (
                <div key={idx}>
                  <p className="text-slate-400 dark:text-slate-500 mb-1 select-none">{step.comment}</p>
                  <p className="text-indigo-600 dark:text-indigo-300">
                    <span className="text-slate-400 dark:text-slate-500 mr-2 select-none">$</span>
                    {step.cmd}
                  </p>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

    </main>
  );
}
