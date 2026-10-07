import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
}

export function StatCard({ title, value, icon: Icon, trend, className }: StatCardProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-lg bg-card border border-border p-6",
        "transition-all duration-300 hover:border-primary/50 hover:glow-primary",
        "animate-fade-in",
        className
      )}
    >
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-primary/5 to-transparent rounded-bl-full" />
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-muted-foreground">{title}</span>
          {Icon && (
            <Icon className="w-5 h-5 text-primary opacity-70" />
          )}
        </div>
        
        <div className="flex items-end gap-2">
          <span className="text-3xl font-bold font-mono text-foreground glow-text">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </span>
          
          {trend && (
            <span
              className={cn(
                "text-sm font-medium mb-1",
                trend.isPositive ? "text-success" : "text-destructive"
              )}
            >
              {trend.isPositive ? "+" : "-"}{Math.abs(trend.value)}%
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
