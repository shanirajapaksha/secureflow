import { PredictionRow } from "@/lib/api";

interface SourceIpOverviewProps {
  predictions?: PredictionRow[];
}

export function SourceIpOverview({ predictions = [] }: SourceIpOverviewProps) {
  const sources = predictions.reduce<Record<string, number>>((counts, row) => {
    if (row.Traffic_Status !== "INTRUSION") return counts;
    const ip = row.Source_IP || row["Src IP"] || row["Source IP"] || "Unknown";
    counts[ip] = (counts[ip] || 0) + 1;
    return counts;
  }, {});
  const entries = Object.entries(sources).sort(([, a], [, b]) => b - a).slice(0, 8);

  return (
    <div className="w-full">
      <h3 className="mb-1 text-lg font-semibold text-foreground">Suspicious Source IP Overview</h3>
      <p className="mb-4 text-sm text-muted-foreground">Actual source IP addresses from the current intrusion results. Geo-location data is not inferred.</p>
      {entries.length ? (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {entries.map(([ip, count]) => (
            <div key={ip} className="rounded-lg border border-border bg-secondary/30 p-4">
              <p className="font-mono text-sm font-semibold text-foreground">{ip}</p>
              <p className="mt-1 text-sm text-muted-foreground">{count} intrusion flow{count === 1 ? "" : "s"}</p>
            </div>
          ))}
        </div>
      ) : <div className="rounded-lg border border-border bg-secondary/30 p-5 text-sm text-muted-foreground">No suspicious source IP addresses detected.</div>}
    </div>
  );
}
