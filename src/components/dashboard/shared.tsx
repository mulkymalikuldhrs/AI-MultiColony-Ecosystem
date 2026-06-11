"use client";

import React from "react";
import { cn } from "@/lib/utils";

type StatusType = "active" | "idle" | "error" | "offline" | "connected" | "disconnected" | "available" | "busy" | "disabled" | "scaling";

const statusConfig: Record<StatusType, { color: string; label: string; dotClass: string }> = {
  active: { color: "text-emerald", label: "Active", dotClass: "status-dot-active" },
  idle: { color: "text-amber", label: "Idle", dotClass: "status-dot-idle" },
  error: { color: "text-rose", label: "Error", dotClass: "status-dot-error" },
  offline: { color: "text-muted-foreground", label: "Offline", dotClass: "status-dot-offline" },
  connected: { color: "text-emerald", label: "Connected", dotClass: "status-dot-active" },
  disconnected: { color: "text-muted-foreground", label: "Disconnected", dotClass: "status-dot-offline" },
  available: { color: "text-emerald", label: "Available", dotClass: "status-dot-active" },
  busy: { color: "text-amber", label: "Busy", dotClass: "status-dot-idle" },
  disabled: { color: "text-muted-foreground", label: "Disabled", dotClass: "status-dot-offline" },
  scaling: { color: "text-cyan", label: "Scaling", dotClass: "status-dot-idle" },
};

interface StatusBadgeProps {
  status: StatusType;
  size?: "sm" | "md";
  showDot?: boolean;
  className?: string;
}

export function StatusBadge({ status, size = "sm", showDot = true, className }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.offline;
  return (
    <span className={cn("inline-flex items-center gap-1.5 font-medium", size === "sm" ? "text-xs" : "text-sm", config.color, className)}>
      {showDot && <span className={cn("status-dot", config.dotClass)} />}
      {config.label}
    </span>
  );
}

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: { value: number; positive: boolean };
  color?: "cyan" | "purple" | "emerald" | "amber" | "rose";
  className?: string;
}

export function StatCard({ title, value, subtitle, icon, trend, color = "cyan", className }: StatCardProps) {
  const colorMap = {
    cyan: "border-cyan/20 hover:border-cyan/40",
    purple: "border-purple/20 hover:border-purple/40",
    emerald: "border-emerald/20 hover:border-emerald/40",
    amber: "border-amber/20 hover:border-amber/40",
    rose: "border-rose/20 hover:border-rose/40",
  };
  const textColorMap = {
    cyan: "text-cyan",
    purple: "text-purple",
    emerald: "text-emerald",
    amber: "text-amber",
    rose: "text-rose",
  };
  return (
    <div className={cn("glass-card p-4", colorMap[color], className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{title}</p>
          <p className={cn("text-2xl font-bold", textColorMap[color])}>{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        {icon && <div className={cn("p-2 rounded-lg bg-secondary/50", textColorMap[color])}>{icon}</div>}
      </div>
      {trend && (
        <div className="mt-2 flex items-center gap-1">
          <span className={cn("text-xs font-medium", trend.positive ? "text-emerald" : "text-rose")}>
            {trend.positive ? "↑" : "↓"} {Math.abs(trend.value)}%
          </span>
          <span className="text-xs text-muted-foreground">vs last hour</span>
        </div>
      )}
    </div>
  );
}

interface SectionHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function SectionHeader({ title, description, action, className }: SectionHeaderProps) {
  return (
    <div className={cn("flex items-center justify-between", className)}>
      <div>
        <h2 className="text-lg font-semibold text-foreground">{title}</h2>
        {description && <p className="text-sm text-muted-foreground mt-0.5">{description}</p>}
      </div>
      {action}
    </div>
  );
}
