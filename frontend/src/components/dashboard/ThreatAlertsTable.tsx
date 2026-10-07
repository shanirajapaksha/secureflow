import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { PredictionRow } from "@/lib/api";

interface ThreatAlertsTableProps {
  predictions?: PredictionRow[];
}

function getSeverityFromLabel(label: string): "high" | "medium" | "low" | "review" {
  const highLabels = ["DDoS", "DoS", "Heartbleed", "Infiltration", "Bot"];
  const mediumLabels = ["PortScan", "Web Attack", "Brute", "FTP", "Signature_Detected_Attack"];

  if (highLabels.some((item) => label.includes(item))) return "high";
  if (mediumLabels.some((item) => label.includes(item))) return "medium";
  if (label === "BENIGN") return "low";
  return "review";
}

function normalizeSeverity(
  backendSeverity?: string,
  label?: string
): "high" | "medium" | "low" | "review" {
  if (backendSeverity) {
    const value = backendSeverity.toLowerCase();
    if (value === "high") return "high";
    if (value === "medium") return "medium";
    if (value === "low") return "low";
    return "review";
  }

  return getSeverityFromLabel(label || "");
}

const severityConfig = {
  high: { label: "High", className: "bg-destructive text-destructive-foreground" },
  medium: { label: "Medium", className: "bg-warning text-warning-foreground" },
  low: { label: "Low", className: "bg-success text-success-foreground" },
  review: { label: "Review", className: "bg-info text-info-foreground" },
};

export function ThreatAlertsTable({ predictions = [] }: ThreatAlertsTableProps) {
  const attackRows = predictions
    .filter((item) => item.Traffic_Status === "INTRUSION")
    .slice(0, 15)
    .map((item, index) => ({
      id: String(item.Alert_ID ?? index + 1),
      timestamp:
        item.Timestamp && item.Timestamp !== "None"
          ? item.Timestamp
          : new Date().toLocaleTimeString(),
      type: item.Predicted_Intrusion_Type,
      severity: normalizeSeverity(item.Severity, item.Predicted_Intrusion_Type),
      method: item.Detection_Method,
      reason: item.Reason,
      sourceIp: (item.Source_IP || item["Src IP"] || item["Source IP"] || "N/A") as string,
    }));

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-foreground mb-4">Threat Alerts</h3>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                Timestamp
              </th>
              <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                Intrusion Type
              </th>
              <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                Method
              </th>
              <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                Reason
              </th>
              <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                Source IP
              </th>
              <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                Severity
              </th>
            </tr>
          </thead>

          <tbody>
            {attackRows.length > 0 ? (
              attackRows.map((alert, index) => (
                <tr
                  key={alert.id}
                  className={cn(
                    "border-b border-border/50 transition-colors hover:bg-secondary/30",
                    "animate-fade-in"
                  )}
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <td className="py-3 px-4 text-sm font-mono text-foreground">
                    {alert.timestamp}
                  </td>
                  <td className="py-3 px-4 text-sm text-foreground">
                    {alert.type}
                  </td>
                  <td className="py-3 px-4 text-sm text-foreground">
                    {alert.method}
                  </td>
                  <td className="py-3 px-4 text-sm text-muted-foreground max-w-[340px]">
                    {alert.reason}
                  </td>
                  <td className="py-3 px-4 text-sm font-mono text-foreground">
                    {alert.sourceIp}
                  </td>
                  <td className="py-3 px-4">
                    <Badge
                      className={cn(
                        "text-xs font-medium",
                        severityConfig[alert.severity].className
                      )}
                    >
                      {severityConfig[alert.severity].label}
                    </Badge>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="py-6 px-4 text-center text-muted-foreground">
                  No intrusion alerts yet. Upload a CSV to see hybrid detection results.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}