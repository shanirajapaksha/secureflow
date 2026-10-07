import { NavLink } from "@/components/NavLink";
import { LayoutDashboard, Activity, AlertTriangle, Radio, Settings, Shield, History, Flame, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

const navItems = [
  { title: "Dashboard", href: "/", icon: LayoutDashboard },
  { title: "Network Traffic", href: "/network-traffic", icon: Activity },
  { title: "Real-Time Capture", href: "/realtime", icon: Radio },
  { title: "Threat Alerts", href: "/threat-alerts", icon: AlertTriangle },
  { title: "Analysis History", href: "/history", icon: History },
  { title: "Firewall", href: "/firewall", icon: Flame },
  { title: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const { user, logout } = useAuth();
  return (
    <aside className="w-56 min-h-screen bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
            <Shield className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground">NIDS</h1>
            <p className="text-xs text-muted-foreground">Dashboard</p>
          </div>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.href}>
              <NavLink
                to={item.href}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium",
                  "text-sidebar-foreground hover:text-foreground",
                  "hover:bg-sidebar-accent transition-all duration-200"
                )}
                activeClassName="bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground"
              >
                <item.icon className="w-5 h-5" />
                <span>{item.title}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      
      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="mb-3 flex items-center justify-between text-xs text-muted-foreground"><span>{user?.username}</span><button onClick={logout} className="flex items-center gap-1 hover:text-foreground"><LogOut className="w-3 h-3" />Logout</button></div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
          <span>System Online</span>
        </div>
      </div>
    </aside>
  );
}
