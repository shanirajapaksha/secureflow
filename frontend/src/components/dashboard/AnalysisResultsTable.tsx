import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { PredictionRow } from "@/lib/api";

interface AnalysisResultsTableProps {
  predictions?: PredictionRow[];
}

function statusClass(status: string) {
  return status === "INTRUSION"
    ? "bg-destructive text-destructive-foreground"
    : "bg-success text-success-foreground";
}

export function AnalysisResultsTable({ predictions = [] }: AnalysisResultsTableProps) {
  return (
    <div className="w-full">
      <h3 className="mb-1 text-lg font-semibold text-foreground">All AI Analysis Results</h3>
      <p className="mb-4 text-sm text-muted-foreground">
        Every analysed network flow, including benign and intrusion classifications.
      </p>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              {['Timestamp', 'Source IP', 'Classification', 'Method', 'Reason', 'Status', 'Severity'].map((heading) => (
                <th key={heading} className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">{heading}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {predictions.length ? predictions.map((item, index) => {
              const sourceIp = item.Source_IP || item["Src IP"] || item["Source IP"] || "N/A";
              const status = item.Traffic_Status || "N/A";
              return (
                <tr key={item.Alert_ID ?? index} className={cn("border-b border-border/50 transition-colors hover:bg-secondary/30", "animate-fade-in")} style={{ animationDelay: `${index * 60}ms` }}>
                  <td className="px-4 py-3 text-sm font-mono text-foreground">{item.Timestamp || "N/A"}</td>
                  <td className="px-4 py-3 text-sm font-mono font-semibold text-foreground">{sourceIp}</td>
                  <td className="px-4 py-3 text-sm text-foreground">{item.Predicted_Intrusion_Type}</td>
                  <td className="px-4 py-3 text-sm text-foreground">{item.Detection_Method}</td>
                  <td className="max-w-[340px] px-4 py-3 text-sm text-muted-foreground">{item.Reason}</td>
                  <td className="px-4 py-3"><Badge className={cn("text-xs font-medium", statusClass(status))}>{status}</Badge></td>
                  <td className="px-4 py-3 text-sm text-foreground">{item.Severity || "N/A"}</td>
                </tr>
              );
            }) : (
              <tr><td colSpan={7} className="px-4 py-6 text-center text-muted-foreground">Upload a CSV or run a live capture to see AI analysis results.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
