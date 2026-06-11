"use client";

import React, { useState } from "react";
import {
  Settings,
  Key,
  Server,
  Cpu,
  Globe,
  Save,
  RefreshCw,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle2,
  Plug,
  Shield,
  Database,
  Bell,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { StatCard } from "@/components/dashboard/shared";

interface LLMProvider {
  id: string;
  name: string;
  model: string;
  apiKey: string;
  baseUrl: string;
  enabled: boolean;
}

interface MCPConfig {
  id: string;
  name: string;
  server: string;
  status: "connected" | "disconnected" | "error";
  tools: number;
}

export default function SettingsPage() {
  const [saving, setSaving] = useState(false);
  const [showApiKeys, setShowApiKeys] = useState<Record<string, boolean>>({});

  const [llmProviders, setLlmProviders] = useState<LLMProvider[]>([
    { id: "llm-1", name: "OpenAI", model: "gpt-4-turbo", apiKey: "sk-...xxxx", baseUrl: "https://api.openai.com/v1", enabled: true },
    { id: "llm-2", name: "Anthropic", model: "claude-3-opus", apiKey: "sk-ant-...xxxx", baseUrl: "https://api.anthropic.com", enabled: true },
    { id: "llm-3", name: "Google AI", model: "gemini-pro", apiKey: "AIza...xxxx", baseUrl: "https://generativelanguage.googleapis.com", enabled: false },
    { id: "llm-4", name: "Local LLM", model: "llama-3-8b", apiKey: "", baseUrl: "http://localhost:11434", enabled: false },
  ]);

  const [mcpConfigs, setMcpConfigs] = useState<MCPConfig[]>([
    { id: "mcp-1", name: "Filesystem MCP", server: "stdio:///mcp/filesystem", status: "connected", tools: 8 },
    { id: "mcp-2", name: "Browser MCP", server: "stdio:///mcp/browser", status: "connected", tools: 12 },
    { id: "mcp-3", name: "Database MCP", server: "stdio:///mcp/database", status: "disconnected", tools: 5 },
    { id: "mcp-4", name: "Git MCP", server: "stdio:///mcp/git", status: "connected", tools: 10 },
    { id: "mcp-5", name: "Custom MCP", server: "ws://localhost:8080/mcp", status: "error", tools: 0 },
  ]);

  const [systemConfig, setSystemConfig] = useState({
    maxAgents: 20,
    maxColonies: 10,
    taskTimeout: 300,
    memoryLimit: 512,
    logLevel: "info",
    enableWebSocket: true,
    enableEventBus: true,
    enableAuditLog: true,
    autoRestart: true,
    notificationsEnabled: true,
  });

  const handleSave = async () => {
    setSaving(true);
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setSaving(false);
  };

  const toggleApiKeyVisibility = (id: string) => {
    setShowApiKeys((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const toggleProvider = (id: string) => {
    setLlmProviders((prev) =>
      prev.map((p) => (p.id === id ? { ...p, enabled: !p.enabled } : p))
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Settings className="w-6 h-6 text-muted-foreground" />
            System Settings
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Configure the AI MultiColony Ecosystem
          </p>
        </div>
        <Button variant="cyan" onClick={handleSave} disabled={saving} className="gap-2">
          {saving ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Save Changes
            </>
          )}
        </Button>
      </div>

      <Tabs defaultValue="general">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="llm">LLM Providers</TabsTrigger>
          <TabsTrigger value="mcp">MCP Config</TabsTrigger>
          <TabsTrigger value="apikeys">API Keys</TabsTrigger>
        </TabsList>

        {/* General Settings */}
        <TabsContent value="general">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <Server className="w-4 h-4 text-cyan" />
                  System Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Max Agents</label>
                    <Input
                      type="number"
                      value={systemConfig.maxAgents}
                      onChange={(e) => setSystemConfig({ ...systemConfig, maxAgents: parseInt(e.target.value) || 0 })}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Max Colonies</label>
                    <Input
                      type="number"
                      value={systemConfig.maxColonies}
                      onChange={(e) => setSystemConfig({ ...systemConfig, maxColonies: parseInt(e.target.value) || 0 })}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Task Timeout (s)</label>
                    <Input
                      type="number"
                      value={systemConfig.taskTimeout}
                      onChange={(e) => setSystemConfig({ ...systemConfig, taskTimeout: parseInt(e.target.value) || 0 })}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Memory Limit (MB)</label>
                    <Input
                      type="number"
                      value={systemConfig.memoryLimit}
                      onChange={(e) => setSystemConfig({ ...systemConfig, memoryLimit: parseInt(e.target.value) || 0 })}
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Log Level</label>
                  <Select
                    value={systemConfig.logLevel}
                    onValueChange={(value) => setSystemConfig({ ...systemConfig, logLevel: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="debug">Debug</SelectItem>
                      <SelectItem value="info">Info</SelectItem>
                      <SelectItem value="warning">Warning</SelectItem>
                      <SelectItem value="error">Error</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-purple" />
                  Feature Toggles
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { key: "enableWebSocket", label: "WebSocket Server", desc: "Real-time updates via WebSocket", icon: <Globe className="w-4 h-4" /> },
                  { key: "enableEventBus", label: "Event Bus", desc: "Internal event bus architecture", icon: <Cpu className="w-4 h-4" /> },
                  { key: "enableAuditLog", label: "Audit Logging", desc: "Track all system actions", icon: <Shield className="w-4 h-4" /> },
                  { key: "autoRestart", label: "Auto Restart", desc: "Restart failed agents automatically", icon: <RefreshCw className="w-4 h-4" /> },
                  { key: "notificationsEnabled", label: "Notifications", desc: "Push notifications for events", icon: <Bell className="w-4 h-4" /> },
                ].map((toggle) => (
                  <div key={toggle.key} className="flex items-center justify-between p-3 rounded-lg bg-secondary/20">
                    <div className="flex items-center gap-3">
                      <div className="text-muted-foreground">{toggle.icon}</div>
                      <div>
                        <p className="text-sm font-medium text-foreground">{toggle.label}</p>
                        <p className="text-xs text-muted-foreground">{toggle.desc}</p>
                      </div>
                    </div>
                    <Switch
                      checked={systemConfig[toggle.key as keyof typeof systemConfig] as boolean}
                      onCheckedChange={(checked) =>
                        setSystemConfig({ ...systemConfig, [toggle.key]: checked })
                      }
                    />
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* LLM Providers */}
        <TabsContent value="llm">
          <div className="mt-4 space-y-4">
            {llmProviders.map((provider) => (
              <Card key={provider.id}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${provider.enabled ? "bg-cyan/10 border border-cyan/20" : "bg-secondary/30 border border-border/30"}`}>
                        <Cpu className={`w-4 h-4 ${provider.enabled ? "text-cyan" : "text-muted-foreground"}`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-semibold text-foreground">{provider.name}</h3>
                          <Badge variant="outline" className="text-[10px]">{provider.model}</Badge>
                        </div>
                        <p className="text-xs text-muted-foreground">{provider.baseUrl}</p>
                      </div>
                    </div>
                    <Switch
                      checked={provider.enabled}
                      onCheckedChange={() => toggleProvider(provider.id)}
                    />
                  </div>

                  {provider.enabled && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Model</label>
                        <Input
                          value={provider.model}
                          onChange={(e) =>
                            setLlmProviders((prev) =>
                              prev.map((p) => (p.id === provider.id ? { ...p, model: e.target.value } : p))
                            )
                          }
                        />
                      </div>
                      <div>
                        <label className="text-xs font-medium text-muted-foreground mb-1.5 block">API Key</label>
                        <div className="relative">
                          <Input
                            type={showApiKeys[provider.id] ? "text" : "password"}
                            value={provider.apiKey}
                            onChange={(e) =>
                              setLlmProviders((prev) =>
                                prev.map((p) => (p.id === provider.id ? { ...p, apiKey: e.target.value } : p))
                              )
                            }
                            className="pr-10"
                          />
                          <button
                            onClick={() => toggleApiKeyVisibility(provider.id)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground cursor-pointer"
                          >
                            {showApiKeys[provider.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                      <div className="sm:col-span-2">
                        <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Base URL</label>
                        <Input
                          value={provider.baseUrl}
                          onChange={(e) =>
                            setLlmProviders((prev) =>
                              prev.map((p) => (p.id === provider.id ? { ...p, baseUrl: e.target.value } : p))
                            )
                          }
                        />
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* MCP Configuration */}
        <TabsContent value="mcp">
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {mcpConfigs.map((mcp) => (
              <Card key={mcp.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground flex items-center gap-2">
                      <Plug className={`w-4 h-4 ${mcp.status === "connected" ? "text-emerald" : mcp.status === "error" ? "text-rose" : "text-muted-foreground"}`} />
                      {mcp.name}
                    </span>
                    <Badge
                      variant={mcp.status === "connected" ? "emerald" : mcp.status === "error" ? "rose" : "outline"}
                      className="text-[10px]"
                    >
                      {mcp.status}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="p-2 rounded bg-secondary/20">
                    <span className="text-[10px] text-muted-foreground">Server</span>
                    <p className="text-xs text-foreground font-mono truncate">{mcp.server}</p>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Available Tools</span>
                    <span className="text-xs text-foreground font-medium">{mcp.tools}</span>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="text-xs flex-1">
                      Configure
                    </Button>
                    {mcp.status === "disconnected" && (
                      <Button variant="cyan" size="sm" className="text-xs">
                        Connect
                      </Button>
                    )}
                    {mcp.status === "connected" && (
                      <Button variant="ghost" size="sm" className="text-xs text-rose">
                        Disconnect
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* API Keys */}
        <TabsContent value="apikeys">
          <div className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <Key className="w-4 h-4 text-amber" />
                  API Key Management
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 rounded-lg border border-amber/20 bg-amber/5">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-amber shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-amber">Security Notice</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        API keys are stored securely and never exposed in logs. Keys are masked in the UI for security.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  {[
                    { name: "Ecosystem API Key", key: "eco_xxxxxxxxxxxxxxxxxxxx", created: "Jan 10, 2025", lastUsed: "2 hours ago" },
                    { name: "WebSocket Auth Token", key: "wsat_xxxxxxxxxxxxxxxxxxxx", created: "Jan 12, 2025", lastUsed: "5 minutes ago" },
                    { name: "Webhook Secret", key: "whsec_xxxxxxxxxxxxxxxxxxxx", created: "Jan 8, 2025", lastUsed: "1 day ago" },
                    { name: "MCP Auth Key", key: "mcpk_xxxxxxxxxxxxxxxxxxxx", created: "Jan 14, 2025", lastUsed: "Never" },
                  ].map((apiKey, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-secondary/20 border border-border/30">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-foreground">{apiKey.name}</p>
                        <p className="text-xs text-muted-foreground font-mono mt-0.5">{apiKey.key}</p>
                        <div className="flex items-center gap-3 mt-1 text-[10px] text-muted-foreground">
                          <span>Created: {apiKey.created}</span>
                          <span>Last used: {apiKey.lastUsed}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" className="text-xs">
                          Regenerate
                        </Button>
                        <Button variant="ghost" size="sm" className="text-xs text-rose">
                          Revoke
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>

                <Button variant="outline" className="gap-2">
                  <Key className="w-4 h-4" />
                  Generate New Key
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
