import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Loader2,
  Play,
  Radio,
  RefreshCw,
  Square,
  Wifi,
  XCircle,
} from "lucide-react";

import { AttackTypesChart } from "@/components/dashboard/AttackTypesChart";
import { NetworkTrafficChart } from "@/components/dashboard/NetworkTrafficChart";
import { StatCard } from "@/components/dashboard/StatCard";
import { ThreatAlertsTable } from "@/components/dashboard/ThreatAlertsTable";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { useDataContext } from "@/context/DataContext";
import {
  CaptureInterface,
  ConverterStatus,
  PredictionRow,
  RealtimeStatus,
  captureAndAnalyze,
  getCaptureInterfaces,
  getConverterStatus,
  getRealtimeAlerts,
  getRealtimeStatus,
  startRealtimeCapture,
  stopRealtimeCapture,
} from "@/lib/api";
import { getAttackTypeSummary, getSummaryCounts } from "@/lib/nids";

const emptyStatus: RealtimeStatus = {
  running: false,
  interface: null,
  capture_file: null,
  started_at: null,
  stopped_at: null,
  last_error: null,
  recent_alert_count: 0,
  monitoring: false,
  processing: false,
};

function alertsToResponse(alerts: PredictionRow[]) {
  const benignCount = alerts.filter((row) => row.Traffic_Status === "BENIGN").length;
  const signatureCount = alerts.filter((row) => row.Detection_Method === "Signature-Based").length;
  return {
    summary: {
      total_rows: alerts.length,
      benign_count: benignCount,
      intrusion_count: alerts.length - benignCount,
      signature_count: signatureCount,
      anomaly_count: alerts.length - signatureCount,
    },
    evaluation: null,
    predictions: alerts,
  };
}

function preferredInterface(interfaces: CaptureInterface[]) {
  return (
    interfaces.find((item) => /\(Wi-Fi\)/i.test(item.name)) ||
    interfaces.find((item) => /\(Ethernet\)/i.test(item.name)) ||
    interfaces[0]
  );
}

const RealtimeCapture = () => {
  const { result, setResult } = useDataContext();
  const [interfaces, setInterfaces] = useState<CaptureInterface[]>([]);
  const [selectedInterface, setSelectedInterface] = useState("");
  const [duration, setDuration] = useState(10);
  const [status, setStatus] = useState<RealtimeStatus>(emptyStatus);
  const [converter, setConverter] = useState<ConverterStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [loadingSetup, setLoadingSetup] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshSetup = useCallback(async () => {
    setLoadingSetup(true);
    setError(null);
    try {
      const [available, converterState, captureState] = await Promise.all([
        getCaptureInterfaces(),
        getConverterStatus(),
        getRealtimeStatus(),
      ]);
      setInterfaces(available);
      setConverter(converterState);
      setStatus(captureState);
      setSelectedInterface((current) =>
        available.some((item) => item.id === current)
          ? current
          : preferredInterface(available)?.id || "",
      );
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to load capture setup");
    } finally {
      setLoadingSetup(false);
    }
  }, []);

  useEffect(() => {
    void refreshSetup();
  }, [refreshSetup]);

  useEffect(() => {
    const timer = window.setInterval(async () => {
      try {
        const [captureState, alertState] = await Promise.all([
          getRealtimeStatus(),
          getRealtimeAlerts(),
        ]);
        setStatus(captureState);
        if (alertState.count > 0) {
          setResult(alertsToResponse(alertState.alerts));
        }
      } catch {
        // The visible action error remains more useful than transient polling errors.
      }
    }, 2000);
    return () => window.clearInterval(timer);
  }, [setResult]);

  const runAction = async (action: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try {
      await action();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Real-time capture failed");
    } finally {
      setBusy(false);
      try {
        setStatus(await getRealtimeStatus());
      } catch {
        // Preserve the original action result.
      }
    }
  };

  const quickCapture = () =>
    runAction(async () => {
      const response = await captureAndAnalyze(selectedInterface, duration);
      setResult(response);
    });

  const startCapture = () =>
    runAction(async () => {
      setStatus(await startRealtimeCapture(selectedInterface, Math.max(2, duration)));
    });

  const stopAndAnalyze = () =>
    runAction(async () => {
      await stopRealtimeCapture();
      const alertState = await getRealtimeAlerts();
      if (alertState.count > 0) setResult(alertsToResponse(alertState.alerts));
    });

  const { totalRows, benignCount, intrusionCount } = getSummaryCounts(result);
  const attackSummary = getAttackTypeSummary(result?.predictions ?? []);
  const captureReady = Boolean(selectedInterface && converter?.configured && !busy && !status.running);

  return (
    <DashboardLayout>
      <div className="p-8">
        <header className="mb-8 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground glow-text">Real-Time Packet Capture</h1>
            <p className="mt-1 text-muted-foreground">Wireshark/TShark capture → CICFlowMeter → Hybrid NIDS</p>
          </div>
          <Button variant="outline" onClick={() => void refreshSetup()} disabled={loadingSetup || busy}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loadingSetup ? "animate-spin" : ""}`} />
            Refresh setup
          </Button>
        </header>

        <div className="mb-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-border bg-card p-4">
            <div className="mb-2 flex items-center gap-2 text-sm font-medium"><Wifi className="h-4 w-4" /> TShark interfaces</div>
            <div className="text-2xl font-bold">{interfaces.length}</div>
            <div className="text-xs text-muted-foreground">{interfaces.length ? "Capture service available" : "No interfaces detected"}</div>
          </div>
          <div className="rounded-lg border border-border bg-card p-4">
            <div className="mb-2 flex items-center gap-2 text-sm font-medium">
              {converter?.configured ? <CheckCircle2 className="h-4 w-4 text-success" /> : <XCircle className="h-4 w-4 text-destructive" />}
              CICFlowMeter
            </div>
            <div className="text-2xl font-bold">{converter?.configured ? "Ready" : "Not ready"}</div>
            <div className="truncate text-xs text-muted-foreground">{converter?.hint || "Bundled converter detected"}</div>
          </div>
          <div className="rounded-lg border border-border bg-card p-4">
            <div className="mb-2 flex items-center gap-2 text-sm font-medium"><Radio className={`h-4 w-4 ${status.running ? "animate-pulse text-destructive" : ""}`} /> Capture status</div>
            <div className="text-2xl font-bold">{status.processing ? "Analyzing" : status.running ? "Monitoring" : busy ? "Processing" : "Idle"}</div>
            <div className="truncate text-xs text-muted-foreground">{status.capture_file || "No active capture"}</div>
          </div>
        </div>

        <section className="mb-8 rounded-lg border border-border bg-card p-6">
          <div className="grid gap-5 lg:grid-cols-[1fr_180px_auto] lg:items-end">
            <label className="space-y-2">
              <span className="text-sm font-medium text-foreground">Network interface</span>
              <select
                value={selectedInterface}
                onChange={(event) => setSelectedInterface(event.target.value)}
                disabled={status.running || busy}
                className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
              >
                {interfaces.map((item) => <option key={item.id} value={item.id}>{item.id}. {item.name}</option>)}
              </select>
            </label>
            <label className="space-y-2">
              <span className="text-sm font-medium text-foreground">Capture/window duration (seconds)</span>
              <input
                type="number"
                min={2}
                max={300}
                value={duration}
                onChange={(event) => setDuration(Math.max(2, Math.min(300, Number(event.target.value) || 2)))}
                disabled={status.running || busy}
                className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
              />
            </label>
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => void quickCapture()} disabled={!captureReady}>
                {busy && !status.running ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Activity className="mr-2 h-4 w-4" />}
                Capture & Analyze
              </Button>
              {!status.running ? (
                <Button variant="outline" onClick={() => void startCapture()} disabled={!captureReady}>
                  <Play className="mr-2 h-4 w-4" /> Start
                </Button>
              ) : (
                <Button variant="destructive" onClick={() => void stopAndAnalyze()} disabled={busy}>
                  <Square className="mr-2 h-4 w-4" /> Stop Monitoring
                </Button>
              )}
            </div>
          </div>

          {error && <div className="mt-4 flex items-center gap-2 rounded-md border border-destructive bg-destructive/10 p-3 text-sm text-destructive"><AlertCircle className="h-4 w-4" />{error}</div>}
          {status.last_error && <div className="mt-4 text-sm text-destructive">Capture error: {status.last_error}</div>}
        </section>

        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3">
          <StatCard title="Flows Analyzed" value={totalRows} icon={Activity} />
          <StatCard title="Intrusions" value={intrusionCount} icon={AlertCircle} />
          <StatCard title="Benign Flows" value={benignCount} icon={CheckCircle2} />
        </div>

        <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="rounded-lg border border-border bg-card p-6"><NetworkTrafficChart benignCount={benignCount} intrusionCount={intrusionCount} /></div>
          <div className="rounded-lg border border-border bg-card p-6"><AttackTypesChart summary={attackSummary} /></div>
        </div>
        <div className="rounded-lg border border-border bg-card p-6"><ThreatAlertsTable predictions={result?.predictions ?? []} /></div>
      </div>
    </DashboardLayout>
  );
};

export default RealtimeCapture;
