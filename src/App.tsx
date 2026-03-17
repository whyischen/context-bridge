import React, { useState, useEffect, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import LandingPage from './pages/Landing';
import DocsPage from './pages/Docs';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import { APP_CONTENT } from './constants/content';

export default function App() {
  const getInitialLang = (): 'en' | 'zh' => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('cbridge-lang');
      if (saved === 'en' || saved === 'zh') return saved;
    }
    return 'en'; // Default to English
  };

  const [lang, setLang] = useState<'en' | 'zh'>(getInitialLang());
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('cbridge-theme');
      return (saved as 'light' | 'dark' | 'system') || 'dark'; // Default to dark mode
    }
    return 'dark';
  });
  const [isThemeOpen, setIsThemeOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  
  useEffect(() => {
    const root = window.document.documentElement;
    localStorage.setItem('cbridge-theme', theme);
    
    const applyTheme = () => {
      let actualTheme = theme;
      if (theme === 'system') {
        actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      
      root.classList.remove('light', 'dark');
      root.classList.add(actualTheme);
      root.style.colorScheme = actualTheme;
      root.style.backgroundColor = actualTheme === 'dark' ? '#1c1e21' : '#f8fafc';
    };

    applyTheme();

    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener('change', applyTheme);
      return () => mediaQuery.removeEventListener('change', applyTheme);
    }
  }, [theme]);

  const copyInstallCmd = useCallback(() => {
    navigator.clipboard.writeText('pip install cbridge-agent');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, []);

  const t = APP_CONTENT[lang];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#1c1e21] text-slate-900 dark:text-white font-sans selection:bg-indigo-500/30 transition-colors duration-300">
      <Navbar 
        lang={lang} 
        setLang={setLang} 
        theme={theme} 
        setTheme={setTheme} 
        isThemeOpen={isThemeOpen} 
        setIsThemeOpen={setIsThemeOpen} 
      />

      <Routes>
        <Route path="/" element={<LandingPage lang={lang} t={t} copied={copied} copyInstallCmd={copyInstallCmd} />} />
        <Route path="/docs/:docType" element={<DocsPage lang={lang} />} />
      </Routes>

      <Footer />
    </div>
  );
}
