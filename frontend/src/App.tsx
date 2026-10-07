import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { DataProvider } from "@/context/DataContext";
import Dashboard from "./pages/Dashboard";
import NetworkTraffic from "./pages/NetworkTraffic";
import ThreatAlerts from "./pages/ThreatAlerts";
import Settings from "./pages/Settings";
import RealtimeCapture from "./pages/RealtimeCapture";
import NotFound from "./pages/NotFound";
import History from "./pages/History";
import Firewall from "./pages/Firewall";
import AuthPage from "./pages/AuthPage";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
    <AuthProvider>
    <DataProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
          <Routes>
            <Route path="/auth" element={<AuthPage />} />
            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/network-traffic" element={<NetworkTraffic />} />
              <Route path="/realtime" element={<RealtimeCapture />} />
              <Route path="/threat-alerts" element={<ThreatAlerts />} />
              <Route path="/history" element={<History />} />
              <Route path="/firewall" element={<Firewall />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
      </TooltipProvider>
    </DataProvider>
    </AuthProvider>
    </BrowserRouter>
  </QueryClientProvider>
);

export default App;
