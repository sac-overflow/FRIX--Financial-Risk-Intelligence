import { motion } from "motion/react";
import { AlertTriangle, Activity, Cpu, TrendingUp, TrendingDown, Clock, Zap } from "lucide-react";
import { Card } from "../components/ui/card";
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";

const driftData = [
  { day: "Jun 4", score: 0.02, threshold: 0.05 },
  { day: "Jun 5", score: 0.03, threshold: 0.05 },
  { day: "Jun 6", score: 0.04, threshold: 0.05 },
  { day: "Jun 7", score: 0.06, threshold: 0.05 },
  { day: "Jun 8", score: 0.05, threshold: 0.05 },
  { day: "Jun 9", score: 0.07, threshold: 0.05 },
  { day: "Jun 10", score: 0.04, threshold: 0.05 },
];

const latencyData = [
  { time: "00:00", p50: 12, p95: 28, p99: 45 },
  { time: "04:00", p50: 11, p95: 25, p99: 40 },
  { time: "08:00", p50: 18, p95: 42, p99: 78 },
  { time: "12:00", p50: 22, p95: 55, p99: 102 },
  { time: "16:00", p50: 19, p95: 48, p99: 89 },
  { time: "20:00", p50: 14, p95: 32, p99: 58 },
];

const accuracyData = [
  { day: "Jun 4", precision: 99.8, recall: 97.2, f1: 98.5 },
  { day: "Jun 5", precision: 99.7, recall: 97.5, f1: 98.6 },
  { day: "Jun 6", precision: 99.6, recall: 96.8, f1: 98.2 },
  { day: "Jun 7", precision: 99.4, recall: 96.1, f1: 97.7 },
  { day: "Jun 8", precision: 99.5, recall: 96.4, f1: 97.9 },
  { day: "Jun 9", precision: 99.3, recall: 95.8, f1: 97.5 },
  { day: "Jun 10", precision: 99.7, recall: 97.1, f1: 98.4 },
];

const volumeData = [
  { hour: "00", volume: 1240 },
  { hour: "02", volume: 890 },
  { hour: "04", volume: 650 },
  { hour: "06", volume: 980 },
  { hour: "08", volume: 2340 },
  { hour: "10", volume: 3210 },
  { hour: "12", volume: 3890 },
  { hour: "14", volume: 3560 },
  { hour: "16", volume: 3120 },
  { hour: "18", volume: 2780 },
  { hour: "20", volume: 2100 },
  { hour: "22", volume: 1560 },
];

const alerts = [
  {
    id: "ALT-001",
    type: "Data Drift",
    model: "XGBoost Champion",
    severity: "high",
    message: "PSI score exceeded threshold (0.07 > 0.05) on feature velocity_7d",
    time: "12 min ago",
  },
  {
    id: "ALT-002",
    type: "Latency Spike",
    model: "Graph-Risk v2.1",
    severity: "medium",
    message: "P99 latency reached 142ms, above SLA of 100ms",
    time: "38 min ago",
  },
  {
    id: "ALT-003",
    type: "Accuracy Drop",
    model: "LightGBM Challenger",
    severity: "medium",
    message: "Recall dropped 1.4pp vs 7-day baseline",
    time: "2 hr ago",
  },
  {
    id: "ALT-004",
    type: "Volume Anomaly",
    model: "All Models",
    severity: "low",
    message: "Inference volume 23% above hourly average",
    time: "3 hr ago",
  },
];

const models = [
  { name: "XGBoost Champion", status: "healthy", accuracy: 99.7, latency: 18, drift: 0.04, uptime: "99.98%" },
  { name: "LightGBM Challenger", status: "degraded", accuracy: 98.2, latency: 24, drift: 0.07, uptime: "99.91%" },
  { name: "Graph-Risk v2.1", status: "warning", accuracy: 97.8, latency: 52, drift: 0.03, uptime: "99.85%" },
  { name: "Random Forest Shadow", status: "healthy", accuracy: 96.4, latency: 31, drift: 0.02, uptime: "100%" },
];

const tooltipStyle = {
  backgroundColor: "var(--card)",
  border: "1px solid var(--frix-border)",
  borderRadius: "8px",
  color: "var(--frix-text)",
};

export function ModelMonitoring() {
  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">Model Monitoring</h1>
          <p className="text-muted-foreground">MLOps observability — drift, latency, performance, and anomaly tracking</p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className="w-2 h-2 rounded-full bg-[#00D4FF] animate-pulse inline-block" />
          <span className="text-muted-foreground">Live · Updated 30s ago</span>
        </div>
      </div>

      {/* Model health grid */}
      <div className="grid grid-cols-4 gap-4">
        {models.map((model, i) => (
          <motion.div
            key={model.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: i * 0.08 }}
          >
            <Card
              className={`bg-card p-5 border ${
                model.status === "healthy"
                  ? "border-[#00D4FF]/20 hover:border-[#00D4FF]/40"
                  : model.status === "degraded"
                  ? "border-[#FF2D55]/30 shadow-[0_0_20px_rgba(255,45,85,0.12)]"
                  : "border-[#FBBF24]/30"
              } transition-all`}
            >
              <div className="flex items-center justify-between mb-3">
                <Cpu className="w-4 h-4 text-muted-foreground" />
                <span
                  className={`text-xs px-2 py-0.5 rounded border ${
                    model.status === "healthy"
                      ? "bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]/30"
                      : model.status === "degraded"
                      ? "bg-[#FF2D55]/10 text-[#FF2D55] border-[#FF2D55]/30"
                      : "bg-[#FBBF24]/10 text-[#FBBF24] border-[#FBBF24]/30"
                  }`}
                >
                  {model.status.toUpperCase()}
                </span>
              </div>
              <div className="text-sm font-semibold mb-3 leading-tight">{model.name}</div>
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Accuracy</span>
                  <span className={model.status === "degraded" ? "text-[#FF2D55]" : "text-foreground"}>
                    {model.accuracy}%
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Latency P50</span>
                  <span className={model.latency > 40 ? "text-[#FBBF24]" : "text-foreground"}>
                    {model.latency}ms
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Drift PSI</span>
                  <span className={model.drift > 0.05 ? "text-[#FF2D55]" : "text-[#00D4FF]"}>
                    {model.drift}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Uptime</span>
                  <span className="text-foreground">{model.uptime}</span>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Charts grid */}
      <div className="grid grid-cols-2 gap-6">
        {/* Data Drift */}
        <Card className="bg-card border-border p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-semibold mb-1">Data Drift (PSI)</h3>
              <p className="text-xs text-muted-foreground">Population Stability Index — threshold 0.05</p>
            </div>
            <AlertTriangle className="w-4 h-4 text-[#FF2D55]" />
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={driftData}>
              <defs>
                <linearGradient id="driftGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#FF2D55" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#FF2D55" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="day" stroke="var(--frix-muted-text)" style={{ fontSize: "11px" }} />
              <YAxis stroke="var(--frix-muted-text)" style={{ fontSize: "11px" }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Area type="monotone" dataKey="threshold" stroke="#FBBF24" strokeDasharray="4 4" fill="none" dot={false} />
              <Area type="monotone" dataKey="score" stroke="#FF2D55" fill="url(#driftGrad)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        {/* Inference Latency */}
        <Card className="bg-card border-border p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-semibold mb-1">Inference Latency</h3>
              <p className="text-xs text-muted-foreground">P50 / P95 / P99 percentiles (ms)</p>
            </div>
            <Clock className="w-4 h-4 text-[#00D4FF]" />
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={latencyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" stroke="var(--frix-muted-text)" style={{ fontSize: "11px" }} />
              <YAxis stroke="var(--frix-muted-text)" style={{ fontSize: "11px" }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="p50" stroke="#00D4FF" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="p95" stroke="#FBBF24" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="p99" stroke="#FF2D55" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
          <div className="flex items-center gap-6 mt-3">
            {[["P50", "#00D4FF"], ["P95", "#FBBF24"], ["P99", "#FF2D55"]].map(([label, color]) => (
              <div key={label} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <div className="w-6 h-0.5 rounded" style={{ backgroundColor: color }} />
                {label}
              </div>
            ))}
          </div>
        </Card>

        {/* Performance Trends */}
        <Card className="bg-card border-border p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-semibold mb-1">Performance Trends</h3>
              <p className="text-xs text-muted-foreground">Precision, Recall, F1 Score (%)</p>
            </div>
            <TrendingUp className="w-4 h-4 text-[#00D4FF]" />
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={accuracyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="day" stroke="var(--frix-muted-text)" style={{ fontSize: "11px" }} />
              <YAxis domain={[94, 100]} stroke="var(--frix-muted-text)" style={{ fontSize: "11px" }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="precision" stroke="#00D4FF" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="recall" stroke="#FBBF24" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="f1" stroke="#A78BFA" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Inference Volume */}
        <Card className="bg-card border-border p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-semibold mb-1">Inference Volume</h3>
              <p className="text-xs text-muted-foreground">Predictions per hour — today</p>
            </div>
            <Zap className="w-4 h-4 text-[#00D4FF]" />
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={volumeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="hour" stroke="var(--frix-muted-text)" style={{ fontSize: "11px" }} />
              <YAxis stroke="var(--frix-muted-text)" style={{ fontSize: "11px" }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="volume" fill="#00D4FF" fillOpacity={0.7} radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Alert feed */}
      <Card className="bg-card border-border p-6">
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-semibold">Active Alerts</h3>
          <span className="text-xs px-2 py-1 bg-[#FF2D55]/10 text-[#FF2D55] border border-[#FF2D55]/30 rounded">
            {alerts.filter((a) => a.severity !== "low").length} critical
          </span>
        </div>
        <div className="space-y-3">
          {alerts.map((alert, i) => (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: i * 0.06 }}
              className={`flex items-start gap-4 p-4 rounded-lg border ${
                alert.severity === "high"
                  ? "bg-[#FF2D55]/5 border-[#FF2D55]/20"
                  : alert.severity === "medium"
                  ? "bg-[#FBBF24]/5 border-[#FBBF24]/20"
                  : "bg-muted/40 border-border"
              }`}
            >
              <AlertTriangle
                className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                  alert.severity === "high"
                    ? "text-[#FF2D55]"
                    : alert.severity === "medium"
                    ? "text-[#FBBF24]"
                    : "text-muted-foreground"
                }`}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-1">
                  <span className="text-sm font-semibold">{alert.type}</span>
                  <span className="text-xs text-muted-foreground">·</span>
                  <span className="text-xs text-muted-foreground font-mono">{alert.model}</span>
                </div>
                <p className="text-sm text-muted-foreground">{alert.message}</p>
              </div>
              <div className="text-xs text-muted-foreground whitespace-nowrap">{alert.time}</div>
            </motion.div>
          ))}
        </div>
      </Card>
    </div>
  );
}
