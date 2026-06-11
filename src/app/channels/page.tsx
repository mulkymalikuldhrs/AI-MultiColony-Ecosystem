"use client";

import React, { useState } from "react";
import {
  Radio,
  MessageSquare,
  Send,
  Settings,
  RefreshCw,
  Wifi,
  WifiOff,
  AlertCircle,
  MessageCircle,
  Phone,
  Hash,
  Clock,
  ArrowUpRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { StatCard, StatusBadge, SectionHeader } from "@/components/dashboard/shared";
import { mockChannels, CHANNEL_TYPES } from "@/lib/mock-data";

const channelIcons: Record<string, React.ReactNode> = {
  discord: <MessageCircle className="w-5 h-5" />,
  slack: <Hash className="w-5 h-5" />,
  telegram: <Send className="w-5 h-5" />,
  whatsapp: <Phone className="w-5 h-5" />,
};

const channelColors: Record<string, string> = {
  discord: "purple",
  slack: "cyan",
  telegram: "emerald",
  whatsapp: "emerald",
};

// Mock messages
const mockMessages = [
  { id: "1", channel: "discord", sender: "ColonyBot", message: "Colony-Alpha health check: 98% — All systems nominal", timestamp: "12:30:15", type: "system" },
  { id: "2", channel: "slack", sender: "Agent-Alert", message: "⚠️ Browser-Alpha CPU usage exceeding 70% threshold", timestamp: "12:28:45", type: "alert" },
  { id: "3", channel: "discord", sender: "Security-Eta", message: "Security scan completed. No threats detected.", timestamp: "12:25:30", type: "info" },
  { id: "4", channel: "slack", sender: "Planner-Epsilon", message: "Task #892 decomposed into 3 subtasks. Scheduling execution.", timestamp: "12:22:00", type: "info" },
  { id: "5", channel: "telegram", sender: "ColonyBot", message: "Colony-Gamma entering idle mode. 2 agents available.", timestamp: "12:20:15", type: "system" },
  { id: "6", channel: "discord", sender: "Registry-Iota", message: "New tool registered: Container Tool v1.2.0", timestamp: "12:18:00", type: "info" },
  { id: "7", channel: "whatsapp", sender: "Agent-Alert", message: "🚨 Unauthorized access attempt blocked from IP 192.168.1.100", timestamp: "12:15:30", type: "alert" },
  { id: "8", channel: "slack", sender: "Coder-Beta", message: "Pull request #42 created: Feature/memory-optimization", timestamp: "12:13:00", type: "info" },
  { id: "9", channel: "discord", sender: "Executor-Gamma", message: "Task #891 completed successfully in 2.3s", timestamp: "12:10:15", type: "system" },
  { id: "10", channel: "telegram", sender: "Manus-Delta", message: "Research report generated: AI Market Trends Q1 2025", timestamp: "12:08:00", type: "info" },
];

export default function ChannelsPage() {
  const [selectedChannel, setSelectedChannel] = useState<string>("discord");
  const [messageInput, setMessageInput] = useState("");

  const activeChannels = mockChannels.filter((c) => c.status === "connected").length;
  const totalMessages = mockChannels.reduce((acc, c) => acc + c.messages, 0);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Radio className="w-6 h-6 text-purple" />
            Communication Channels
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Configure and monitor multi-platform messaging
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Connected"
          value={activeChannels}
          subtitle={`of ${mockChannels.length} channels`}
          icon={<Wifi className="w-4 h-4" />}
          color="emerald"
        />
        <StatCard
          title="Total Messages"
          value={totalMessages.toLocaleString()}
          subtitle="All time"
          icon={<MessageSquare className="w-4 h-4" />}
          color="cyan"
        />
        <StatCard
          title="Active Platforms"
          value={new Set(mockChannels.map((c) => c.type)).size}
          subtitle="Integrated"
          icon={<Radio className="w-4 h-4" />}
          color="purple"
        />
        <StatCard
          title="Error Rate"
          value="0.3%"
          subtitle="Last 24 hours"
          icon={<AlertCircle className="w-4 h-4" />}
          color="amber"
        />
      </div>

      <Tabs defaultValue="monitor">
        <TabsList>
          <TabsTrigger value="monitor">Message Monitor</TabsTrigger>
          <TabsTrigger value="config">Channel Config</TabsTrigger>
        </TabsList>

        {/* Message Monitor */}
        <TabsContent value="monitor">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-4">
            {/* Channel Selector */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                    Channels
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {mockChannels.map((channel) => (
                    <button
                      key={channel.id}
                      onClick={() => setSelectedChannel(channel.type)}
                      className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-all cursor-pointer ${
                        selectedChannel === channel.type
                          ? "bg-primary/10 border-primary/30"
                          : "bg-secondary/20 border-border/30 hover:border-primary/20"
                      }`}
                    >
                      <div className={`text-${channelColors[channel.type]}`}>
                        {channelIcons[channel.type]}
                      </div>
                      <div className="text-left flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-foreground">{channel.name}</span>
                        </div>
                        <div className="flex items-center gap-2 mt-0.5">
                          <StatusBadge status={channel.status} />
                          <span className="text-[10px] text-muted-foreground">{channel.messages} msgs</span>
                        </div>
                      </div>
                    </button>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Message Feed */}
            <div className="lg:col-span-3">
              <Card className="flex flex-col h-[600px]">
                <CardHeader className="border-b border-border/30">
                  <CardTitle className="flex items-center justify-between">
                    <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                      {channelIcons[selectedChannel]}
                      {selectedChannel.charAt(0).toUpperCase() + selectedChannel.slice(1)} — Live Feed
                    </span>
                    <Badge variant="outline" className="text-[10px]">
                      {mockMessages.filter((m) => m.channel === selectedChannel).length} messages
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex-1 overflow-hidden p-0">
                  <ScrollArea className="h-full max-h-[480px] p-4">
                    <div className="space-y-3">
                      {mockMessages
                        .filter((m) => m.channel === selectedChannel)
                        .map((msg) => (
                          <div
                            key={msg.id}
                            className={`flex items-start gap-3 p-3 rounded-lg border-l-2 ${
                              msg.type === "alert"
                                ? "bg-amber/5 border-l-amber"
                                : msg.type === "system"
                                ? "bg-cyan/5 border-l-cyan"
                                : "bg-secondary/10 border-l-purple"
                            }`}
                          >
                            <div className="w-8 h-8 rounded-full bg-secondary/50 flex items-center justify-center shrink-0 text-xs font-bold text-foreground">
                              {msg.sender.charAt(0)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-0.5">
                                <span className="text-sm font-medium text-foreground">{msg.sender}</span>
                                <span className="text-[10px] text-muted-foreground">{msg.timestamp}</span>
                                {msg.type === "alert" && <Badge variant="amber" className="text-[9px]">Alert</Badge>}
                                {msg.type === "system" && <Badge variant="cyan" className="text-[9px]">System</Badge>}
                              </div>
                              <p className="text-xs text-muted-foreground leading-relaxed">{msg.message}</p>
                            </div>
                          </div>
                        ))}
                      {mockMessages.filter((m) => m.channel === selectedChannel).length === 0 && (
                        <div className="text-center py-12 text-muted-foreground">
                          <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                          <p className="text-sm">No messages for this channel</p>
                        </div>
                      )}
                    </div>
                  </ScrollArea>
                </CardContent>
                {/* Message Input */}
                <div className="p-3 border-t border-border/30">
                  <div className="flex items-center gap-2">
                    <Input
                      placeholder={`Send message to ${selectedChannel}...`}
                      value={messageInput}
                      onChange={(e) => setMessageInput(e.target.value)}
                      className="flex-1"
                    />
                    <Button variant="cyan" size="icon" disabled={!messageInput}>
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Channel Configuration */}
        <TabsContent value="config">
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-6">
            {mockChannels.map((channel) => (
              <Card key={channel.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <span className={`text-${channelColors[channel.type]}`}>
                        {channelIcons[channel.type]}
                      </span>
                      <span className="text-sm font-medium text-foreground">{channel.name}</span>
                    </span>
                    <div className="flex items-center gap-2">
                      <StatusBadge status={channel.status} />
                      <Switch
                        checked={channel.status === "connected"}
                        onCheckedChange={() => {}}
                      />
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    {Object.entries(channel.config).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between p-2 rounded bg-secondary/20">
                        <span className="text-xs text-muted-foreground capitalize">{key.replace(/_/g, " ")}</span>
                        <span className="text-xs text-foreground font-mono">
                          {key.includes("token") ? "••••••••" : value}
                        </span>
                      </div>
                    ))}
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        Last message: {channel.lastMessage}
                      </span>
                    </div>
                    <Button variant="outline" size="sm" className="text-xs gap-1">
                      <Settings className="w-3 h-3" />
                      Configure
                    </Button>
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
