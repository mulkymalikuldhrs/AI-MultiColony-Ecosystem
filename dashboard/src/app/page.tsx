'use client';
import AppLayout from '@/components/layout/app-layout';
import { StatusCard, GlassCard } from '@/components/shared/cards';
import { mockAgents, mockColonies, mockEvents, statusColors } from '@/lib/mock-data';

export default function DashboardPage() {
  const activeAgents = mockAgents.filter(a => a.status === 'active').length;
  const healthyColonies = mockColonies.filter(c => c.status === 'active').length;
  const totalCpu = Math.round(mockAgents.reduce((s, a) => s + a.cpu, 0) / mockAgents.length);
  const totalMemory = Math.round(mockAgents.reduce((s, a) => s + a.memory, 0) / mockAgents.length);

  return (
    <AppLayout title="Dashboard">
      <div className="relative z-10 space-y-6">
        {/* Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <StatusCard title="Active Agents" value={activeAgents} subtitle={`of ${mockAgents.length} total`} color="cyan" />
          <StatusCard title="Colonies" value={healthyColonies} subtitle={`${mockColonies.length} total`} color="purple" />
          <StatusCard title="Avg CPU" value={`${totalCpu}%`} subtitle="Across all agents" color="emerald" />
          <StatusCard title="Avg Memory" value={`${totalMemory}%`} subtitle="Utilization" color="amber" />
          <StatusCard title="Events/s" value="24.5" subtitle="Event throughput" color="cyan" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Colony Status */}
          <GlassCard title="Colony Status" className="col-span-2">
            <div className="space-y-3">
              {mockColonies.map(colony => (
                <div key={colony.id} className="flex items-center justify-between p-3 rounded-lg bg-white/[0.02] border border-white/5">
                  <div className="flex items-center gap-3">
                    <div className={`w-2.5 h-2.5 rounded-full ${statusColors[colony.status]}`} />
                    <div>
                      <div className="text-white text-sm font-medium">{colony.name}</div>
                      <div className="text-white/30 text-xs">{colony.agents} agents · {colony.schedule}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-32">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-white/40">Health</span>
                        <span className="text-white/60">{colony.health}%</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-white/5">
                        <div className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-purple-500" style={{ width: `${colony.health}%` }} />
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-white/60 text-xs">{colony.capacity - colony.agents} slots</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>

          {/* Live Event Feed */}
          <GlassCard title="Event Feed">
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {mockEvents.map(event => (
                <div key={event.id} className="flex items-start gap-2 p-2 rounded bg-white/[0.02]">
                  <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${
                    event.severity === 'error' ? 'bg-red-500' :
                    event.severity === 'warning' ? 'bg-amber-500' :
                    event.severity === 'success' ? 'bg-emerald-500' : 'bg-cyan-500'
                  }`} />
                  <div>
                    <div className="text-white/70 text-xs">{event.message}</div>
                    <div className="text-white/30 text-[10px]">{event.timestamp}</div>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>

        {/* Agent Overview */}
        <GlassCard title="Agent Overview">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {mockAgents.map(agent => (
              <div key={agent.id} className="p-3 rounded-lg bg-white/[0.02] border border-white/5">
                <div className="flex items-center gap-2 mb-2">
                  <div className={`w-2 h-2 rounded-full ${statusColors[agent.status]}`} />
                  <span className="text-white/70 text-xs font-medium truncate">{agent.name}</span>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-[10px]">
                    <span className="text-white/30">CPU</span>
                    <span className="text-white/50">{agent.cpu}%</span>
                  </div>
                  <div className="h-1 rounded-full bg-white/5">
                    <div className="h-full rounded-full bg-cyan-500/60" style={{ width: `${agent.cpu}%` }} />
                  </div>
                  <div className="flex justify-between text-[10px]">
                    <span className="text-white/30">MEM</span>
                    <span className="text-white/50">{agent.memory}%</span>
                  </div>
                  <div className="h-1 rounded-full bg-white/5">
                    <div className="h-full rounded-full bg-purple-500/60" style={{ width: `${agent.memory}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </AppLayout>
  );
}
