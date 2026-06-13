import { motion } from "motion/react";
import { useState } from "react";
import { Crown, Zap, TrendingUp, CheckCircle, ChevronDown } from "lucide-react";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

const tooltipStyle = {
  backgroundColor: "var(--card)",
  border: "1px solid var(--frix-border)",
  borderRadius: "8px",
  color: "var(--frix-text)",
};

const modelCards = [
  { id: 1, name: "Random Forest Baseline", tag: "Stable", color: "#00D4FF", desc: "Ensemble of decision trees with bootstrap aggregation. High interpretability, proven baseline performance.", acc: 98.2 },
  { id: 2, name: "XGBoost Advanced Fraud Model", tag: "Champion", color: "#00D4FF", desc: "Gradient boosting with deep feature engineering. Top fraud detection accuracy.", acc: 99.7 },
  { id: 3, name: "LightGBM Fast Inference Model", tag: "Challenger", color: "#A78BFA", desc: "Optimised gradient boosting for sub-20ms inference. Best for high-throughput environments.", acc: 99.1 },
  { id: 4, name: "Graph-Risk Model", tag: "Challenger", color: "#A78BFA", desc: "Graph neural network leveraging account relationship topology for mule-risk detection.", acc: 99.4 },
  { id: 5, name: "Rule-Assisted Mode", tag: "Hybrid", color: "#FBBF24", desc: "Combines ML scores with configurable rule engine. Ideal for regulated environments requiring auditability.", acc: 97.8 },
  { id: 6, name: "Explainability-First Mode", tag: "Audit", color: "#FBBF24", desc: "Prioritises SHAP-based explanations and reason codes. Required for compliance reporting.", acc: 97.2 },
  { id: 7, name: "Low-Latency Mode", tag: "Speed", color: "#34D399", desc: "Optimised for <10ms P99 latency. Lightweight feature set for real-time payment gating.", acc: 96.8 },
  { id: 8, name: "High-Accuracy Mode", tag: "Precision", color: "#00D4FF", desc: "Full feature pipeline with ensemble stacking. Maximises PR-AUC, recommended for batch scoring.", acc: 99.9 },
];

const comparisonData = [
  { model: "Random Forest", precision: 97.1, recall: 96.8, prAuc: 0.978, fp: 142, fn: 89, speed: "38ms", status: "Stable" },
  { model: "XGBoost",       precision: 98.9, recall: 97.4, prAuc: 0.994, fp: 87,  fn: 71, speed: "42ms", status: "Champion" },
  { model: "LightGBM",      precision: 98.4, recall: 97.2, prAuc: 0.989, fp: 98,  fn: 78, speed: "28ms", status: "Challenger" },
  { model: "Graph-Risk",    precision: 99.2, recall: 98.1, prAuc: 0.996, fp: 54,  fn: 52, speed: "85ms", status: "Challenger" },
  { model: "Rule-Assisted", precision: 96.8, recall: 95.4, prAuc: 0.971, fp: 182, fn: 124, speed: "22ms", status: "Hybrid" },
  { model: "Explainability", precision: 96.3, recall: 94.9, prAuc: 0.965, fp: 204, fn: 139, speed: "55ms", status: "Audit" },
];

const chartData = [
  { name: "Random Forest", precision: 97.1, recall: 96.8 },
  { name: "XGBoost",       precision: 98.9, recall: 97.4 },
  { name: "LightGBM",      precision: 98.4, recall: 97.2 },
  { name: "Graph-Risk",    precision: 99.2, recall: 98.1 },
];

const selectorOptions = {
  "Client Usage Pattern": ["High Volume B2B", "Retail Payments", "Crypto Exchange", "Mobile Banking"],
  "Data Volume": ["< 1K/day", "1K–100K/day", "> 100K/day"],
  "Required Latency": ["< 10ms", "10–50ms", "50–200ms", "> 200ms"],
  "Required Accuracy": ["Max Accuracy", "Balanced", "Speed Priority"],
  "Explainability Need": ["Required", "Preferred", "Not needed"],
  "Volatility Level": ["Low", "Medium", "High"],
};

const statusBadge = (s: string) => {
  if (s === "Champion") return "bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]/30";
  if (s === "Challenger") return "bg-[#A78BFA]/10 text-[#A78BFA] border-[#A78BFA]/30";
  if (s === "Stable") return "bg-[#34D399]/10 text-[#34D399] border-[#34D399]/30";
  return "bg-muted/40 text-muted-foreground border-border";
};

export function ModelEngine() {
  const [activeModel, setActiveModel] = useState(modelCards[1]);
  const [selectorValues, setSelectorValues] = useState<Record<string, string>>({});

  const recommended = (() => {
    const lat = selectorValues["Required Latency"];
    const acc = selectorValues["Required Accuracy"];
    const exp = selectorValues["Explainability Need"];
    if (lat === "< 10ms") return "Low-Latency Mode";
    if (exp === "Required") return "Explainability-First Mode";
    if (acc === "Max Accuracy") return "High-Accuracy Mode";
    return "XGBoost Advanced Fraud Model";
  })();

  return (
    <div className="space-y-10">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">Adaptive Model Engine</h1>
          <p className="text-muted-foreground">Select, compare, and deploy ML models for fraud detection</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="gap-2">
            <TrendingUp className="w-4 h-4" /> Run Benchmark
          </Button>
          <Button className="bg-[#00D4FF] hover:bg-[#00B8E0] text-[#0F0F12] gap-2">
            <Crown className="w-4 h-4" /> Promote Champion
          </Button>
        </div>
      </div>

      {/* 8 Model Cards */}
      <div>
        <div className="text-xs text-muted-foreground uppercase tracking-wider mb-4">Available Model Modes</div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {modelCards.map((m, i) => (
            <motion.button
              key={m.id}
              onClick={() => setActiveModel(m)}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
              className={`text-left p-5 rounded-lg border transition-all ${
                activeModel.id === m.id
                  ? "border-[#00D4FF]/50 bg-[#00D4FF]/5 shadow-[0_0_20px_rgba(0,212,255,0.1)]"
                  : "bg-card border-border hover:border-[#00D4FF]/30"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className={`text-xs px-2 py-0.5 rounded border font-semibold`} style={{ color: m.color, borderColor: `${m.color}40`, background: `${m.color}15` }}>
                  {m.tag}
                </span>
                {m.tag === "Champion" && <Crown className="w-4 h-4 text-[#00D4FF]" />}
              </div>
              <div className="text-sm font-semibold leading-snug mb-2">{m.name}</div>
              <div className="text-xs text-muted-foreground leading-relaxed">{m.desc}</div>
              <div className="mt-3 text-xs font-mono" style={{ color: m.color }}>{m.acc}% acc</div>
            </motion.button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Model Selector Panel */}
        <Card className="bg-card border-border p-6">
          <h3 className="font-semibold mb-1">Model Selector</h3>
          <p className="text-xs text-muted-foreground mb-5">Configure requirements to get a recommended model</p>
          <div className="space-y-4">
            {Object.entries(selectorOptions).map(([label, opts]) => (
              <div key={label}>
                <label className="block text-xs text-muted-foreground mb-1.5">{label}</label>
                <div className="relative">
                  <select
                    value={selectorValues[label] ?? ""}
                    onChange={(e) => setSelectorValues((v) => ({ ...v, [label]: e.target.value }))}
                    className="w-full appearance-none bg-muted/40 border border-border rounded-lg px-3 py-2 pr-7 text-sm text-foreground focus:outline-none focus:border-[#00D4FF]/50"
                  >
                    <option value="">Select…</option>
                    {opts.map((o) => <option key={o} value={o}>{o}</option>)}
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
                </div>
              </div>
            ))}
          </div>
          {Object.keys(selectorValues).length > 0 && (
            <div className="mt-5 p-4 bg-[#00D4FF]/5 border border-[#00D4FF]/20 rounded-lg">
              <div className="text-xs text-muted-foreground mb-1">Recommended Model Mode</div>
              <div className="text-sm font-semibold text-[#00D4FF]">{recommended}</div>
            </div>
          )}
        </Card>

        {/* Champion vs Challenger */}
        <Card className="col-span-2 bg-card border-border p-6">
          <h3 className="font-semibold mb-5">Champion vs Challenger</h3>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-4 bg-[#00D4FF]/5 border border-[#00D4FF]/30 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Crown className="w-4 h-4 text-[#00D4FF]" />
                <span className="text-xs text-[#00D4FF] font-semibold uppercase tracking-wider">Champion</span>
              </div>
              <div className="font-semibold">XGBoost Advanced</div>
              <div className="text-xs text-muted-foreground mt-1">v4.2.1 · 99.7% acc · 42ms</div>
              <div className="text-xs font-mono text-[#00D4FF] mt-2">PR-AUC: 0.994</div>
            </div>
            <div className="p-4 bg-muted/40 border border-border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-4 h-4 text-[#A78BFA]" />
                <span className="text-xs text-[#A78BFA] font-semibold uppercase tracking-wider">Challengers</span>
              </div>
              <div className="space-y-1">
                {["LightGBM Fast · 99.1%", "Graph-Risk · 99.4%", "Random Forest · 98.2%"].map((c) => (
                  <div key={c} className="text-xs text-muted-foreground">{c}</div>
                ))}
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" stroke="var(--frix-muted-text)" style={{ fontSize: "10px" }} />
              <YAxis domain={[94, 100]} stroke="var(--frix-muted-text)" style={{ fontSize: "10px" }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="precision" name="Precision %" fill="#00D4FF" fillOpacity={0.8} radius={[3, 3, 0, 0]} />
              <Bar dataKey="recall" name="Recall %" fill="#A78BFA" fillOpacity={0.8} radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Full Comparison Table */}
      <Card className="bg-card border-border overflow-hidden">
        <div className="p-6 border-b border-border">
          <h3 className="font-semibold">Model Comparison Table</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--frix-border)" }}>
                {["Model", "Precision", "Recall", "PR-AUC", "False Positives", "False Negatives", "Inference Speed", "Deployment Status"].map((h) => (
                  <th key={h} className="text-left text-xs font-medium text-muted-foreground px-5 py-3 whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {comparisonData.map((row, i) => (
                <motion.tr
                  key={row.model}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.05 }}
                  className={`hover:bg-muted/20 transition-colors ${row.status === "Champion" ? "border-l-2 border-l-[#00D4FF]" : ""}`}
                  style={{ borderBottom: "1px solid var(--frix-border)" }}
                >
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      {row.status === "Champion" && <Crown className="w-3.5 h-3.5 text-[#00D4FF]" />}
                      <span className="text-sm font-semibold">{row.model}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3 text-sm font-mono">{row.precision}%</td>
                  <td className="px-5 py-3 text-sm font-mono">{row.recall}%</td>
                  <td className="px-5 py-3 text-sm font-mono text-[#00D4FF]">{row.prAuc}</td>
                  <td className="px-5 py-3 text-sm font-mono">{row.fp}</td>
                  <td className="px-5 py-3 text-sm font-mono">{row.fn}</td>
                  <td className="px-5 py-3 text-sm font-mono">{row.speed}</td>
                  <td className="px-5 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded border font-semibold ${statusBadge(row.status)}`}>{row.status}</span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
