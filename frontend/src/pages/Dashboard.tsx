import { useState } from "react";
import { Shield, AlertTriangle, Activity, Upload, Loader, Check, AlertCircle, ScanSearch, BrainCircuit } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StatCard } from "@/components/dashboard/StatCard";
import { NetworkTrafficChart } from "@/components/dashboard/NetworkTrafficChart";
import { AttackTypesChart } from "@/components/dashboard/AttackTypesChart";
import { AnalysisResultsTable } from "@/components/dashboard/AnalysisResultsTable";
import { SourceIpOverview } from "@/components/dashboard/SourceIpOverview";
import { Button } from "@/components/ui/button";
import { uploadCsvForPrediction } from "@/lib/api";
import { useDataContext } from "@/context/DataContext";
import { getAttackTypeSummary, getSummaryCounts, getThreatPercentage } from "@/lib/nids";

const Dashboard = () => {
  const { result, setResult, loading, setLoading, error, setError } = useDataContext();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      const data = await uploadCsvForPrediction(selectedFile);
      setResult(data);
      setSelectedFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process file");
    } finally {
      setLoading(false);
    }
  };

  const { totalRows, benignCount, intrusionCount, signatureCount, anomalyCount } = getSummaryCounts(result);
  const threatPercentage = getThreatPercentage(result);
  const attackSummary = getAttackTypeSummary(result?.predictions ?? []);

  return (
    <DashboardLayout>
      <div className="p-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-foreground glow-text">Hybrid NIDS Dashboard</h1>
          <p className="text-muted-foreground mt-1">Signature-based + anomaly-based intrusion detection</p>
        </header>

        <div className="bg-card border border-border rounded-lg p-6 mb-8">
          <div className="flex items-center gap-4 flex-wrap">
            <label className="flex-1 min-w-[250px]">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                disabled={loading}
                className="hidden"
              />
              <div className="cursor-pointer flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition disabled:opacity-50 disabled:cursor-not-allowed w-fit">
                {loading ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Upload CSV File
                  </>
                )}
              </div>
            </label>
            <span className="text-sm text-muted-foreground">Upload a CSV file to run hybrid intrusion detection</span>
          </div>

          {selectedFile && (
            <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500 rounded text-blue-600 text-sm flex items-center gap-2">
              <Check className="w-4 h-4" />
              Selected: {selectedFile.name}
              <Button onClick={handleUpload} disabled={loading} size="sm" className="ml-auto">
                {loading ? "Processing..." : "Analyze"}
              </Button>
            </div>
          )}

          {error && (
            <div className="mt-4 p-3 bg-destructive/10 border border-destructive rounded text-destructive text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}

          {totalRows > 0 && (
            <div className="mt-4 space-y-3">
              <div className="p-3 bg-green-500/10 border border-green-500 rounded text-green-600 text-sm flex items-center gap-2">
                <Check className="w-4 h-4" />
                Successfully processed {totalRows.toLocaleString()} rows
              </div>

              {result?.evaluation && (
                <div className="p-3 bg-primary/10 border border-primary/40 rounded text-sm text-foreground">
                  Accuracy: <span className="font-semibold">{(result.evaluation.accuracy * 100).toFixed(2)}%</span>
                  <span className="text-muted-foreground"> using label column "{result.evaluation.label_column}"</span>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-6 mb-8">
          <StatCard title="Total Rows Scanned" value={totalRows} icon={Shield} />
          <StatCard title="Detected Intrusions" value={intrusionCount} icon={AlertTriangle} trend={{ value: threatPercentage, isPositive: false }} />
          <StatCard title="Benign Traffic" value={benignCount} icon={Activity} />
          <StatCard title="Signature Detections" value={signatureCount} icon={ScanSearch} />
          <StatCard title="ML / Anomaly Checks" value={anomalyCount} icon={BrainCircuit} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-card border border-border rounded-lg p-6 animate-fade-in" style={{ animationDelay: "200ms" }}>
            <NetworkTrafficChart benignCount={benignCount} intrusionCount={intrusionCount} />
          </div>
          <div className="bg-card border border-border rounded-lg p-6 animate-fade-in" style={{ animationDelay: "300ms" }}>
            <AttackTypesChart summary={attackSummary} />
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6 mb-8 animate-fade-in" style={{ animationDelay: "400ms" }}>
          <SourceIpOverview predictions={result?.predictions ?? []} />
        </div>

        <div className="bg-card border border-border rounded-lg p-6 animate-fade-in" style={{ animationDelay: "500ms" }}>
          <AnalysisResultsTable predictions={result?.predictions ?? []} />
        </div>

      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
