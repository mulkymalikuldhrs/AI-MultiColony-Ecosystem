'use client';
import AppLayout from '@/components/layout/app-layout';
import { GlassCard } from '@/components/shared/cards';
import { useState } from 'react';

export default function SettingsPage() {
  const [featureToggles, setFeatureToggles] = useState({
    websocket: true, eventBus: true, audit: true, autoRestart: false,
  });

  return (
    <AppLayout title="Settings">
      <div className="relative z-10 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* System Configuration */}
          <GlassCard title="System Configuration">
            <div className="space-y-4">
              {[
                { label: 'Max Agents', value: '20', type: 'number' },
                { label: 'Task Timeout (s)', value: '300', type: 'number' },
                { label: 'Memory Limit (MB)', value: '4096', type: 'number' },
                { label: 'Log Level', value: 'INFO', type: 'select', options: ['DEBUG', 'INFO', 'WARNING', 'ERROR'] },
                { label: 'Scheduling Algorithm', value: 'round-robin', type: 'select', options: ['round-robin', 'priority-based', 'fifo'] },
              ].map(field => (
                <div key={field.label} className="flex items-center justify-between">
                  <label className="text-white/60 text-sm">{field.label}</label>
                  {field.type === 'select' ? (
                    <select className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none">
                      {field.options?.map(o => <option key={o} value={o}>{o}</option>)}
                    </select>
                  ) : (
                    <input type="number" defaultValue={field.value}
                      className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white text-sm w-24 text-right focus:outline-none focus:border-cyan-500/50" />
                  )}
                </div>
              ))}
            </div>
          </GlassCard>

          {/* Feature Toggles */}
          <GlassCard title="Feature Toggles">
            <div className="space-y-4">
              {Object.entries(featureToggles).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-white/60 text-sm">{key.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase())}</span>
                  <button onClick={() => setFeatureToggles(prev => ({ ...prev, [key]: !value }))}
                    className={`w-10 h-5 rounded-full transition-all ${value ? 'bg-cyan-500' : 'bg-white/10'}`}>
                    <div className={`w-4 h-4 rounded-full bg-white transition-transform ${value ? 'translate-x-5' : 'translate-x-0.5'}`} />
                  </button>
                </div>
              ))}
            </div>
          </GlassCard>

          {/* LLM Providers */}
          <GlassCard title="LLM Providers">
            <div className="space-y-3">
              {[
                { name: 'OpenAI', model: 'gpt-4o', color: 'emerald', configured: true },
                { name: 'Anthropic', model: 'claude-3-opus', color: 'purple', configured: true },
                { name: 'Google', model: 'gemini-2.0-flash', color: 'cyan', configured: true },
                { name: 'Local (Ollama)', model: 'llama3', color: 'amber', configured: false },
              ].map(provider => (
                <div key={provider.name} className="p-3 rounded-lg bg-white/[0.02] border border-white/5">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${provider.configured ? 'bg-emerald-500' : 'bg-gray-500'}`} />
                      <span className="text-white/70 text-sm font-medium">{provider.name}</span>
                    </div>
                    <span className="text-white/30 text-[10px] font-mono">{provider.model}</span>
                  </div>
                  <input type="password" placeholder={`${provider.name} API Key`}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white text-xs focus:outline-none focus:border-cyan-500/50" />
                </div>
              ))}
            </div>
          </GlassCard>

          {/* MCP Configuration */}
          <GlassCard title="MCP Servers">
            <div className="space-y-3">
              {[
                { name: 'filesystem', transport: 'stdio', command: 'npx @anthropic/mcp-filesystem' },
                { name: 'github', transport: 'stdio', command: 'npx @anthropic/mcp-github' },
                { name: 'brave-search', transport: 'stdio', command: 'npx @anthropic/mcp-brave-search' },
              ].map(server => (
                <div key={server.name} className="p-3 rounded-lg bg-white/[0.02] border border-white/5">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-white/70 text-sm font-medium">{server.name}</span>
                    <span className="text-white/30 text-[10px] px-2 py-0.5 rounded bg-white/5">{server.transport}</span>
                  </div>
                  <div className="text-white/30 text-xs font-mono">{server.command}</div>
                </div>
              ))}
              <button className="w-full py-2 rounded-lg bg-white/5 border border-white/10 text-white/40 text-sm hover:bg-white/10 transition">
                + Add MCP Server
              </button>
            </div>
          </GlassCard>
        </div>

        <div className="flex justify-end gap-3">
          <button className="px-6 py-2 rounded-lg bg-white/5 border border-white/10 text-white/50 text-sm">Reset</button>
          <button className="px-6 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white text-sm font-medium hover:opacity-90 transition">Save Changes</button>
        </div>
      </div>
    </AppLayout>
  );
}
