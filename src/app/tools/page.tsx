"use client";

import React, { useState } from "react";
import {
  Wrench,
  Play,
  Search,
  RefreshCw,
  Terminal,
  Code,
  Globe,
  HardDrive,
  FileText,
  MessageSquare,
  Database,
  Search as SearchIcon,
  TerminalSquare,
  Mic,
  Settings,
  Container,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
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
import { ScrollArea } from "@/components/ui/scroll-area";
import { StatCard, StatusBadge, SectionHeader } from "@/components/dashboard/shared";
import { mockTools, TOOL_CATEGORIES, toolExecutionHistory } from "@/lib/mock-data";

const toolIcons: Record<string, React.ReactNode> = {
  browser: <Globe className="w-4 h-4" />,
  channel: <MessageSquare className="w-4 h-4" />,
  code: <Code className="w-4 h-4" />,
  docker: <Container className="w-4 h-4" />,
  file: <FileText className="w-4 h-4" />,
  mcp: <Settings className="w-4 h-4" />,
  memory: <Database className="w-4 h-4" />,
  search: <SearchIcon className="w-4 h-4" />,
  shell: <TerminalSquare className="w-4 h-4" />,
  voice: <Mic className="w-4 h-4" />,
  registry: <Wrench className="w-4 h-4" />,
};

const categoryColors: Record<string, string> = {
  browser: "cyan",
  channel: "emerald",
  code: "purple",
  docker: "amber",
  file: "cyan",
  mcp: "purple",
  memory: "emerald",
  search: "amber",
  shell: "rose",
  voice: "purple",
  registry: "cyan",
};

export default function ToolsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [executeDialogOpen, setExecuteDialogOpen] = useState(false);
  const [selectedTool, setSelectedTool] = useState<string>("");
  const [toolParams, setToolParams] = useState("");
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<string | null>(null);

  const filteredTools = mockTools.filter((tool) => {
    const matchesSearch = tool.name.toLowerCase().includes(searchQuery.toLowerCase()) || tool.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = filterCategory === "all" || tool.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const handleExecute = async () => {
    setIsExecuting(true);
    setExecutionResult(null);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setExecutionResult(`{
  "status": "success",
  "tool": "${selectedTool}",
  "result": "Operation completed successfully",
  "execution_time": "1.23s",
  "timestamp": "${new Date().toISOString()}"
}`);
    setIsExecuting(false);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Wrench className="w-6 h-6 text-amber" />
            Tool Registry
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Browse, execute, and monitor system tools
          </p>
        </div>
        <Button variant="amber" onClick={() => { setSelectedTool(""); setExecuteDialogOpen(true); }} className="gap-2">
          <Play className="w-4 h-4" />
          Execute Tool
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Tools"
          value={mockTools.length}
          subtitle="Registered in ecosystem"
          icon={<Wrench className="w-4 h-4" />}
          color="amber"
        />
        <StatCard
          title="Available"
          value={mockTools.filter((t) => t.status === "available").length}
          subtitle="Ready to use"
          icon={<Play className="w-4 h-4" />}
          color="emerald"
        />
        <StatCard
          title="Total Executions"
          value={mockTools.reduce((acc, t) => acc + t.executions, 0).toLocaleString()}
          subtitle="All time"
          icon={<Terminal className="w-4 h-4" />}
          color="cyan"
        />
        <StatCard
          title="Avg Latency"
          value={`${Math.round(mockTools.reduce((acc, t) => acc + t.avgLatency, 0) / mockTools.length)}ms`}
          subtitle="Across all tools"
          icon={<RefreshCw className="w-4 h-4" />}
          color="purple"
        />
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search tools..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={filterCategory} onValueChange={setFilterCategory}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {TOOL_CATEGORIES.map((cat) => (
              <SelectItem key={cat} value={cat} className="capitalize">
                {cat}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Tabs defaultValue="grid">
        <TabsList>
          <TabsTrigger value="grid">Tool Cards</TabsTrigger>
          <TabsTrigger value="executions">Execution History</TabsTrigger>
        </TabsList>

        {/* Tool Cards */}
        <TabsContent value="grid">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mt-4">
            {filteredTools.map((tool) => {
              const colorName = categoryColors[tool.category] || "cyan";
              return (
                <div
                  key={tool.id}
                  className="glass-card p-4 hover:border-primary/30 transition-all cursor-pointer"
                  onClick={() => {
                    setSelectedTool(tool.name);
                    setExecuteDialogOpen(true);
                  }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className={`p-1.5 rounded-lg bg-${colorName}/10 border border-${colorName}/20`}>
                        {toolIcons[tool.category] || <Wrench className="w-4 h-4" />}
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-foreground">{tool.name}</h3>
                        <Badge variant="outline" className="text-[10px] capitalize mt-0.5">{tool.category}</Badge>
                      </div>
                    </div>
                    <StatusBadge status={tool.status} />
                  </div>

                  <p className="text-xs text-muted-foreground mb-3 line-clamp-2">{tool.description}</p>

                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="p-1.5 rounded bg-secondary/30">
                      <p className="text-xs font-bold text-foreground">{tool.executions.toLocaleString()}</p>
                      <p className="text-[9px] text-muted-foreground">Execs</p>
                    </div>
                    <div className="p-1.5 rounded bg-secondary/30">
                      <p className="text-xs font-bold text-foreground">{tool.avgLatency}ms</p>
                      <p className="text-[9px] text-muted-foreground">Latency</p>
                    </div>
                    <div className="p-1.5 rounded bg-secondary/30">
                      <p className="text-xs font-bold text-foreground">{tool.version}</p>
                      <p className="text-[9px] text-muted-foreground">Version</p>
                    </div>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full mt-3 text-xs"
                    disabled={tool.status !== "available"}
                  >
                    <Play className="w-3 h-3 mr-1" />
                    Execute
                  </Button>
                </div>
              );
            })}
          </div>
        </TabsContent>

        {/* Execution History */}
        <TabsContent value="executions">
          <div className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  Execution History
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-72">
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
                      <Bar dataKey="executions" fill="#06b6d4" radius={[4, 4, 0, 0]} name="Executions" />
                      <Bar dataKey="errors" fill="#ef4444" radius={[4, 4, 0, 0]} name="Errors" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Execute Tool Dialog */}
      <Dialog open={executeDialogOpen} onOpenChange={setExecuteDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Execute Tool</DialogTitle>
            <DialogDescription>
              Select a tool and provide parameters to execute.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">Tool</label>
              <Select value={selectedTool} onValueChange={setSelectedTool}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a tool" />
                </SelectTrigger>
                <SelectContent>
                  {mockTools
                    .filter((t) => t.status === "available")
                    .map((tool) => (
                      <SelectItem key={tool.id} value={tool.name}>
                        {tool.name}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">Parameters (JSON)</label>
              <Textarea
                placeholder='{"key": "value"}'
                value={toolParams}
                onChange={(e) => setToolParams(e.target.value)}
                rows={4}
                className="font-mono text-xs"
              />
            </div>
            {executionResult && (
              <div>
                <label className="text-sm font-medium text-foreground mb-1.5 block">Result</label>
                <pre className="p-3 rounded-lg bg-secondary/30 border border-border/50 text-xs text-emerald font-mono overflow-x-auto">
                  {executionResult}
                </pre>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => { setExecuteDialogOpen(false); setExecutionResult(null); }}>
              Close
            </Button>
            <Button
              variant="cyan"
              onClick={handleExecute}
              disabled={!selectedTool || isExecuting}
            >
              {isExecuting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Executing...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Execute
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
