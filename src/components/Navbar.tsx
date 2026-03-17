import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { FileText, Github, Languages, Sun, Moon, Monitor, Blocks } from 'lucide-react';

interface NavbarProps {
  lang: 'en' | 'zh';
  setLang: (lang: 'en' | 'zh') => void;
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  isThemeOpen: boolean;
  setIsThemeOpen: (open: boolean) => void;
}

export default function Navbar({ lang, setLang, theme, setTheme, isThemeOpen, setIsThemeOpen }: NavbarProps) {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav className="fixed top-0 w-full border-b border-slate-200 dark:border-white/10 bg-white/80 dark:bg-black/50 backdrop-blur-md z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 sm:gap-3 font-bold text-lg sm:text-xl group cursor-pointer selection:bg-transparent">
          <div className="relative w-8 sm:w-9 h-8 sm:h-9 flex items-center justify-center transition-transform duration-300 group-hover:scale-105">
            <div className="absolute inset-0 bg-gradient-to-tr from-indigo-500 via-purple-500 to-cyan-400 rounded-xl blur-md opacity-20 dark:opacity-50 group-hover:opacity-40 dark:group-hover:opacity-80 transition-opacity duration-300"></div>
            <div className="relative w-full h-full bg-gradient-to-tr from-indigo-600 to-cyan-500 rounded-xl flex items-center justify-center shadow-[inset_0_1px_1px_rgba(255,255,255,0.4)] border border-white/20">
              <Blocks size={18} className="sm:w-5 sm:h-5 text-white drop-shadow-md" />
            </div>
          </div>
          <span className="hidden sm:inline bg-clip-text text-transparent bg-gradient-to-r from-slate-900 via-indigo-600 to-slate-700 dark:from-white dark:via-indigo-100 dark:to-gray-300 tracking-tight font-sans">ContextBridge</span>
        </Link>
        <div className="flex items-center gap-3 sm:gap-6">
          {/* Theme Toggle */}
          <div 
            className="relative flex items-center bg-slate-200/50 dark:bg-white/5 rounded-full p-1 border border-slate-200 dark:border-white/10 transition-all duration-300 ease-in-out overflow-hidden cursor-pointer"
            onMouseEnter={() => setIsThemeOpen(true)}
            onMouseLeave={() => setIsThemeOpen(false)}
            onClick={() => !isThemeOpen && setIsThemeOpen(true)}
            style={{ width: isThemeOpen ? '108px' : '36px' }}
          >
            <div className="flex items-center gap-1">
              <button 
                onClick={(e) => { e.stopPropagation(); setTheme('light'); }}
                className={`p-1.5 rounded-full transition-all duration-200 ${theme === 'light' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-gray-400 dark:hover:text-white'} ${!isThemeOpen && theme !== 'light' ? 'opacity-0 invisible absolute' : 'opacity-100 visible relative'}`}
                title="Light Mode"
              >
                <Sun size={14} />
              </button>
              <button 
                onClick={(e) => { e.stopPropagation(); setTheme('dark'); }}
                className={`p-1.5 rounded-full transition-all duration-200 ${theme === 'dark' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-gray-400 dark:hover:text-white'} ${!isThemeOpen && theme !== 'dark' ? 'opacity-100 visible relative' : 'opacity-0 invisible absolute'}`}
                title="Dark Mode"
              >
                <Moon size={14} />
              </button>
              <button 
                onClick={(e) => { e.stopPropagation(); setTheme('system'); }}
                className={`p-1.5 rounded-full transition-all duration-200 ${theme === 'system' ? 'bg-slate-300/50 dark:bg-white/10 text-indigo-600 dark:text-white shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-gray-400 dark:hover:text-white'} ${!isThemeOpen && theme !== 'system' ? 'opacity-100 visible relative' : 'opacity-0 invisible absolute'}`}
                title="System Preference"
              >
                <Monitor size={14} />
              </button>
            </div>
          </div>
          <button 
            onClick={() => {
              if (location.pathname !== '/') {
                navigate('/');
                setTimeout(() => {
                  document.getElementById('docs-center')?.scrollIntoView({ behavior: 'smooth' });
                }, 100);
              } else {
                document.getElementById('docs-center')?.scrollIntoView({ behavior: 'smooth' });
              }
            }}
            className="text-slate-500 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white transition-colors flex items-center gap-1 sm:gap-2 text-xs sm:text-sm font-medium"
          >
            <FileText size={16} className="sm:w-[18px] sm:h-[18px]" />
            <span className="hidden sm:inline">Docs</span>
          </button>
          <a href="https://github.com/whyischen/ContextBridge" target="_blank" rel="noreferrer" className="text-slate-500 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white transition-colors flex items-center gap-1 sm:gap-2 text-xs sm:text-sm font-medium">
            <Github size={16} className="sm:w-[18px] sm:h-[18px]" />
            <span className="hidden sm:inline">GitHub</span>
          </a>
          <button 
            onClick={() => setLang(lang === 'en' ? 'zh' : 'en')}
            className="flex items-center gap-1 sm:gap-2 text-slate-500 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white transition-colors text-xs sm:text-sm font-medium"
          >
            <Languages size={16} className="sm:w-[18px] sm:h-[18px]" />
            <span className="hidden sm:inline">{lang === 'en' ? '中文' : 'English'}</span>
            <span className="sm:hidden">{lang === 'en' ? 'ZH' : 'EN'}</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
