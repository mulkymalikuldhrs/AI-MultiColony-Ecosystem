import { Activity, Settings, Power, Skull } from "lucide-react";
import { Button } from "./ui/button";
import { StatusIndicator } from "./ui/status-indicator";

interface HeaderProps {
  organismName: string;
  generation: number;
  status: "online" | "offline" | "warning" | "error" | "processing";
}

export function Header({ organismName, generation, status }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Activity className="w-6 h-6 text-primary" />
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-success rounded-full animate-pulse" />
            </div>
            <div>
              <h1 className="text-lg font-bold gradient-text-primary">
                {organismName}
              </h1>
              <span className="text-[10px] text-muted-foreground font-mono">
                GEN-{generation.toString().padStart(4, "0")}
              </span>
            </div>
          </div>

          <StatusIndicator status={status} className="ml-4">
            System {status}
          </StatusIndicator>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
            <Settings className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="icon" className="text-warning hover:text-warning hover:bg-warning/10">
            <Power className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive hover:bg-destructive/10">
            <Skull className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
