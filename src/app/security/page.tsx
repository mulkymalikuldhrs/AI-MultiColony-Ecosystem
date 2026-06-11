"use client";

import React, { useState } from "react";
import {
  Shield,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Lock,
  Unlock,
  Container,
  Search,
  Filter,
  RefreshCw,
  Eye,
  FileWarning,
  Server,
  Activity,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { StatCard, StatusBadge, SectionHeader } from "@/components/dashboard/shared";
import { mockSecurityEvents } from "@/lib/mock-data";

const severityColors: Record<string, string> = {
  low: "emerald",
  medium: "amber",
  high: "rose",
  critical: "rose",
};

const severityBg: Record<string, string> = {
  low: "bg-emerald/5 border-l-emerald",
  medium: "bg-amber/5 border-l-amber",
  high: "bg-rose/5 border-l-rose",
  critical: "bg-rose/10 border-l-rose",
};

const typeIcons: Record<string, React.ReactNode> = {
  audit: <Eye className="w-3.5 h-3.5" />,
  permission: <Lock className="w-3.5 h-3.5" />,
  sandbox: <Container className="w-3.5 h-3.5" />,
  alert: <AlertTriangle className="w-3.5 h-3.5" />,
};

// Mock permission rules
const mockPermissions = [
  { id: "perm-1", agent: "Browser-Alpha", resource: "memory:read", granted: true },
  { id: "perm-2", agent: "Browser-Alpha", resource: "shell:execute", granted: false },
  { id: "perm-3", agent: "Coder-Beta", resource: "code:execute", granted: true },
  { id: "perm-4", agent: "Coder-Beta", resource: "file:write", granted: true },
  { id: "perm-5", agent: "Executor-Gamma", resource: "docker:manage", granted: true },
  { id: "perm-6", agent: "Voice-Theta", resource: "shell:execute", granted: false },
  { id: "perm-7", agent: "Security-Eta", resource: "system:audit", granted: true },
  { id: "perm-8", agent: "Security-Eta", resource: "permission:manage", granted: true },
  { id: "perm-9", agent: "Manus-Delta", resource: "memory:write", granted: true },
  { id: "perm-10", agent: "Manus-Delta", resource: "network:external", granted: false },
];

// Mock sandbox status
const mockSandbox = [
  { id: "sb-1", name: "Docker Container Alpha", type: "docker", status: "running", cpu: 35, memory: 48, agents: 2 },
  { id: "sb-2", name: "Docker Container Beta", type: "docker", status: "running", cpu: 22, memory: 31, agents: 1 },
  { id: "sb-3", name: "WASM Sandbox Gamma", type: "wasm", status: "idle", cpu: 0, memory: 5, agents: 0 },
  { id: "sb-4", name: "Docker Container Delta", type: "docker", status: "stopped", cpu: 0, memory: 0, agents: 0 },
];

export default function SecurityPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterSeverity, setFilterSeverity] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");

  const filteredEvents = mockSecurityEvents.filter((event) => {
    const matchesSearch = event.message.toLowerCase().includes(searchQuery.toLowerCase()) || event.source.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSeverity = filterSeverity === "all" || event.severity === filterSeverity;
    const matchesType = filterType === "all" || event.type === filterType;
    return matchesSearch && matchesSeverity && matchesType;
  });

  const unresolvedEvents = mockSecurityEvents.filter((e) => !e.resolved);
  const severityCounts = mockSecurityEvents.reduce((acc, e) => {
    acc[e.severity] = (acc[e.severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const pieData = Object.entries(severityCounts).map(([name, value]) => ({
    name,
    value,
    color: { low: "#10b981", medium: "#f59e0b", high: "#ef4444", critical: "#dc2626" }[name] || "#64748b",
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Shield className="w-6 h-6 text-rose" />
            Security Center
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Audit logs, permissions, and sandbox management
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          title="Total Events"
          value={mockSecurityEvents.length}
          subtitle="Security events logged"
          icon={<Activity className="w-4 h-4" />}
          color="cyan"
        />
        <StatCard
          title="Unresolved"
          value={unresolvedEvents.length}
          subtitle="Require attention"
          icon={<AlertTriangle className="w-4 h-4" />}
          color="rose"
        />
        <StatCard
          title="Critical"
          value={severityCounts.critical || 0}
          subtitle="Critical alerts"
          icon={<XCircle className="w-4 h-4" />}
          color="rose"
        />
        <StatCard
          title="Sandbox Active"
          value={mockSandbox.filter((s) => s.status === "running").length}
          subtitle={`of ${mockSandbox.length} total`}
          icon={<Container className="w-4 h-4" />}
          color="amber"
        />
        <StatCard
          title="Permission Rules"
          value={mockPermissions.length}
          subtitle="Access control rules"
          icon={<Lock className="w-4 h-4" />}
          color="purple"
        />
      </div>

      <Tabs defaultValue="audit">
        <TabsList>
          <TabsTrigger value="audit">Audit Log</TabsTrigger>
          <TabsTrigger value="permissions">Permissions</TabsTrigger>
          <TabsTrigger value="sandbox">Sandbox</TabsTrigger>
        </TabsList>

        {/* Audit Log */}
        <TabsContent value="audit">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-4">
            {/* Filters + Severity Distribution */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                    Filters
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      placeholder="Search events..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Severity</label>
                    <Select value={filterSeverity} onValueChange={setFilterSeverity}>
                      <SelectTrigger>
                        <SelectValue placeholder="All" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Severities</SelectItem>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Type</label>
                    <Select value={filterType} onValueChange={setFilterType}>
                      <SelectTrigger>
                        <SelectValue placeholder="All" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="audit">Audit</SelectItem>
                        <SelectItem value="permission">Permission</SelectItem>
                        <SelectItem value="sandbox">Sandbox</SelectItem>
                        <SelectItem value="alert">Alert</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Separator className="bg-border/50" />

                  {/* Severity Distribution */}
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-2 block">Severity Distribution</label>
                    <div className="h-40">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie data={pieData} cx="50%" cy="50%" innerRadius={30} outerRadius={55} dataKey="value">
                            {pieData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip
                            contentStyle={{
                              background: "#111827",
                              border: "1px solid #1e293b",
                              borderRadius: "8px",
                              fontSize: "12px",
                            }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="space-y-1">
                      {pieData.map((entry) => (
                        <div key={entry.name} className="flex items-center justify-between text-xs">
                          <div className="flex items-center gap-1.5">
                            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                            <span className="text-muted-foreground capitalize">{entry.name}</span>
                          </div>
                          <span className="text-foreground">{entry.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Events List */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                    Security Events ({filteredEvents.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="max-h-[600px]">
                    <div className="space-y-2">
                      {filteredEvents.map((event) => (
                        <div
                          key={event.id}
                          className={`p-3 rounded-lg border-l-2 ${severityBg[event.severity]} transition-all`}
                        >
                          <div className="flex items-start justify-between mb-1.5">
                            <div className="flex items-center gap-2">
                              <span className={event.severity === "critical" || event.severity === "high" ? "text-rose" : event.severity === "medium" ? "text-amber" : "text-emerald"}>
                                {typeIcons[event.type]}
                              </span>
                              <Badge
                                variant={severityColors[event.severity] as "emerald" | "amber" | "rose"}
                                className="text-[10px] capitalize"
                              >
                                {event.severity}
                              </Badge>
                              <Badge variant="outline" className="text-[10px] capitalize">{event.type}</Badge>
                            </div>
                            <div className="flex items-center gap-2">
                              {event.resolved ? (
                                <Badge variant="emerald" className="text-[10px] gap-0.5">
                                  <CheckCircle2 className="w-2.5 h-2.5" />
                                  Resolved
                                </Badge>
                              ) : (
                                <Badge variant="rose" className="text-[10px] gap-0.5">
                                  <XCircle className="w-2.5 h-2.5" />
                                  Unresolved
                                </Badge>
                              )}
                            </div>
                          </div>
                          <p className="text-xs text-foreground mb-1">{event.message}</p>
                          <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                            <span>Source: {event.source}</span>
                            <span>{new Date(event.timestamp).toLocaleString()}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Permissions */}
        <TabsContent value="permissions">
          <div className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <Lock className="w-4 h-4 text-purple" />
                  Permission Rules
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border/50">
                        <th className="text-left py-2 px-3 text-xs text-muted-foreground font-medium">Agent</th>
                        <th className="text-left py-2 px-3 text-xs text-muted-foreground font-medium">Resource</th>
                        <th className="text-left py-2 px-3 text-xs text-muted-foreground font-medium">Access</th>
                        <th className="text-left py-2 px-3 text-xs text-muted-foreground font-medium">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mockPermissions.map((perm) => (
                        <tr key={perm.id} className="border-b border-border/20 hover:bg-secondary/20">
                          <td className="py-2.5 px-3 text-foreground text-xs font-medium">{perm.agent}</td>
                          <td className="py-2.5 px-3">
                            <code className="text-xs bg-secondary/40 px-1.5 py-0.5 rounded font-mono">{perm.resource}</code>
                          </td>
                          <td className="py-2.5 px-3">
                            {perm.granted ? (
                              <Badge variant="emerald" className="text-[10px] gap-0.5">
                                <Unlock className="w-2.5 h-2.5" />
                                Granted
                              </Badge>
                            ) : (
                              <Badge variant="rose" className="text-[10px] gap-0.5">
                                <Lock className="w-2.5 h-2.5" />
                                Denied
                              </Badge>
                            )}
                          </td>
                          <td className="py-2.5 px-3">
                            <Button variant="ghost" size="sm" className="text-[10px] h-6">
                              Edit
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Sandbox */}
        <TabsContent value="sandbox">
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-6">
            {mockSandbox.map((sandbox) => (
              <Card key={sandbox.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground flex items-center gap-2">
                      <Container className="w-4 h-4 text-amber" />
                      {sandbox.name}
                    </span>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-[10px] uppercase">
                        {sandbox.type}
                      </Badge>
                      <StatusBadge
                        status={sandbox.status === "running" ? "active" : sandbox.status === "idle" ? "idle" : "offline"}
                      />
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    <div className="p-2 rounded bg-secondary/20 text-center">
                      <p className="text-sm font-bold text-foreground">{sandbox.cpu}%</p>
                      <p className="text-[9px] text-muted-foreground">CPU</p>
                    </div>
                    <div className="p-2 rounded bg-secondary/20 text-center">
                      <p className="text-sm font-bold text-foreground">{sandbox.memory}%</p>
                      <p className="text-[9px] text-muted-foreground">Memory</p>
                    </div>
                    <div className="p-2 rounded bg-secondary/20 text-center">
                      <p className="text-sm font-bold text-foreground">{sandbox.agents}</p>
                      <p className="text-[9px] text-muted-foreground">Agents</p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-muted-foreground">CPU</span>
                        <span className="text-foreground">{sandbox.cpu}%</span>
                      </div>
                      <Progress value={sandbox.cpu} indicatorClassName={sandbox.cpu > 70 ? "bg-amber" : "bg-cyan"} />
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-muted-foreground">Memory</span>
                        <span className="text-foreground">{sandbox.memory}%</span>
                      </div>
                      <Progress value={sandbox.memory} indicatorClassName={sandbox.memory > 70 ? "bg-amber" : "bg-purple"} />
                    </div>
                  </div>

                  <div className="flex gap-2 mt-4">
                    {sandbox.status === "running" ? (
                      <Button variant="outline" size="sm" className="text-xs">Stop</Button>
                    ) : (
                      <Button variant="cyan" size="sm" className="text-xs">Start</Button>
                    )}
                    <Button variant="ghost" size="sm" className="text-xs">Restart</Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
