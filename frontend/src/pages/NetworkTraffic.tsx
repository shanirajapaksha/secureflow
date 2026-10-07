import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StatCard } from "@/components/dashboard/StatCard";
import { NetworkTrafficChart } from "@/components/dashboard/NetworkTrafficChart";
import { AttackTypesChart } from "@/components/dashboard/AttackTypesChart";
import { ThreatAlertsTable } from "@/components/dashboard/ThreatAlertsTable";
import { GeographicMap } from "@/components/dashboard/GeographicMap";
import { Shield, AlertTriangle, Activity, ScanSearch, BrainCircuit } from "lucide-react";
import { useDataContext } from "@/context/DataContext";
import { getAttackTypeSummary, getSummaryCounts } from "@/lib/nids";

const NetworkTrafficPage = () => {
  const { result } = useDataContext();
  const { totalRows, intrusionCount, benignCount, signatureCount, anomalyCount } = getSummaryCounts(result);
  const attackSummary = getAttackTypeSummary(result?.predictions ?? []);

  return (
    <DashboardLayout>
      <div className="p-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-foreground glow-text">Network Traffic</h1>
          <p className="text-muted-foreground mt-1">Traffic distribution and hybrid detection results</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-6 mb-8">
          <StatCard title="Total Rows Scanned" value={totalRows} icon={Shield} />
          <StatCard title="Detected Intrusions" value={intrusionCount} icon={AlertTriangle} />
          <StatCard title="Benign Traffic" value={benignCount} icon={Activity} />
          <StatCard title="Signature Detections" value={signatureCount} icon={ScanSearch} />
          <StatCard title="ML / Anomaly Checks" value={anomalyCount} icon={BrainCircuit} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-card border border-border rounded-lg p-6 animate-fade-in">
            <NetworkTrafficChart benignCount={benignCount} intrusionCount={intrusionCount} />
          </div>
          <div className="bg-card border border-border rounded-lg p-6 animate-fade-in">
            <AttackTypesChart summary={attackSummary} />
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6 mb-8 animate-fade-in">
          <GeographicMap />
        </div>

        <div className="bg-card border border-border rounded-lg p-6 animate-fade-in">
          <ThreatAlertsTable predictions={result?.predictions ?? []} />
        </div>
      </div>
    </DashboardLayout>
  );
};

export default NetworkTrafficPage;
