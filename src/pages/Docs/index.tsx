import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import { ArrowLeft } from 'lucide-react';
import enDocs from '../../../docs/usage_en.md?raw';
import zhDocs from '../../../docs/usage_zh.md?raw';
import enOpenClawDocs from '../../../docs/openclaw_integration_en.md?raw';
import zhOpenClawDocs from '../../../docs/openclaw_integration_zh.md?raw';

interface DocsPageProps {
  lang: 'en' | 'zh';
}

export default function DocsPage({ lang }: DocsPageProps) {
  const { docType } = useParams<{ docType: string }>();
  const navigate = useNavigate();

  const getContent = () => {
    if (docType === 'openclaw') {
      return lang === 'en' ? enOpenClawDocs : zhOpenClawDocs;
    }
    return lang === 'en' ? enDocs : zhDocs;
  };

  const content = getContent();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [docType]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0a0a0a] pt-20 sm:pt-24 pb-12 sm:pb-20 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto">
        <button 
          onClick={() => navigate('/')}
          className="mb-8 flex items-center gap-2 text-slate-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-white transition-colors group"
        >
          <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-white/5 flex items-center justify-center group-hover:bg-indigo-50 dark:group-hover:bg-white/10 transition-colors">
            <ArrowLeft className="text-slate-600 dark:text-gray-400 group-hover:text-indigo-600 dark:group-hover:text-white" size={18} />
          </div>
          <span className="text-sm sm:text-base">{lang === 'en' ? 'Back to Home' : '返回首页'}</span>
        </button>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="prose prose-indigo dark:prose-invert max-w-none prose-sm sm:prose-base prose-pre:bg-slate-50 dark:prose-pre:bg-[#111] prose-pre:border prose-pre:border-slate-200 dark:prose-pre:border-white/10 prose-pre:text-xs sm:prose-pre:text-sm prose-headings:text-slate-900 dark:prose-headings:text-indigo-100 prose-a:text-indigo-600 dark:prose-a:text-indigo-400 hover:prose-a:text-indigo-500 dark:hover:prose-a:text-indigo-300"
        >
          <ReactMarkdown rehypePlugins={[rehypeRaw]}>{content}</ReactMarkdown>
        </motion.div>
      </div>
    </div>
  );
}
