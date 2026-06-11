"use client";

import React, { useState } from "react";
import {
  Database,
  Search,
  Plus,
  Brain,
  Layers,
  FileStack,
  Zap,
  RefreshCw,
  ChevronRight,
  Clock,
  Hash,
  HardDrive,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
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
import { StatCard, SectionHeader } from "@/components/dashboard/shared";
import { mockMemory, MEMORY_TYPES } from "@/lib/mock-data";

const categoryColors: Record<string, string> = {
  knowledge: "#06b6d4",
  session: "#8b5cf6",
  vector: "#10b981",
  condenser: "#f59e0b",
  paging: "#f43f5e",
};

const categoryIcons: Record<string, React.ReactNode> = {
  knowledge: <Brain className="w-4 h-4" />,
  session: <Clock className="w-4 h-4" />,
  vector: <Zap className="w-4 h-4" />,
  condenser: <Layers className="w-4 h-4" />,
  paging: <FileStack className="w-4 h-4" />,
};

export default function MemoryPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [storeDialogOpen, setStoreDialogOpen] = useState(false);
  const [storeKey, setStoreKey] = useState("");
  const [storeValue, setStoreValue] = useState("");
  const [storeCategory, setStoreCategory] = useState("knowledge");
  const [isStoring, setIsStoring] = useState(false);

  const filteredMemory = mockMemory.filter((entry) => {
    const matchesSearch = entry.key.toLowerCase().includes(searchQuery.toLowerCase()) || entry.value.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = filterCategory === "all" || entry.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const categoryCounts = mockMemory.reduce((acc, entry) => {
    acc[entry.category] = (acc[entry.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const pieData = Object.entries(categoryCounts).map(([name, value]) => ({
    name,
    value,
    color: categoryColors[name] || "#64748b",
  }));

  const totalSize = mockMemory.reduce((acc, m) => acc + m.size, 0);
  const totalAccess = mockMemory.reduce((acc, m) => acc + m.accessCount, 0);

  const handleStore = async () => {
    setIsStoring(true);
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsStoring(false);
    setStoreDialogOpen(false);
    setStoreKey("");
    setStoreValue("");
    setStoreCategory("knowledge");
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Database className="w-6 h-6 text-cyan" />
            Memory System
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Search, browse, and manage the knowledge base
          </p>
        </div>
        <Button variant="cyan" onClick={() => setStoreDialogOpen(true)} className="gap-2">
          <Plus className="w-4 h-4" />
          Store Memory
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          title="Total Entries"
          value={mockMemory.length}
          subtitle="In memory store"
          icon={<Database className="w-4 h-4" />}
          color="cyan"
        />
        <StatCard
          title="Total Size"
          value={`${(totalSize / 1024).toFixed(1)}KB`}
          subtitle="Memory footprint"
          icon={<HardDrive className="w-4 h-4" />}
          color="purple"
        />
        <StatCard
          title="Total Accesses"
          value={totalAccess.toLocaleString()}
          subtitle="Read operations"
          icon={<Search className="w-4 h-4" />}
          color="emerald"
        />
        <StatCard
          title="Categories"
          value={Object.keys(categoryCounts).length}
          subtitle="Memory types"
          icon={<Layers className="w-4 h-4" />}
          color="amber"
        />
        <StatCard
          title="Avg Access"
          value={Math.round(totalAccess / mockMemory.length)}
          subtitle="Per entry"
          icon={<Zap className="w-4 h-4" />}
          color="rose"
        />
      </div>

      <Tabs defaultValue="search">
        <TabsList>
          <TabsTrigger value="search">Memory Search</TabsTrigger>
          <TabsTrigger value="browser">Knowledge Browser</TabsTrigger>
          <TabsTrigger value="vector">Vector Store</TabsTrigger>
        </TabsList>

        {/* Search Tab */}
        <TabsContent value="search">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-4">
            {/* Search Panel */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                    <Search className="w-4 h-4 text-cyan" />
                    Search
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      placeholder="Search memories..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Category</label>
                    <Select value={filterCategory} onValueChange={setFilterCategory}>
                      <SelectTrigger>
                        <SelectValue placeholder="All" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Categories</SelectItem>
                        {MEMORY_TYPES.map((type) => (
                          <SelectItem key={type} value={type} className="capitalize">
                            {type}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Category Distribution */}
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-2 block">Distribution</label>
                    <div className="h-48">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            innerRadius={40}
                            outerRadius={70}
                            dataKey="value"
                          >
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

            {/* Results */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                    Search Results ({filteredMemory.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="max-h-[600px]">
                    <div className="space-y-2">
                      {filteredMemory.map((entry) => (
                        <div
                          key={entry.id}
                          className="p-3 rounded-lg bg-secondary/20 border border-border/50 hover:border-primary/20 transition-all cursor-pointer"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <div style={{ color: categoryColors[entry.category] }}>
                                {categoryIcons[entry.category]}
                              </div>
                              <span className="text-sm font-medium text-foreground font-mono">
                                {entry.key}
                              </span>
                            </div>
                            <Badge
                              variant="outline"
                              className="text-[10px] capitalize"
                              style={{ borderColor: categoryColors[entry.category], color: categoryColors[entry.category] }}
                            >
                              {entry.category}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground line-clamp-2 mb-2">{entry.value}</p>
                          <div className="flex items-center gap-4 text-[10px] text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {new Date(entry.timestamp).toLocaleString()}
                            </span>
                            <span className="flex items-center gap-1">
                              <HardDrive className="w-3 h-3" />
                              {entry.size}B
                            </span>
                            <span className="flex items-center gap-1">
                              <Hash className="w-3 h-3" />
                              {entry.accessCount} accesses
                            </span>
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

        {/* Knowledge Browser */}
        <TabsContent value="browser">
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {MEMORY_TYPES.map((type) => {
              const entries = mockMemory.filter((m) => m.category === type);
              const totalSize = entries.reduce((acc, m) => acc + m.size, 0);
              const totalAccess = entries.reduce((acc, m) => acc + m.accessCount, 0);
              return (
                <Card key={type}>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <span style={{ color: categoryColors[type] }}>{categoryIcons[type]}</span>
                      <span className="text-sm font-medium text-foreground capitalize">{type}</span>
                      <Badge variant="outline" className="text-[10px] ml-auto">
                        {entries.length} entries
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-2 text-center mb-3">
                      <div className="p-2 rounded bg-secondary/30">
                        <p className="text-sm font-bold text-foreground">{(totalSize / 1024).toFixed(1)}KB</p>
                        <p className="text-[9px] text-muted-foreground">Total Size</p>
                      </div>
                      <div className="p-2 rounded bg-secondary/30">
                        <p className="text-sm font-bold text-foreground">{totalAccess}</p>
                        <p className="text-[9px] text-muted-foreground">Accesses</p>
                      </div>
                    </div>
                    <div className="space-y-1">
                      {entries.map((entry) => (
                        <div key={entry.id} className="flex items-center gap-2 p-1.5 rounded bg-secondary/20 text-xs">
                          <ChevronRight className="w-3 h-3 text-muted-foreground shrink-0" />
                          <span className="text-foreground font-mono truncate">{entry.key}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Vector Store */}
        <TabsContent value="vector">
          <div className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <Zap className="w-4 h-4 text-emerald" />
                  Vector Store Explorer
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                  <div className="p-4 rounded-lg bg-secondary/20 border border-border/30">
                    <p className="text-xs text-muted-foreground mb-1">Embedding Model</p>
                    <p className="text-sm font-medium text-foreground">text-embedding-3-small</p>
                    <p className="text-xs text-muted-foreground mt-1">1536 dimensions</p>
                  </div>
                  <div className="p-4 rounded-lg bg-secondary/20 border border-border/30">
                    <p className="text-xs text-muted-foreground mb-1">Similarity Metric</p>
                    <p className="text-sm font-medium text-foreground">Cosine Similarity</p>
                    <p className="text-xs text-muted-foreground mt-1">Normalized vectors</p>
                  </div>
                  <div className="p-4 rounded-lg bg-secondary/20 border border-border/30">
                    <p className="text-xs text-muted-foreground mb-1">Vector Count</p>
                    <p className="text-sm font-medium text-foreground">{mockMemory.filter((m) => m.category === "vector").length}</p>
                    <p className="text-xs text-muted-foreground mt-1">Indexed entries</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-foreground">Vector Entries</h4>
                  {mockMemory
                    .filter((m) => m.category === "vector")
                    .map((entry) => (
                      <div
                        key={entry.id}
                        className="p-3 rounded-lg bg-secondary/20 border border-emerald/10 hover:border-emerald/30 transition-all"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-mono font-medium text-emerald">{entry.key}</span>
                          <Badge variant="emerald" className="text-[10px]">Vector</Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mb-2">{entry.value}</p>
                        <div className="flex items-center gap-2">
                          <div className="flex gap-0.5">
                            {Array.from({ length: 12 }, (_, i) => (
                              <div
                                key={i}
                                className="w-4 h-8 rounded-sm"
                                style={{
                                  backgroundColor: `rgba(16, 185, 129, ${Math.random() * 0.8 + 0.2})`,
                                }}
                              />
                            ))}
                          </div>
                          <span className="text-[10px] text-muted-foreground">Embedding preview (12 of 1536 dims)</span>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Store Memory Dialog */}
      <Dialog open={storeDialogOpen} onOpenChange={setStoreDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Store Memory</DialogTitle>
            <DialogDescription>
              Save data to the memory system for later retrieval.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">Key</label>
              <Input
                placeholder="e.g., my_config_key"
                value={storeKey}
                onChange={(e) => setStoreKey(e.target.value)}
                className="font-mono"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">Value</label>
              <Textarea
                placeholder="Enter the data to store..."
                value={storeValue}
                onChange={(e) => setStoreValue(e.target.value)}
                rows={4}
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">Category</label>
              <Select value={storeCategory} onValueChange={setStoreCategory}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {MEMORY_TYPES.map((type) => (
                    <SelectItem key={type} value={type} className="capitalize">
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setStoreDialogOpen(false)}>Cancel</Button>
            <Button
              variant="cyan"
              onClick={handleStore}
              disabled={!storeKey || !storeValue || isStoring}
            >
              {isStoring ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Storing...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Store
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
