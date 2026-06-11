import React from 'react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: '◉', href: '/' },
  { id: 'agents', label: 'Agents', icon: '⬡', href: '/agents' },
  { id: 'colony', label: 'Colony', icon: '⬢', href: '/colony' },
  { id: 'tools', label: 'Tools', icon: '⚙', href: '/tools' },
  { id: 'memory', label: 'Memory', icon: '◈', href: '/memory' },
  { id: 'channels', label: 'Channels', icon: '◈', href: '/channels' },
  { id: 'security', label: 'Security', icon: '⬟', href: '/security' },
  { id: 'settings', label: 'Settings', icon: '⚙', href: '/settings' },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-56 bg-[#0a0a1a]/90 backdrop-blur-xl border-r border-white/5 flex flex-col z-50">
      <div className="p-4 border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">M</div>
          <div>
            <div className="text-white font-bold text-sm">MultiColony</div>
            <div className="text-[10px] text-cyan-400/70">Agent OS v2.0</div>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-2 space-y-0.5">
        {navItems.map(item => (
          <a key={item.id} href={item.href}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-white/60 hover:text-white hover:bg-white/5 transition-all">
            <span className="text-base">{item.icon}</span>
            <span>{item.label}</span>
          </a>
        ))}
      </nav>
      <div className="p-4 border-t border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs text-white/40">System Online</span>
        </div>
      </div>
    </aside>
  );
}
