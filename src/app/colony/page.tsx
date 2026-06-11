"use client";

import React, { useState } from "react";
import {
  Network,
  Plus,
  Activity,
  Users,
  Clock,
  Zap,
  RefreshCw,
  ArrowRight,
  Layers,
  GitBranch,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { StatCard, StatusBadge, SectionHeader } from "@/components/dashboard/shared";
import { mockColonies, mockAgents, colonyHealthHistory, AGENT_TYPES } from "@/lib/mock-data";

// Colony grid visualization
const colonyGridCells = [
  { id: 1, type: "coordinator", label: "Coordinator", status: "active" },
  { id: 2, type: "agent", label: "Browser-α", status: "active" },
  { id: 3, type: "agent", label: "Coder-β", status: "active" },
  { id: 4, type: "agent", label: "Planner-ε", status: "active" },
  { id: 5, type: "channel", label: "Event Bus", status: "active" },
  { id: 6, type: "agent", label: "Security-η", status: "active" },
  { id: 7, type: "agent", label: "Manus-δ", status: "active" },
  { id: 8, type: "memory", label: "Shared Memory", status: "active" },
  { id: 9, type: "agent", label: "Registry-ι", status: "active" },
  { id: 10, type: "tool", label: "Tool Registry", status: "active" },
  { id: 11, type: "agent", label: "Colony-μ", status: "idle" },
  { id: 12, type: "channel", label: "MCP Hub", status: "active" },
];

const cellTypeColors: Record<string, string> = {
  coordinator: "border-cyan/40 bg-cyan/10",
  agent: "border-purple/30 bg-purple/5",
  channel: "border-emerald/30 bg-emerald/5",
  memory: "border-amber/30 bg-amber/5",
  tool: "border-rose/30 bg-rose/5",
};

export default function ColonyPage() {
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newColonyName, setNewColonyName] = useState("");
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [isCreating, setIsCreating] = useState(false);

  const totalAgents = mockColonies.reduce((acc, c) => acc + c.agents, 0);
  const avgHealth = Math.round(mockColonies.reduce((acc, c) => acc + c.health, 0) / mockColonies.length);

  const handleCreateColony = async () => {
    setIsCreating(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsCreating(false);
    setCreateDialogOpen(false);
    setNewColonyName("");
    setSelectedAgents([]);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Network className="w-6 h-6 text-emerald" />
            Colony Network
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Visualize and manage agent colonies
          </p>
        </div>
        <Button variant="emerald" onClick={() => setCreateDialogOpen(true)} className="gap-2">
          <Plus className="w-4 h-4" />
          Create Colony
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Colonies"
          value={mockColonies.length}
          subtitle={`${mockColonies.filter((c) => c.status === "active").length} active`}
          icon={<Network className="w-4 h-4" />}
          color="emerald"
        />
        <StatCard
          title="Total Agents"
          value={totalAgents}
          subtitle="Across all colonies"
          icon={<Users className="w-4 h-4" />}
          color="cyan"
        />
        <StatCard
          title="Avg Health"
          value={`${avgHealth}%`}
          subtitle="System-wide health"
          icon={<Activity className="w-4 h-4" />}
          color="purple"
        />
        <StatCard
          title="Schedulers"
          value={mockColonies.length}
          subtitle="Active coordinators"
          icon={<Clock className="w-4 h-4" />}
          color="amber"
        />
      </div>

      <Tabs defaultValue="grid">
        <TabsList>
          <TabsTrigger value="grid">Colony Grid</TabsTrigger>
          <TabsTrigger value="health">Health Monitor</TabsTrigger>
          <TabsTrigger value="scheduling">Scheduling</TabsTrigger>
        </TabsList>

        {/* Colony Grid Visualization */}
        <TabsContent value="grid">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
            {/* Interactive Grid */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan" />
                  Colony-Alpha — Network Topology
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-2">
                  {colonyGridCells.map((cell) => (
                    <div
                      key={cell.id}
                      className={`aspect-square rounded-lg border p-2 flex flex-col items-center justify-center text-center transition-all hover:scale-105 cursor-pointer ${cellTypeColors[cell.type]}`}
                    >
                      <div className="flex items-center gap-1 mb-1">
                        <span className={`status-dot ${cell.status === "active" ? "status-dot-active" : "status-dot-idle"}`} />
                      </div>
                      <span className="text-[10px] font-medium text-foreground leading-tight">{cell.label}</span>
                      <span className="text-[9px] text-muted-foreground capitalize">{cell.type}</span>
                    </div>
                  ))}
                </div>
                <div className="flex items-center gap-4 mt-4 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded border border-cyan/40 bg-cyan/10" />
                    Coordinator
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded border border-purple/30 bg-purple/5" />
                    Agent
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded border border-emerald/30 bg-emerald/5" />
                    Channel
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded border border-amber/30 bg-amber/5" />
                    Memory
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded border border-rose/30 bg-rose/5" />
                    Tool
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Colony Details List */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <Network className="w-4 h-4 text-emerald" />
                  All Colonies
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {mockColonies.map((colony) => (
                  <div
                    key={colony.id}
                    className="p-4 rounded-lg bg-secondary/20 border border-border/50 hover:border-primary/30 transition-all"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-emerald/10 border border-emerald/20 flex items-center justify-center">
                          <Network className="w-4 h-4 text-emerald" />
                        </div>
                        <div>
                          <h3 className="text-sm font-semibold text-foreground">{colony.name}</h3>
                          <p className="text-xs text-muted-foreground">Coordinator: {colony.coordinator}</p>
                        </div>
                      </div>
                      <StatusBadge status={colony.status} />
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs mb-3">
                      <div className="p-2 rounded bg-secondary/30">
                        <span className="text-muted-foreground">Agents</span>
                        <p className="text-foreground font-medium">{colony.agents} / {colony.maxAgents}</p>
                      </div>
                      <div className="p-2 rounded bg-secondary/30">
                        <span className="text-muted-foreground">Uptime</span>
                        <p className="text-foreground font-medium">{colony.uptime}</p>
                      </div>
                      <div className="p-2 rounded bg-secondary/30">
                        <span className="text-muted-foreground">Schedule</span>
                        <p className="text-foreground font-medium">{colony.schedule}</p>
                      </div>
                      <div className="p-2 rounded bg-secondary/30">
                        <span className="text-muted-foreground">Health</span>
                        <p className="text-foreground font-medium">{colony.health}%</p>
                      </div>
                    </div>

                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-muted-foreground">Health</span>
                        <span className={colony.health > 90 ? "text-emerald" : colony.health > 70 ? "text-amber" : "text-rose"}>
                          {colony.health}%
                        </span>
                      </div>
                      <Progress
                        value={colony.health}
                        indicatorClassName={
                          colony.health > 90 ? "bg-emerald" : colony.health > 70 ? "bg-amber" : "bg-rose"
                        }
                      />
                    </div>

                    <div className="flex items-center gap-1 mt-3">
                      <div className="flex-1">
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-muted-foreground">Capacity</span>
                          <span className="text-foreground">{Math.round((colony.agents / colony.maxAgents) * 100)}%</span>
                        </div>
                        <Progress value={(colony.agents / colony.maxAgents) * 100} />
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Health Monitor */}
        <TabsContent value="health">
          <div className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <Activity className="w-4 h-4 text-emerald" />
                  Colony Health Over Time
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={colonyHealthHistory}>
                      <defs>
                        <linearGradient id="alphaGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="betaGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="gammaGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                      </defs>
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
                      <Area type="monotone" dataKey="alpha" stroke="#06b6d4" fill="url(#alphaGrad)" strokeWidth={2} name="Alpha" />
                      <Area type="monotone" dataKey="beta" stroke="#8b5cf6" fill="url(#betaGrad)" strokeWidth={2} name="Beta" />
                      <Area type="monotone" dataKey="gamma" stroke="#10b981" fill="url(#gammaGrad)" strokeWidth={2} name="Gamma" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex items-center gap-6 mt-4">
                  <div className="flex items-center gap-2 text-xs"><span className="w-3 h-0.5 bg-cyan rounded" /> Colony-Alpha</div>
                  <div className="flex items-center gap-2 text-xs"><span className="w-3 h-0.5 bg-purple rounded" /> Colony-Beta</div>
                  <div className="flex items-center gap-2 text-xs"><span className="w-3 h-0.5 bg-emerald rounded" /> Colony-Gamma</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Scheduling */}
        <TabsContent value="scheduling">
          <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-6">
            {mockColonies.map((colony) => (
              <Card key={colony.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                      <GitBranch className="w-4 h-4 text-amber" />
                      {colony.name} — Scheduling
                    </span>
                    <Badge variant="outline">{colony.schedule}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-3 rounded-lg bg-secondary/20 border border-border/30">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-muted-foreground">Scheduling Algorithm</span>
                        <Badge variant="amber">{colony.schedule}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {colony.schedule === "Round-Robin"
                          ? "Tasks are distributed evenly across agents in rotation order."
                          : colony.schedule === "Priority-Based"
                          ? "Tasks are assigned based on priority levels and agent capabilities."
                          : "Tasks are assigned only when agents request them."}
                      </p>
                    </div>

                    <div className="p-3 rounded-lg bg-secondary/20 border border-border/30">
                      <span className="text-xs text-muted-foreground mb-2 block">Active Schedule</span>
                      <div className="flex items-center gap-2 flex-wrap">
                        {mockAgents
                          .filter((a) => a.colony === colony.name)
                          .map((agent) => (
                            <div
                              key={agent.id}
                              className="flex items-center gap-1 px-2 py-1 rounded bg-secondary/40 border border-border/30 text-xs"
                            >
                              <span className={`status-dot ${agent.status === "active" ? "status-dot-active" : "status-dot-idle"}`} />
                              <span className="text-foreground">{agent.name}</span>
                            </div>
                          ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div className="p-2 rounded bg-secondary/20">
                        <p className="text-lg font-bold text-foreground">{colony.agents}</p>
                        <p className="text-[10px] text-muted-foreground">Agents</p>
                      </div>
                      <div className="p-2 rounded bg-secondary/20">
                        <p className="text-lg font-bold text-foreground">{colony.health}%</p>
                        <p className="text-[10px] text-muted-foreground">Health</p>
                      </div>
                      <div className="p-2 rounded bg-secondary/20">
                        <p className="text-lg font-bold text-foreground">{colony.maxAgents - colony.agents}</p>
                        <p className="text-[10px] text-muted-foreground">Available</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Create Colony Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Colony</DialogTitle>
            <DialogDescription>
              Set up a new agent colony with a coordinator and initial agents.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">Colony Name</label>
              <Input
                placeholder="e.g., Colony-Delta"
                value={newColonyName}
                onChange={(e) => setNewColonyName(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">Initial Agents</label>
              <div className="grid grid-cols-2 gap-2">
                {AGENT_TYPES.map((type) => (
                  <label
                    key={type}
                    className={`flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition-all ${
                      selectedAgents.includes(type)
                        ? "border-primary/40 bg-primary/10"
                        : "border-border/50 bg-secondary/20 hover:border-primary/20"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedAgents.includes(type)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedAgents([...selectedAgents, type]);
                        } else {
                          setSelectedAgents(selectedAgents.filter((a) => a !== type));
                        }
                      }}
                      className="accent-primary"
                    />
                    <span className="text-xs text-foreground">{type}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
            <Button
              variant="emerald"
              onClick={handleCreateColony}
              disabled={!newColonyName || selectedAgents.length === 0 || isCreating}
            >
              {isCreating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Create Colony
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
