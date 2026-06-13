import { Outlet, NavLink, Link } from "react-router";
import {
  LayoutDashboard,
  Shield,
  Activity,
  Network,
  Cpu,
  LineChart,
  Code2,
  GitBranch,
  Settings,
  Bell,
  Search,
  ChevronDown,
  User
} from "lucide-react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { ThemeToggle } from "./ThemeToggle";
import { useTheme } from "../context/ThemeContext";

const navItems = [
  { path: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { path: "/dashboard/fraud-prediction", label: "Fraud Prediction", icon: Shield },
  { path: "/dashboard/transactions", label: "Transaction Risk", icon: Activity },
  { path: "/dashboard/mule-graph", label: "Mule Network", icon: Network },
  { path: "/dashboard/model-engine", label: "Model Engine", icon: Cpu },
  { path: "/dashboard/monitoring", label: "Model Monitoring", icon: LineChart },
  { path: "/dashboard/api", label: "API Console", icon: Code2 },
  { path: "/dashboard/cicd", label: "CI/CD Pipeline", icon: GitBranch },
  { path: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function DashboardLayout() {
  const { isDark } = useTheme();

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Sidebar */}
      <aside
        className="fixed left-0 top-0 bottom-0 w-64 flex flex-col"
        style={{
          background: "var(--sidebar)",
          borderRight: "1px solid var(--frix-border)",
        }}
      >
        {/* Logo */}
        <Link
          to="/"
          className="h-16 flex items-center gap-2 px-6 hover:opacity-80 transition-opacity"
          style={{ borderBottom: "1px solid var(--frix-border)" }}
        >
          <div className="w-8 h-8 bg-gradient-to-br from-[#00D4FF] to-[#0099CC] rounded-md flex items-center justify-center flex-shrink-0">
            <Shield className="w-5 h-5 text-black" />
          </div>
          <span className="text-lg font-bold tracking-tight">FRIX</span>
        </Link>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-6 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/dashboard"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all text-sm ${
                  isActive
                    ? "bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/30 shadow-[0_0_15px_rgba(0,212,255,0.15)]"
                    : "text-muted-foreground hover:text-foreground"
                }`
              }
              style={({ isActive }) =>
                isActive ? {} : { ":hover": { background: "var(--frix-surface-2)" } }
              }
            >
              {({ isActive }) => (
                <>
                  <item.icon className="w-4 h-4 flex-shrink-0" />
                  <span className="font-medium">{item.label}</span>
                  {isActive && (
                    <div className="ml-auto w-1.5 h-1.5 bg-[#00D4FF] rounded-full shadow-[0_0_8px_rgba(0,212,255,0.8)]" />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Bottom user card */}
        <div className="p-4" style={{ borderTop: "1px solid var(--frix-border)" }}>
          <div
            className="flex items-center gap-3 px-3 py-2 rounded-lg"
            style={{ background: "var(--frix-surface-2)" }}
          >
            <div className="w-8 h-8 bg-gradient-to-br from-[#00D4FF] to-[#0099CC] rounded-full flex items-center justify-center flex-shrink-0">
              <User className="w-4 h-4 text-black" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">Admin User</div>
              <div className="text-xs text-muted-foreground">admin@frix.io</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="ml-64 flex flex-col min-h-screen">
        {/* Top Bar */}
        <header
          className="h-16 sticky top-0 z-40 backdrop-blur-xl"
          style={{
            background: isDark ? "rgba(15,15,18,0.85)" : "rgba(248,248,250,0.85)",
            borderBottom: "1px solid var(--frix-border)",
          }}
        >
          <div className="h-full px-8 flex items-center justify-between">
            {/* Search */}
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search transactions, accounts..."
                  className="pl-10 rounded-lg focus:border-[#00D4FF]/50 focus:ring-2 focus:ring-[#00D4FF]/20"
                />
              </div>
            </div>

            {/* Right actions */}
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                className="rounded-lg text-sm"
              >
                Production
                <ChevronDown className="w-4 h-4 ml-2" />
              </Button>

              <Button variant="ghost" size="icon" className="relative rounded-lg">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#FF2D55] rounded-full" />
              </Button>

              {/* Theme toggle */}
              <ThemeToggle />

              <div className="w-9 h-9 bg-gradient-to-br from-[#00D4FF] to-[#0099CC] rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-black" />
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
