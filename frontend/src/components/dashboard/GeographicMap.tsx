import { Globe } from "lucide-react";

export function GeographicMap() {
  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-foreground mb-4">Geographic Locations</h3>
      
      <div className="relative h-48 rounded-lg overflow-hidden bg-secondary/30 cyber-grid">
        {/* Simplified world map visualization */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="relative">
            <Globe className="w-24 h-24 text-muted-foreground/30" />
            
            {/* Attack origin dots */}
            <div className="absolute top-4 left-8 w-2 h-2 rounded-full bg-destructive animate-pulse" />
            <div className="absolute top-8 right-4 w-2 h-2 rounded-full bg-warning animate-pulse" style={{ animationDelay: "0.5s" }} />
            <div className="absolute bottom-8 left-12 w-2 h-2 rounded-full bg-primary animate-pulse" style={{ animationDelay: "1s" }} />
            <div className="absolute bottom-4 right-8 w-2 h-2 rounded-full bg-success animate-pulse" style={{ animationDelay: "1.5s" }} />
          </div>
        </div>
        
        {/* Location stats */}
        <div className="absolute bottom-4 left-4 right-4 flex justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-destructive" />
            <span className="text-xs text-muted-foreground">US: 45%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-warning" />
            <span className="text-xs text-muted-foreground">CN: 23%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary" />
            <span className="text-xs text-muted-foreground">RU: 18%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-success" />
            <span className="text-xs text-muted-foreground">Other: 14%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
