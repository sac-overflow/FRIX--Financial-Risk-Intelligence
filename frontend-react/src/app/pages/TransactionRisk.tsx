import { motion } from "motion/react";
import { useState } from "react";
import { Filter, Download, Search, ChevronDown } from "lucide-react";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

const transactions = [
  { id: "TXN-8372", type: "TRANSFER",   amount: 245000, sender: "ACC-4721", receiver: "ACC-9900", prob: 0.942, risk: "HIGH",   model: "XGBoost",    reasons: ["sender_emptied_account","large_amount"],             ts: "2026-06-10 14:23:12" },
  { id: "TXN-8371", type: "CASH_OUT",   amount: 87500,  sender: "ACC-2156", receiver: "ACC-3310", prob: 0.785, risk: "HIGH",   model: "XGBoost",    reasons: ["high_risk_transaction_type","origin_balance_error"], ts: "2026-06-10 14:18:45" },
  { id: "TXN-8370", type: "PAYMENT",    amount: 12400,  sender: "ACC-9834", receiver: "ACC-1120", prob: 0.421, risk: "MEDIUM", model: "LightGBM",   reasons: ["large_amount"],                                      ts: "2026-06-10 14:15:33" },
  { id: "TXN-8369", type: "TRANSFER",   amount: 500,    sender: "ACC-5623", receiver: "ACC-7745", prob: 0.123, risk: "LOW",    model: "XGBoost",    reasons: [],                                                    ts: "2026-06-10 14:11:22" },
  { id: "TXN-8368", type: "PAYMENT",    amount: 920,    sender: "ACC-7891", receiver: "ACC-4452", prob: 0.087, risk: "LOW",    model: "LightGBM",   reasons: [],                                                    ts: "2026-06-10 14:08:15" },
  { id: "TXN-8367", type: "CASH_OUT",   amount: 56000,  sender: "ACC-3421", receiver: "ACC-8821", prob: 0.674, risk: "HIGH",   model: "Graph-Risk", reasons: ["high_risk_transaction_type","dest_balance_error"],   ts: "2026-06-10 14:05:42" },
  { id: "TXN-8366", type: "DEBIT",      amount: 2400,   sender: "ACC-8912", receiver: "ACC-5512", prob: 0.238, risk: "MEDIUM", model: "XGBoost",    reasons: ["origin_balance_error"],                              ts: "2026-06-10 14:02:11" },
  { id: "TXN-8365", type: "CASH_IN",    amount: 780,    sender: "ACC-5647", receiver: "ACC-2231", prob: 0.152, risk: "LOW",    model: "LightGBM",   reasons: [],                                                    ts: "2026-06-10 13:58:33" },
  { id: "TXN-8364", type: "TRANSFER",   amount: 380000, sender: "ACC-1133", receiver: "ACC-7654", prob: 0.967, risk: "HIGH",   model: "XGBoost",    reasons: ["large_amount","sender_emptied_account","high_risk_transaction_type"], ts: "2026-06-10 13:55:01" },
  { id: "TXN-8363", type: "PAYMENT",    amount: 4200,   sender: "ACC-6678", receiver: "ACC-3398", prob: 0.312, risk: "MEDIUM", model: "Graph-Risk", reasons: ["dest_balance_error"],                                ts: "2026-06-10 13:51:44" },
];

const RISK_LEVELS = ["all", "HIGH", "MEDIUM", "LOW"];
const TXN_TYPES = ["all", "TRANSFER", "CASH_OUT", "PAYMENT", "DEBIT", "CASH_IN"];
const MODELS = ["all", "XGBoost", "LightGBM", "Graph-Risk"];

const riskClass = (risk: string) => {
  if (risk === "HIGH") return "bg-[#FF2D55]/10 text-[#FF2D55] border-[#FF2D55]/30";
  if (risk === "MEDIUM") return "bg-[#FBBF24]/10 text-[#FBBF24] border-[#FBBF24]/30";
  return "bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]/30";
};

const rowGlow = (risk: string) => {
  if (risk === "HIGH") return "border-l-2 border-l-[#FF2D55]";
  if (risk === "MEDIUM") return "border-l-2 border-l-[#FBBF24]";
  return "";
};

export function TransactionRisk() {
  const [search, setSearch] = useState("");
  const [filterRisk, setFilterRisk] = useState("all");
  const [filterType, setFilterType] = useState("all");
  const [filterModel, setFilterModel] = useState("all");
  const [minAmt, setMinAmt] = useState("");
  const [maxAmt, setMaxAmt] = useState("");

  const filtered = transactions.filter((t) => {
    if (search && !t.id.toLowerCase().includes(search.toLowerCase()) && !t.sender.toLowerCase().includes(search.toLowerCase())) return false;
    if (filterRisk !== "all" && t.risk !== filterRisk) return false;
    if (filterType !== "all" && t.type !== filterType) return false;
    if (filterModel !== "all" && t.model !== filterModel) return false;
    if (minAmt && t.amount < parseFloat(minAmt)) return false;
    if (maxAmt && t.amount > parseFloat(maxAmt)) return false;
    return true;
  });

  const Select = ({ value, onChange, options }: { value: string; onChange: (v: string) => void; options: string[] }) => (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="appearance-none bg-muted/40 border border-border rounded-lg px-3 py-2 pr-7 text-sm text-foreground focus:outline-none focus:border-[#00D4FF]/50 cursor-pointer"
      >
        {options.map((o) => <option key={o} value={o}>{o === "all" ? `All ${o}` : o}</option>)}
      </select>
      <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">Transaction Risk Analysis</h1>
          <p className="text-muted-foreground">Monitor and filter transaction-level fraud scores</p>
        </div>
        <Button variant="outline" className="gap-2">
          <Download className="w-4 h-4" /> Export CSV
        </Button>
      </div>

      {/* Filters */}
      <Card className="bg-card border-border p-5">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="relative flex-1 min-w-48">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search ID or account…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 focus:border-[#00D4FF]/50 focus:ring-2 focus:ring-[#00D4FF]/20"
            />
          </div>
          <Filter className="w-4 h-4 text-muted-foreground" />
          <Select value={filterRisk} onChange={setFilterRisk} options={RISK_LEVELS} />
          <Select value={filterType} onChange={setFilterType} options={TXN_TYPES} />
          <Select value={filterModel} onChange={setFilterModel} options={MODELS} />
          <div className="flex items-center gap-2">
            <Input placeholder="Min $" value={minAmt} onChange={(e) => setMinAmt(e.target.value)} className="w-24 text-sm" />
            <span className="text-muted-foreground text-xs">–</span>
            <Input placeholder="Max $" value={maxAmt} onChange={(e) => setMaxAmt(e.target.value)} className="w-24 text-sm" />
          </div>
          <span className="text-xs text-muted-foreground ml-auto">{filtered.length} results</span>
        </div>
      </Card>

      {/* Table */}
      <Card className="bg-card border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--frix-border)" }}>
                {["Transaction ID", "Type", "Amount", "Sender", "Receiver", "Fraud Prob.", "Risk Level", "Model Used", "Reason Codes", "Timestamp"].map((h) => (
                  <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((txn, i) => (
                <motion.tr
                  key={txn.id}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.25, delay: i * 0.04 }}
                  className={`hover:bg-muted/20 transition-colors ${rowGlow(txn.risk)}`}
                  style={{ borderBottom: "1px solid var(--frix-border)" }}
                >
                  <td className="px-4 py-3 font-mono text-xs">{txn.id}</td>
                  <td className="px-4 py-3">
                    <span className="text-xs font-mono px-2 py-0.5 bg-muted/40 border border-border rounded">{txn.type}</span>
                  </td>
                  <td className="px-4 py-3 text-sm font-semibold">${txn.amount.toLocaleString()}</td>
                  <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{txn.sender}</td>
                  <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{txn.receiver}</td>
                  <td className="px-4 py-3">
                    <span className={`text-sm font-bold font-mono ${
                      txn.prob >= 0.7 ? "text-[#FF2D55]" : txn.prob >= 0.4 ? "text-[#FBBF24]" : "text-[#00D4FF]"
                    }`}>{txn.prob.toFixed(3)}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded border font-semibold ${riskClass(txn.risk)}`}>{txn.risk}</span>
                  </td>
                  <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{txn.model}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1 flex-wrap">
                      {txn.reasons.length === 0 ? (
                        <span className="text-xs text-muted-foreground">—</span>
                      ) : txn.reasons.map((r) => (
                        <span key={r} className="text-xs px-1.5 py-0.5 bg-[#FF2D55]/10 text-[#FF2D55] border border-[#FF2D55]/20 rounded font-mono whitespace-nowrap">{r}</span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-xs text-muted-foreground font-mono whitespace-nowrap">{txn.ts}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
