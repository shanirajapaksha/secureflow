import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ThreatAlertsTable } from "@/components/dashboard/ThreatAlertsTable";
import { StatCard } from "@/components/dashboard/StatCard";
import { AlertTriangle, ShieldAlert, ShieldCheck, ScanSearch, BrainCircuit } from "lucide-react";
import { useDataContext } from "@/context/DataContext";
import { getAttackTypeSummary, getSummaryCounts } from "@/lib/nids";

const ThreatAlerts = () => {
  const { result } = useDataContext();
  const { intrusionCount, benignCount, signatureCount, anomalyCount } = getSummaryCounts(result);
  const distinctThreats = Object.keys(getAttackTypeSummary(result?.predictions ?? [])).length;

  return (
    <DashboardLayout>
      <div className="p-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-foreground glow-text">Threat Alerts</h1>
          <p className="text-muted-foreground mt-1">Signature alerts and anomaly detections</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-6 mb-8">
          <StatCard title="Total Intrusions" value={intrusionCount} icon={ShieldAlert} className="border-destructive/50" />
          <StatCard title="Threat Types" value={distinctThreats} icon={AlertTriangle} />
          <StatCard title="Benign Rows" value={benignCount} icon={ShieldCheck} />
          <StatCard title="Signature-Based" value={signatureCount} icon={ScanSearch} />
          <StatCard title="Anomaly-Based" value={anomalyCount} icon={BrainCircuit} />
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <ThreatAlertsTable predictions={result?.predictions ?? []} />
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ThreatAlerts;
