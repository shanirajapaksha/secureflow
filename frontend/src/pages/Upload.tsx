import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Upload, Loader, Check, AlertCircle } from "lucide-react";
import { useState } from "react";
import { uploadCsvForPrediction } from "@/lib/api";
import { useDataContext } from "@/context/DataContext";

const UploadPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { setResult, loading, setLoading, error, setError } = useDataContext();

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

  return (
    <DashboardLayout>
      <div className="p-8">
        <header className="mb-12">
          <h1 className="text-4xl font-bold text-foreground glow-text">Upload CSV File</h1>
          <p className="text-muted-foreground mt-2">
            Upload network traffic data for analysis and detection
          </p>
        </header>

        <div className="max-w-2xl">
          {/* Upload Card */}
          <div className="bg-card border border-border rounded-lg p-8 mb-6">
            <div className="flex flex-col items-center justify-center py-8">
              <div className="w-24 h-24 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <Upload className="w-12 h-12 text-primary" />
              </div>

              <h2 className="text-2xl font-semibold text-foreground mb-2">
                Select CSV File
              </h2>
              <p className="text-muted-foreground mb-6 text-center">
                Choose a CSV file containing network traffic data
              </p>

              <label className="mb-6">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileSelect}
                  disabled={loading}
                  className="hidden"
                />
                <div className="cursor-pointer px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium">
                  Choose File
                </div>
              </label>

              {selectedFile && (
                <div className="w-full bg-green-500/10 border border-green-500 rounded-lg p-4 mb-6 flex items-center gap-3">
                  <Check className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="text-green-600 font-medium">File Selected</p>
                    <p className="text-green-600/80 text-sm">{selectedFile.name}</p>
                  </div>
                </div>
              )}

              {error && (
                <div className="w-full bg-destructive/10 border border-destructive rounded-lg p-4 mb-6 flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-destructive" />
                  <div>
                    <p className="text-destructive font-medium">Error</p>
                    <p className="text-destructive/80 text-sm">{error}</p>
                  </div>
                </div>
              )}

              <Button
                onClick={handleUpload}
                disabled={!selectedFile || loading}
                size="lg"
                className="w-full sm:w-auto"
              >
                {loading ? (
                  <>
                    <Loader className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Upload & Analyze
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Info Section */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">
              🔍 Expected CSV Format
            </h3>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>
                Your CSV file should contain network traffic features with columns like:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-2">
                <li>Destination Port, Protocol, Flow Duration</li>
                <li>Total Fwd Packets, Total Bwd Packets</li>
                <li>Total Length of Fwd Packets, Total Length of Bwd Packets</li>
                <li>And other network traffic metrics</li>
              </ul>
              <p className="mt-4 pt-4 border-t border-border">
                ✓ The system will automatically preprocess and analyze your data
              </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default UploadPage;
