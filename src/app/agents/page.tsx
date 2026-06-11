"use client";

import React, { useState } from "react";
import {
  Bot,
  Play,
  Search,
  Plus,
  Activity,
  Cpu,
  HardDrive,
  ChevronDown,
  ArrowUpRight,
  RefreshCw,
  Filter,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { StatCard, StatusBadge, SectionHeader } from "@/components/dashboard/shared";
import { mockAgents, AGENT_TYPES } from "@/lib/mock-data";

const agentTypeColors: Record<string, string> = {
  Browser: "cyan",
  Coder: "purple",
  Colony: "emerald",
  Executor: "amber",
  Manus: "cyan",
  Planner: "purple",
  Researcher: "emerald",
  Security: "rose",
  Voice: "purple",
  Registry: "amber",
};

const agentTypeIcons: Record<string, string> = {
  Browser: "🌐",
  Coder: "💻",
  Colony: "🏛️",
  Executor: "⚡",
  Manus: "🤖",
  Planner: "📋",
  Researcher: "🔍",
  Security: "🛡️",
  Voice: "🎤",
  Registry: "📦",
};

export default function AgentsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");
  const [runDialogOpen, setRunDialogOpen] = useState(false);
  const [selectedAgentType, setSelectedAgentType] = useState("");
  const [taskDescription, setTaskDescription] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  const filteredAgents = mockAgents.filter((agent) => {
    const matchesSearch =
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.type.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === "all" || agent.status === filterStatus;
    const matchesType = filterType === "all" || agent.type === filterType;
    return matchesSearch && matchesStatus && matchesType;
  });

  const activeCount = mockAgents.filter((a) => a.status === "active").length;
  const idleCount = mockAgents.filter((a) => a.status === "idle").length;
  const errorCount = mockAgents.filter((a) => a.status === "error").length;

  const handleRunAgent = async () => {
    setIsRunning(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsRunning(false);
    setRunDialogOpen(false);
    setSelectedAgentType("");
    setTaskDescription("");
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Bot className="w-6 h-6 text-purple" />
            Agent Management
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Deploy, monitor, and manage autonomous agents
          </p>
        </div>
        <Button variant="cyan" onClick={() => setRunDialogOpen(true)} className="gap-2">
          <Play className="w-4 h-4" />
          Run Agent
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Agents"
          value={mockAgents.length}
          subtitle="Deployed across colonies"
          icon={<Bot className="w-4 h-4" />}
          color="purple"
        />
        <StatCard
          title="Active"
          value={activeCount}
          subtitle="Currently processing tasks"
          icon={<Activity className="w-4 h-4" />}
          color="emerald"
        />
        <StatCard
          title="Idle"
          value={idleCount}
          subtitle="Awaiting task assignment"
          icon={<Cpu className="w-4 h-4" />}
          color="amber"
        />
        <StatCard
          title="Errors"
          value={errorCount}
          subtitle="Require attention"
          icon={<HardDrive className="w-4 h-4" />}
          color="rose"
        />
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-[140px]">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="idle">Idle</SelectItem>
            <SelectItem value="error">Error</SelectItem>
            <SelectItem value="offline">Offline</SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {AGENT_TYPES.map((type) => (
              <SelectItem key={type} value={type}>
                {type}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button variant="ghost" size="icon">
          <RefreshCw className="w-4 h-4" />
        </Button>
      </div>

      {/* Agent Cards */}
      <Tabs defaultValue="grid">
        <TabsList>
          <TabsTrigger value="grid">Grid View</TabsTrigger>
          <TabsTrigger value="list">List View</TabsTrigger>
        </TabsList>

        <TabsContent value="grid">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mt-4">
            {filteredAgents.map((agent) => {
              const colorName = agentTypeColors[agent.type] || "cyan";
              const borderColor = {
                cyan: "border-cyan/20 hover:border-cyan/40",
                purple: "border-purple/20 hover:border-purple/40",
                emerald: "border-emerald/20 hover:border-emerald/40",
                amber: "border-amber/20 hover:border-amber/40",
                rose: "border-rose/20 hover:border-rose/40",
              }[colorName] || "border-cyan/20 hover:border-cyan/40";

              return (
                <div key={agent.id} className={`glass-card p-4 ${borderColor} transition-all`}>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{agentTypeIcons[agent.type] || "🤖"}</span>
                      <div>
                        <h3 className="text-sm font-semibold text-foreground">{agent.name}</h3>
                        <p className="text-xs text-muted-foreground">{agent.type}</p>
                      </div>
                    </div>
                    <StatusBadge status={agent.status} />
                  </div>

                  <p className="text-xs text-muted-foreground mb-3 line-clamp-2">{agent.description}</p>

                  <div className="space-y-2">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-muted-foreground">CPU</span>
                        <span className="text-foreground">{agent.cpu}%</span>
                      </div>
                      <Progress value={agent.cpu} indicatorClassName={agent.cpu > 70 ? "bg-amber" : "bg-cyan"} />
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-muted-foreground">Memory</span>
                        <span className="text-foreground">{agent.memory}%</span>
                      </div>
                      <Progress value={agent.memory} indicatorClassName={agent.memory > 70 ? "bg-amber" : "bg-purple"} />
                    </div>
                  </div>

                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-border/50">
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span>{agent.tasksCompleted} done</span>
                      <span>{agent.tasksRunning} running</span>
                    </div>
                    <Badge variant={colorName as "cyan" | "purple" | "emerald" | "amber" | "rose"} className="text-[10px]">
                      {agent.colony}
                    </Badge>
                  </div>
                </div>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="list">
          <div className="mt-4 space-y-2">
            {filteredAgents.map((agent) => (
              <div
                key={agent.id}
                className="glass-card p-3 flex items-center gap-4 hover:border-primary/30 transition-all"
              >
                <span className="text-lg">{agentTypeIcons[agent.type] || "🤖"}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-foreground">{agent.name}</span>
                    <Badge variant="outline" className="text-[10px]">{agent.type}</Badge>
                    <StatusBadge status={agent.status} />
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5 truncate">{agent.description}</p>
                </div>
                <div className="hidden sm:flex items-center gap-6 text-xs text-muted-foreground">
                  <div className="text-center">
                    <div className="text-foreground font-medium">{agent.cpu}%</div>
                    <div>CPU</div>
                  </div>
                  <div className="text-center">
                    <div className="text-foreground font-medium">{agent.memory}%</div>
                    <div>MEM</div>
                  </div>
                  <div className="text-center">
                    <div className="text-foreground font-medium">{agent.tasksRunning}</div>
                    <div>Active</div>
                  </div>
                  <div className="text-center">
                    <div className="text-foreground font-medium">{agent.tasksCompleted}</div>
                    <div>Done</div>
                  </div>
                </div>
                <Badge variant="outline" className="text-[10px] hidden md:inline-flex">{agent.colony}</Badge>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Agent Type Overview */}
      <div>
        <SectionHeader title="Agent Types" description="Available agent types in the ecosystem" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mt-4">
          {AGENT_TYPES.map((type) => {
            const count = mockAgents.filter((a) => a.type === type).length;
            const colorName = agentTypeColors[type] || "cyan";
            return (
              <div
                key={type}
                className="glass-card p-3 text-center hover:border-primary/30 transition-all cursor-pointer"
              >
                <span className="text-2xl">{agentTypeIcons[type]}</span>
                <p className="text-sm font-medium text-foreground mt-1">{type}</p>
                <p className="text-xs text-muted-foreground">{count} deployed</p>
                <Badge
                  variant={colorName as "cyan" | "purple" | "emerald" | "amber" | "rose"}
                  className="mt-2 text-[10px]"
                >
                  {count > 0 ? "Active" : "Available"}
                </Badge>
              </div>
            );
          })}
        </div>
      </div>

      {/* Run Agent Dialog */}
      <Dialog open={runDialogOpen} onOpenChange={setRunDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Run Agent Task</DialogTitle>
            <DialogDescription>
              Select an agent type and describe the task you want it to execute.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">Agent Type</label>
              <Select value={selectedAgentType} onValueChange={setSelectedAgentType}>
                <SelectTrigger>
                  <SelectValue placeholder="Select agent type" />
                </SelectTrigger>
                <SelectContent>
                  {AGENT_TYPES.map((type) => (
                    <SelectItem key={type} value={type}>
                      {agentTypeIcons[type]} {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">Task Description</label>
              <Textarea
                placeholder="Describe the task for the agent to execute..."
                value={taskDescription}
                onChange={(e) => setTaskDescription(e.target.value)}
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setRunDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="cyan"
              onClick={handleRunAgent}
              disabled={!selectedAgentType || !taskDescription || isRunning}
            >
              {isRunning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Run Agent
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
