import { useState } from "react";
import { motion } from "motion/react";
import {
  Building2, Key, Bell, Shield, Users, Database,
  FileText, ToggleLeft, CheckCircle, Copy, Eye, EyeOff, Plus, Terminal, Cpu
} from "lucide-react";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

const sections = [
  { id: "workspace", label: "Workspace", icon: Building2 },
  { id: "model-prefs", label: "Model Preferences", icon: Cpu },
  { id: "thresholds", label: "Risk Thresholds", icon: ToggleLeft },
  { id: "api-keys", label: "API Keys", icon: Key },
  { id: "env-vars", label: "Environment Variables", icon: Terminal },
  { id: "team", label: "Team & Access", icon: Users },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "audit", label: "Audit Log", icon: FileText },
  { id: "security", label: "Security", icon: Shield },
  { id: "data", label: "Data & Privacy", icon: Database },
];

const apiKeys = [
  { name: "Production", key: "frix_prod_sk_a7d2f1c3e8b4", env: "Production", created: "Jan 12 2026", lastUsed: "Just now" },
  { name: "Staging", key: "frix_stg_sk_b3e9a1d5c7f2", env: "Staging", created: "Mar 4 2026", lastUsed: "2 hr ago" },
  { name: "CI/CD Runner", key: "frix_ci_sk_c5f8b2e4a9d1", env: "CI/CD", created: "Apr 21 2026", lastUsed: "12 min ago" },
];

const teamMembers = [
  { name: "Elena Vargas", email: "elena@frix.io", role: "Admin", status: "active", avatar: "EV" },
  { name: "Amir Patel", email: "amir@frix.io", role: "ML Engineer", status: "active", avatar: "AP" },
  { name: "Nadia Chen", email: "nadia@frix.io", role: "Analyst", status: "active", avatar: "NC" },
  { name: "Luca Romano", email: "luca@frix.io", role: "Analyst", status: "invited", avatar: "LR" },
];

const auditLog = [
  { actor: "Elena Vargas", action: "Promoted XGBoost v4.2.1 to champion", time: "2 min ago", type: "model" },
  { actor: "Amir Patel", action: "Updated fraud threshold to 0.85", time: "1 hr ago", type: "config" },
  { actor: "System", action: "Auto-rotation: API key frix_prod_sk_••••", time: "3 hr ago", type: "security" },
  { actor: "Nadia Chen", action: "Exported transaction report (CSV)", time: "5 hr ago", type: "data" },
  { actor: "Elena Vargas", action: "Invited luca@frix.io as Analyst", time: "Yesterday", type: "team" },
  { actor: "System", action: "Model drift alert resolved — PSI 0.04", time: "Yesterday", type: "model" },
];

const auditColors: Record<string, string> = {
  model: "text-[#A78BFA] bg-[#A78BFA]/10 border-[#A78BFA]/20",
  config: "text-[#FBBF24] bg-[#FBBF24]/10 border-[#FBBF24]/20",
  security: "text-[#FF2D55] bg-[#FF2D55]/10 border-[#FF2D55]/20",
  data: "text-[#00D4FF] bg-[#00D4FF]/10 border-[#00D4FF]/20",
  team: "text-[#34D399] bg-[#34D399]/10 border-[#34D399]/20",
};

export function Settings() {
  const [activeSection, setActiveSection] = useState("workspace");
  const [visibleKeys, setVisibleKeys] = useState<Record<number, boolean>>({});
  const [copied, setCopied] = useState<number | null>(null);

  const [fraudThreshold, setFraudThreshold] = useState("0.85");
  const [muleThreshold, setMuleThreshold] = useState("0.72");
  const [autoReview, setAutoReview] = useState(true);
  const [alertsEnabled, setAlertsEnabled] = useState(true);

  const toggleKeyVisibility = (i: number) => setVisibleKeys((prev) => ({ ...prev, [i]: !prev[i] }));

  const copyKey = (key: string, i: number) => {
    navigator.clipboard.writeText(key);
    setCopied(i);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">Settings</h1>
        <p className="text-muted-foreground">Workspace configuration, thresholds, keys, and security</p>
      </div>

      <div className="grid grid-cols-5 gap-6">
        {/* Sidebar */}
        <div className="col-span-1 space-y-1">
          {sections.map((s) => (
            <button
              key={s.id}
              onClick={() => setActiveSection(s.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-all ${
                activeSection === s.id
                  ? "bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/30"
                  : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
              }`}
            >
              <s.icon className="w-4 h-4" />
              {s.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="col-span-4 space-y-5">

          {activeSection === "workspace" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
              <Card className="bg-card border-border p-6">
                <h3 className="font-semibold mb-5">Organization Details</h3>
                <div className="grid grid-cols-2 gap-5">
                  {[
                    { label: "Organization Name", value: "FRIX Financial Intelligence" },
                    { label: "Industry", value: "Financial Services / Fintech" },
                    { label: "Plan", value: "Enterprise" },
                    { label: "Data Region", value: "US East (us-east-1)" },
                  ].map((f) => (
                    <div key={f.label}>
                      <label className="block text-xs text-muted-foreground mb-1.5">{f.label}</label>
                      <Input
                        defaultValue={f.value}
                        className="bg-muted border-white/10 focus:border-[#00D4FF]/50 text-sm"
                      />
                    </div>
                  ))}
                </div>
                <div className="flex justify-end mt-5">
                  <Button className="bg-[#00D4FF] hover:bg-[#00B8E0] text-[#0F0F12]">
                    Save Changes
                  </Button>
                </div>
              </Card>
            </motion.div>
          )}

          {activeSection === "model-prefs" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
              <Card className="bg-card border-border p-6">
                <h3 className="font-semibold mb-1">Model Preferences</h3>
                <p className="text-sm text-muted-foreground mb-6">Configure default model selection and inference behaviour.</p>
                <div className="space-y-4">
                  {[
                    { label: "Default Model Mode", options: ["XGBoost Advanced (Champion)", "LightGBM Fast", "High-Accuracy Mode", "Low-Latency Mode"] },
                    { label: "Fallback Model", options: ["Random Forest Baseline", "LightGBM Fast", "Rule-Assisted Mode"] },
                    { label: "Explainability Level", options: ["Full SHAP + Reason Codes", "Reason Codes Only", "Score Only"] },
                    { label: "Inference Timeout", options: ["50ms", "100ms", "200ms", "500ms"] },
                  ].map((f) => (
                    <div key={f.label}>
                      <label className="block text-xs text-muted-foreground mb-1.5">{f.label}</label>
                      <select className="w-full bg-muted/40 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-[#00D4FF]/50">
                        {f.options.map((o) => <option key={o}>{o}</option>)}
                      </select>
                    </div>
                  ))}
                  <div className="flex items-center justify-between p-4 bg-muted/40 rounded-lg border border-border">
                    <div>
                      <div className="text-sm font-semibold mb-0.5">Auto-Promote on Benchmark Win</div>
                      <div className="text-xs text-muted-foreground">Automatically promote a challenger when it beats champion by &gt;0.5% PR-AUC.</div>
                    </div>
                    <button className="relative w-12 h-6 rounded-full bg-[#00D4FF] transition-colors">
                      <div className="absolute top-1 w-4 h-4 rounded-full bg-white translate-x-7 transition-transform" />
                    </button>
                  </div>
                </div>
                <div className="flex justify-end mt-5">
                  <Button className="bg-[#00D4FF] hover:bg-[#00B8E0] text-[#0F0F12]">Save Preferences</Button>
                </div>
              </Card>
            </motion.div>
          )}

          {activeSection === "env-vars" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
              <Card className="bg-card border-border p-6">
                <div className="flex items-center justify-between mb-5">
                  <div>
                    <h3 className="font-semibold mb-1">Environment Variables</h3>
                    <p className="text-sm text-muted-foreground">Runtime configuration for FRIX services.</p>
                  </div>
                  <Button variant="outline" className="border-border hover:border-[#00D4FF]/50 text-xs h-8 gap-1.5">
                    <Plus className="w-3.5 h-3.5" /> Add Variable
                  </Button>
                </div>
                <div className="space-y-2">
                  {[
                    { key: "FRIX_ENV", value: "production", locked: true },
                    { key: "FRIX_MODEL_PATH", value: "/models/xgboost_v4.2.1.joblib", locked: false },
                    { key: "FRIX_DB_URL", value: "postgresql://••••••••@db.frix.io:5432/frix", locked: true },
                    { key: "FRIX_REDIS_URL", value: "redis://cache.frix.io:6379/0", locked: true },
                    { key: "FRIX_LOG_LEVEL", value: "INFO", locked: false },
                    { key: "FRIX_API_TIMEOUT_MS", value: "100", locked: false },
                    { key: "FRIX_FRAUD_THRESHOLD", value: "0.85", locked: false },
                    { key: "FRIX_MULE_THRESHOLD", value: "0.72", locked: false },
                  ].map((env, i) => (
                    <div key={env.key} className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg border border-border font-mono text-xs">
                      <span className="text-[#00D4FF] w-48 flex-shrink-0">{env.key}</span>
                      <span className="text-muted-foreground flex-1">=</span>
                      <span className={`flex-1 ${env.locked ? "text-muted-foreground" : "text-foreground"}`}>{env.value}</span>
                      {!env.locked && (
                        <button className="text-muted-foreground hover:text-foreground transition-colors">
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            </motion.div>
          )}

          {activeSection === "thresholds" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
              <Card className="bg-card border-border p-6">
                <h3 className="font-semibold mb-1">Risk Decision Thresholds</h3>
                <p className="text-sm text-muted-foreground mb-6">Scores above these values trigger automatic review or block actions.</p>
                <div className="space-y-6">
                  {[
                    { label: "Fraud Probability Threshold", key: "fraud", value: fraudThreshold, onChange: setFraudThreshold, desc: "Transactions above this score are flagged HIGH and routed for review." },
                    { label: "Mule Risk Score Threshold", key: "mule", value: muleThreshold, onChange: setMuleThreshold, desc: "Accounts above this score trigger mule network investigation workflow." },
                  ].map((t) => (
                    <div key={t.key} className="p-4 bg-muted/40 rounded-lg border border-border">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <div className="text-sm font-semibold mb-1">{t.label}</div>
                          <div className="text-xs text-muted-foreground">{t.desc}</div>
                        </div>
                        <Input
                          value={t.value}
                          onChange={(e) => t.onChange(e.target.value)}
                          className="bg-muted border-white/10 focus:border-[#00D4FF]/50 w-24 text-center font-mono text-sm"
                        />
                      </div>
                      <div className="relative h-2 bg-white/10 rounded-full mt-3">
                        <div
                          className="absolute top-0 left-0 h-full bg-gradient-to-r from-[#00D4FF] to-[#FF2D55] rounded-full"
                          style={{ width: `${parseFloat(t.value) * 100}%` }}
                        />
                        <div
                          className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full border-2 border-[#00D4FF] shadow"
                          style={{ left: `${parseFloat(t.value) * 100 - 1}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-muted-foreground mt-1.5">
                        <span>0.0 — Safe</span>
                        <span>1.0 — Block</span>
                      </div>
                    </div>
                  ))}
                  <div className="flex items-center justify-between p-4 bg-muted/40 rounded-lg border border-border">
                    <div>
                      <div className="text-sm font-semibold mb-1">Auto-Review Routing</div>
                      <div className="text-xs text-muted-foreground">Automatically route high-risk transactions to the review queue.</div>
                    </div>
                    <button
                      onClick={() => setAutoReview((v) => !v)}
                      className={`relative w-12 h-6 rounded-full transition-colors ${autoReview ? "bg-[#00D4FF]" : "bg-white/10"}`}
                    >
                      <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${autoReview ? "translate-x-7" : "translate-x-1"}`} />
                    </button>
                  </div>
                </div>
                <div className="flex justify-end mt-5">
                  <Button className="bg-[#00D4FF] hover:bg-[#00B8E0] text-[#0F0F12]">
                    Apply Thresholds
                  </Button>
                </div>
              </Card>
            </motion.div>
          )}

          {activeSection === "api-keys" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
              <Card className="bg-card border-border p-6">
                <div className="flex items-center justify-between mb-5">
                  <h3 className="font-semibold">API Keys</h3>
                  <Button variant="outline" className="border-white/10 hover:border-[#00D4FF]/50 text-xs h-8 gap-1.5">
                    <Plus className="w-3.5 h-3.5" /> New Key
                  </Button>
                </div>
                <div className="space-y-3">
                  {apiKeys.map((k, i) => (
                    <div key={k.name} className="p-4 bg-muted/40 rounded-lg border border-border flex items-center gap-4">
                      <Key className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-semibold">{k.name}</span>
                          <span className="text-xs px-1.5 py-0.5 bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/20 rounded">
                            {k.env}
                          </span>
                        </div>
                        <code className="text-xs font-mono text-muted-foreground">
                          {visibleKeys[i] ? k.key : k.key.replace(/[a-z0-9]/gi, "•").slice(0, 20) + "••••••"}
                        </code>
                      </div>
                      <div className="text-xs text-muted-foreground whitespace-nowrap">Last used {k.lastUsed}</div>
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => toggleKeyVisibility(i)}
                          className="p-1.5 rounded hover:bg-white/5 text-muted-foreground hover:text-foreground transition-colors"
                        >
                          {visibleKeys[i] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                        <button
                          onClick={() => copyKey(k.key, i)}
                          className="p-1.5 rounded hover:bg-white/5 text-muted-foreground hover:text-foreground transition-colors"
                        >
                          {copied === i ? (
                            <CheckCircle className="w-4 h-4 text-[#00D4FF]" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </motion.div>
          )}

          {activeSection === "team" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
              <Card className="bg-card border-border p-6">
                <div className="flex items-center justify-between mb-5">
                  <h3 className="font-semibold">Team Members</h3>
                  <Button className="bg-[#00D4FF] hover:bg-[#00B8E0] text-[#0F0F12] text-xs h-8 gap-1.5">
                    <Plus className="w-3.5 h-3.5" /> Invite Member
                  </Button>
                </div>
                <div className="space-y-3">
                  {teamMembers.map((m) => (
                    <div key={m.email} className="flex items-center gap-4 p-3 bg-muted/40 rounded-lg">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#00D4FF]/30 to-[#0099CC]/30 border border-[#00D4FF]/30 flex items-center justify-center text-xs font-bold text-[#00D4FF]">
                        {m.avatar}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-semibold">{m.name}</div>
                        <div className="text-xs text-muted-foreground">{m.email}</div>
                      </div>
                      <span className="text-xs px-2 py-0.5 bg-white/5 border border-white/10 rounded text-muted-foreground">
                        {m.role}
                      </span>
                      <span
                        className={`text-xs px-2 py-0.5 rounded border ${
                          m.status === "active"
                            ? "bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]/20"
                            : "bg-white/5 text-muted-foreground border-white/10"
                        }`}
                      >
                        {m.status}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            </motion.div>
          )}

          {activeSection === "audit" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
              <Card className="bg-card border-border p-6">
                <h3 className="font-semibold mb-5">Audit Log</h3>
                <div className="space-y-2">
                  {auditLog.map((entry, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.25, delay: i * 0.04 }}
                      className="flex items-center gap-4 p-3 rounded-lg hover:bg-muted/40 transition-colors"
                    >
                      <span className={`text-xs px-2 py-0.5 rounded border whitespace-nowrap ${auditColors[entry.type]}`}>
                        {entry.type}
                      </span>
                      <div className="flex-1 text-sm">
                        <span className="font-semibold text-foreground">{entry.actor}</span>
                        <span className="text-muted-foreground"> · {entry.action}</span>
                      </div>
                      <div className="text-xs text-muted-foreground whitespace-nowrap">{entry.time}</div>
                    </motion.div>
                  ))}
                </div>
              </Card>
            </motion.div>
          )}

          {activeSection === "notifications" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
              <Card className="bg-card border-border p-6">
                <h3 className="font-semibold mb-5">Notification Preferences</h3>
                <div className="space-y-4">
                  {[
                    { label: "High-risk fraud alerts", desc: "Notify when transactions exceed fraud threshold", enabled: true },
                    { label: "Model drift warnings", desc: "Alert when PSI exceeds 0.05 on production models", enabled: alertsEnabled },
                    { label: "Pipeline failures", desc: "Alert on CI/CD deployment failures", enabled: true },
                    { label: "Weekly model performance digest", desc: "Summary email every Monday at 09:00 UTC", enabled: false },
                    { label: "API key expiry reminders", desc: "Remind 7 days before key expiration", enabled: true },
                  ].map((n) => (
                    <div key={n.label} className="flex items-center justify-between p-4 bg-muted/40 rounded-lg border border-border">
                      <div>
                        <div className="text-sm font-semibold">{n.label}</div>
                        <div className="text-xs text-muted-foreground mt-0.5">{n.desc}</div>
                      </div>
                      <button
                        onClick={() => n.label.includes("drift") && setAlertsEnabled((v) => !v)}
                        className={`relative w-12 h-6 rounded-full transition-colors ${n.enabled ? "bg-[#00D4FF]" : "bg-white/10"}`}
                      >
                        <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${n.enabled ? "translate-x-7" : "translate-x-1"}`} />
                      </button>
                    </div>
                  ))}
                </div>
              </Card>
            </motion.div>
          )}

          {(activeSection === "security" || activeSection === "data") && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Card className="bg-card border-border p-12 flex flex-col items-center justify-center text-center">
                <Shield className="w-10 h-10 text-muted-foreground mb-4" />
                <h3 className="font-semibold mb-2">Enterprise SSO & Security Settings</h3>
                <p className="text-sm text-muted-foreground max-w-sm">
                  Contact your account manager to configure SAML SSO, IP allowlisting, and data residency settings.
                </p>
                <Button className="mt-5 bg-[#00D4FF] hover:bg-[#00B8E0] text-[#0F0F12]">
                  Contact Enterprise Support
                </Button>
              </Card>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
