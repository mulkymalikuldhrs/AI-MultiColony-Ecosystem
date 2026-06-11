"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Bot,
  Network,
  Wrench,
  Database,
  Radio,
  Shield,
  Settings,
  ChevronLeft,
  ChevronRight,
  Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/lib/store";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard, color: "text-cyan" },
  { href: "/agents", label: "Agents", icon: Bot, color: "text-purple" },
  { href: "/colony", label: "Colony", icon: Network, color: "text-emerald" },
  { href: "/tools", label: "Tools", icon: Wrench, color: "text-amber" },
  { href: "/memory", label: "Memory", icon: Database, color: "text-cyan" },
  { href: "/channels", label: "Channels", icon: Radio, color: "text-purple" },
  { href: "/security", label: "Security", icon: Shield, color: "text-rose" },
  { href: "/settings", label: "Settings", icon: Settings, color: "text-muted-foreground" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar, wsConnected } = useAppStore();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-sidebar border-r border-border/50 transition-all duration-300 flex flex-col",
        sidebarOpen ? "w-64" : "w-16"
      )}
    >
      {/* Logo / Brand */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-border/50">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/20 border border-primary/30">
          <Activity className="w-4 h-4 text-primary" />
        </div>
        {sidebarOpen && (
          <div className="overflow-hidden">
            <h1 className="text-sm font-bold text-foreground whitespace-nowrap">AI MultiColony</h1>
            <p className="text-[10px] text-muted-foreground whitespace-nowrap">Ecosystem OS</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group",
                isActive
                  ? "bg-primary/10 text-primary border border-primary/20"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              )}
            >
              <item.icon
                className={cn(
                  "w-5 h-5 shrink-0 transition-colors",
                  isActive ? "text-primary" : item.color
                )}
              />
              {sidebarOpen && <span className="whitespace-nowrap">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-2 pb-4 space-y-2">
        {/* WebSocket status */}
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-secondary/30">
          <span className={cn("status-dot", wsConnected ? "status-dot-active" : "status-dot-error")} />
          {sidebarOpen && (
            <span className="text-xs text-muted-foreground">
              {wsConnected ? "WS Connected" : "WS Disconnected"}
            </span>
          )}
        </div>

        {/* Toggle button */}
        <button
          onClick={toggleSidebar}
          className="flex items-center justify-center w-full py-2 rounded-lg hover:bg-secondary/50 text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
        >
          {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
}
