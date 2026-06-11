"use client";

import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
} from "recharts";
import {
  Bot,
  Network,
  Activity,
  Cpu,
  HardDrive,
  Zap,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowUpRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { StatCard, StatusBadge, SectionHeader } from "@/components/dashboard/shared";
import {
  mockAgents,
  mockColonies,
  mockSystemEvents,
  resourceUsageHistory,
  colonyHealthHistory,
  toolExecutionHistory,
} from "@/lib/mock-data";

const severityIcon: Record<string, React.ReactNode> = {
  success: <CheckCircle2 className="w-3.5 h-3.5 text-emerald" />,
  info: <Activity className="w-3.5 h-3.5 text-cyan" />,
  warning: <AlertTriangle className="w-3.5 h-3.5 text-amber" />,
  error: <AlertTriangle className="w-3.5 h-3.5 text-rose" />,
};

const severityColor: Record<string, string> = {
  success: "border-l-emerald",
  info: "border-l-cyan",
  warning: "border-l-amber",
  error: "border-l-rose",
};

export default function DashboardPage() {
  const activeAgents = mockAgents.filter((a) => a.status === "active").length;
  const totalTasks = mockAgents.reduce((acc, a) => acc + a.tasksRunning, 0);
  const totalCompleted = mockAgents.reduce((acc, a) => acc + a.tasksCompleted, 0);
  const avgCpu = Math.round(mockAgents.reduce((acc, a) => acc + a.cpu, 0) / mockAgents.length);
  const avgMemory = Math.round(mockAgents.reduce((acc, a) => acc + a.memory, 0) / mockAgents.length);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Zap className="w-6 h-6 text-cyan" />
            Mission Control
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            AI MultiColony Ecosystem — System Overview
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="emerald" className="gap-1">
            <span className="status-dot status-dot-active" />
            System Online
          </Badge>
          <Badge variant="outline" className="text-muted-foreground">
            <Clock className="w-3 h-3 mr-1" />
            {new Date().toLocaleTimeString()}
          </Badge>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          title="Active Colonies"
          value={mockColonies.length}
          subtitle={`${mockColonies.filter((c) => c.status === "active").length} running`}
          icon={<Network className="w-4 h-4" />}
          color="cyan"
          trend={{ value: 12, positive: true }}
        />
        <StatCard
          title="Active Agents"
          value={activeAgents}
          subtitle={`of ${mockAgents.length} total`}
          icon={<Bot className="w-4 h-4" />}
          color="purple"
          trend={{ value: 5, positive: true }}
        />
        <StatCard
          title="Running Tasks"
          value={totalTasks}
          subtitle={`${totalCompleted} completed`}
          icon={<Activity className="w-4 h-4" />}
          color="emerald"
          trend={{ value: 8, positive: true }}
        />
        <StatCard
          title="Avg CPU Usage"
          value={`${avgCpu}%`}
          subtitle="Across all agents"
          icon={<Cpu className="w-4 h-4" />}
          color="amber"
          trend={{ value: 3, positive: false }}
        />
        <StatCard
          title="Avg Memory"
          value={`${avgMemory}%`}
          subtitle={`${(avgMemory * 3.2).toFixed(0)}MB / 512MB`}
          icon={<HardDrive className="w-4 h-4" />}
          color="rose"
          trend={{ value: 2, positive: false }}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Resource Usage Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan" />
              Resource Usage Over Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={resourceUsageHistory}>
                  <defs>
                    <linearGradient id="cpuGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="memGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      background: "#111827",
                      border: "1px solid #1e293b",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                  <Area type="monotone" dataKey="cpu" stroke="#06b6d4" fill="url(#cpuGrad)" strokeWidth={2} />
                  <Area type="monotone" dataKey="memory" stroke="#8b5cf6" fill="url(#memGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Colony Health Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
              <Network className="w-4 h-4 text-emerald" />
              Colony Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={colonyHealthHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{
                      background: "#111827",
                      border: "1px solid #1e293b",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                  <Line type="monotone" dataKey="alpha" stroke="#06b6d4" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="beta" stroke="#8b5cf6" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="gamma" stroke="#10b981" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tool Executions + Colony Status + Event Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tool Executions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-amber" />
              Tool Executions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={toolExecutionHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      background: "#111827",
                      border: "1px solid #1e293b",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="executions" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="errors" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Colony Status Cards */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
              <Network className="w-4 h-4 text-cyan" />
              Colony Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {mockColonies.map((colony) => (
              <div
                key={colony.id}
                className="p-3 rounded-lg bg-secondary/30 border border-border/50 hover:border-primary/20 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-foreground">{colony.name}</span>
                    <StatusBadge status={colony.status} />
                  </div>
                  <span className="text-xs text-muted-foreground">{colony.uptime}</span>
                </div>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span>Agents: {colony.agents}/{colony.maxAgents}</span>
                  <span>Health: {colony.health}%</span>
                </div>
                <div className="mt-2">
                  <div className="h-1.5 rounded-full bg-secondary">
                    <div
                      className="h-full rounded-full bg-cyan transition-all"
                      style={{ width: `${colony.health}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Live Event Feed */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald" />
              Live Event Feed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-72">
              <div className="space-y-1">
                {mockSystemEvents.map((event) => (
                  <div
                    key={event.id}
                    className={`flex items-start gap-2 p-2 rounded-md hover:bg-secondary/30 transition-colors border-l-2 ${severityColor[event.severity]}`}
                  >
                    <span className="mt-0.5 shrink-0">{severityIcon[event.severity]}</span>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs text-foreground leading-relaxed">{event.message}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                          {event.type}
                        </Badge>
                        <span className="text-[10px] text-muted-foreground">{event.timestamp}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Agent Overview Row */}
      <div>
        <SectionHeader
          title="Agent Overview"
          description="Current status of all deployed agents"
          action={
            <a href="/agents" className="text-xs text-primary hover:text-primary/80 flex items-center gap-1">
              View All <ArrowUpRight className="w-3 h-3" />
            </a>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mt-4">
          {mockAgents.slice(0, 5).map((agent) => (
            <div
              key={agent.id}
              className="glass-card p-3 hover:border-primary/30 transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-foreground">{agent.name}</span>
                <StatusBadge status={agent.status} />
              </div>
              <div className="text-xs text-muted-foreground space-y-1">
                <div className="flex justify-between">
                  <span>Type</span>
                  <span className="text-foreground">{agent.type}</span>
                </div>
                <div className="flex justify-between">
                  <span>CPU</span>
                  <span className="text-foreground">{agent.cpu}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Tasks</span>
                  <span className="text-foreground">{agent.tasksRunning} running</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
