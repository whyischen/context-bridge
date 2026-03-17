import React from 'react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 dark:border-white/10 py-8 sm:py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col md:flex-row items-center justify-between text-slate-500 dark:text-gray-500 text-xs sm:text-sm gap-4">
        <p>© {new Date().getFullYear()} ContextBridge. Open source under MIT License.</p>
        <div className="flex items-center gap-4">
          <a href="https://github.com/whyischen/ContextBridge" className="hover:text-indigo-600 dark:hover:text-white transition-colors">GitHub</a>
        </div>
      </div>
    </footer>
  );
}
