import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
export default function ProtectedRoute() { return useAuth().isAuthenticated ? <Outlet /> : <Navigate to="/auth" replace />; }
