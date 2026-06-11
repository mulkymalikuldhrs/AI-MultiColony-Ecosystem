import React from 'react';
import Sidebar from '@/components/layout/sidebar';

export default function AppLayout({ children, title }: { children: React.ReactNode; title: string }) {
  return (
    <div className="min-h-screen bg-[#050510] text-white">
      <Sidebar />
      <div className="ml-56">
        <header className="sticky top-0 z-40 h-14 bg-[#0a0a1a]/80 backdrop-blur-xl border-b border-white/5 flex items-center justify-between px-6">
          <h1 className="text-white font-semibold text-lg">{title}</h1>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20">
              <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse" />
              <span className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider">Colony Active</span>
            </div>
            <div className="text-white/40 text-sm">{new Date().toLocaleTimeString()}</div>
          </div>
        </header>
        <main className="p-6">{children}</main>
      </div>
      {/* Grid background */}
      <div className="fixed inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none z-0" />
    </div>
  );
}
