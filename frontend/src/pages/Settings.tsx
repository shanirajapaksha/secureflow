import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Bell, Shield, Database, Server, BrainCircuit, ScanSearch } from "lucide-react";

const Settings = () => {
  return (
    <DashboardLayout>
      <div className="p-8 max-w-5xl">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-foreground glow-text">System Settings</h1>
          <p className="text-muted-foreground mt-1">Reference configuration for your hybrid NIDS project</p>
        </header>

        <section className="bg-card border border-border rounded-lg p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <Server className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold text-foreground">Backend API</h2>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label className="text-foreground">Prediction Endpoint</Label>
              <Input value="http://127.0.0.1:8000/predict" readOnly className="mt-2 bg-secondary border-border" />
            </div>
            <div>
              <Label className="text-foreground">Health Endpoint</Label>
              <Input value="http://127.0.0.1:8000/health" readOnly className="mt-2 bg-secondary border-border" />
            </div>
          </div>
        </section>

        <section className="bg-card border border-border rounded-lg p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <Shield className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold text-foreground">Detection Layers</h2>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border border-border bg-secondary/40 p-4">
              <div className="mb-3 flex items-center gap-2">
                <ScanSearch className="w-4 h-4 text-primary" />
                <h3 className="font-medium text-foreground">Signature-Based</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Checks for known rules such as SYN flood, DoS/DDoS patterns, FTP brute-force behavior, and suspicious traffic rates.
              </p>
            </div>
            <div className="rounded-lg border border-border bg-secondary/40 p-4">
              <div className="mb-3 flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-primary" />
                <h3 className="font-medium text-foreground">Anomaly-Based ML</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Uses the trained model and preprocessing artifacts to classify traffic as benign or intrusion when no signature rule is matched.
              </p>
            </div>
          </div>
        </section>

        <section className="bg-card border border-border rounded-lg p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <Bell className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold text-foreground">Dashboard Output</h2>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label className="text-foreground">CSV Input</Label>
              <Input value="Upload network traffic CSV from dashboard" readOnly className="mt-2 bg-secondary border-border" />
            </div>
            <div>
              <Label className="text-foreground">Displayed Outputs</Label>
              <Input value="Summary cards, attack chart, traffic overview, threat table" readOnly className="mt-2 bg-secondary border-border" />
            </div>
          </div>
        </section>

        <section className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-6">
            <Database className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold text-foreground">Returned Fields</h2>
          </div>
          <div className="rounded-lg border border-border bg-secondary/40 p-4 text-sm text-muted-foreground leading-7">
            Detection_Method, Predicted_Intrusion_Type, Traffic_Status, Reason, summary.total_rows, summary.benign_count,
            summary.intrusion_count, summary.signature_count, summary.anomaly_count, and optional evaluation accuracy.
          </div>
        </section>
      </div>
    </DashboardLayout>
  );
};

export default Settings;
