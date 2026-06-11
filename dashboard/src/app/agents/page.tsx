'use client';
import AppLayout from '@/components/layout/app-layout';
import { GlassCard } from '@/components/shared/cards';
import { mockAgents, statusColors } from '@/lib/mock-data';
import { useState } from 'react';

export default function AgentsPage() {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const filtered = mockAgents.filter(a => (filter === 'all' || a.status === filter) && a.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <AppLayout title="Agents">
      <div className="relative z-10 space-y-6">
        <div className="flex items-center gap-4">
          <input type="text" placeholder="Search agents..." value={search} onChange={e => setSearch(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white text-sm flex-1 max-w-md focus:outline-none focus:border-cyan-500/50" />
          <div className="flex gap-2">
            {['all', 'active', 'idle', 'error'].map(s => (
              <button key={s} onClick={() => setFilter(s)}
                className={`px-3 py-1 rounded-lg text-xs ${filter === s ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'bg-white/5 text-white/40 border border-white/10'}`}>
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(agent => (
            <GlassCard key={agent.id}>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${statusColors[agent.status]}`} />
                    <h3 className="text-white font-medium">{agent.name}</h3>
                  </div>
                  <span className="text-[10px] uppercase tracking-wider text-white/30 px-2 py-0.5 rounded-full bg-white/5">{agent.type}</span>
                </div>
                {agent.task && <p className="text-white/50 text-xs">{agent.task}</p>}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <div className="flex justify-between text-[10px] mb-1"><span className="text-white/30">CPU</span><span className="text-cyan-400">{agent.cpu}%</span></div>
                    <div className="h-1.5 rounded-full bg-white/5"><div className="h-full rounded-full bg-cyan-500" style={{ width: `${agent.cpu}%` }} /></div>
                  </div>
                  <div>
                    <div className="flex justify-between text-[10px] mb-1"><span className="text-white/30">Memory</span><span className="text-purple-400">{agent.memory}%</span></div>
                    <div className="h-1.5 rounded-full bg-white/5"><div className="h-full rounded-full bg-purple-500" style={{ width: `${agent.memory}%` }} /></div>
                  </div>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                  <span className="text-white/30 text-[10px]">Last: {agent.lastAction}</span>
                  <button className="text-[10px] px-2 py-1 rounded bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 transition">Run Task</button>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
