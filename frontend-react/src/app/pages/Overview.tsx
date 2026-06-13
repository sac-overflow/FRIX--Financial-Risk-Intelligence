import { motion } from "motion/react";
import { AlertTriangle, CheckCircle, TrendingUp, TrendingDown, ArrowRight, DollarSign, Eye, Cpu, Wifi } from "lucide-react";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from "recharts";

const riskActivityData = [
  { time: "00:00", low: 120, medium: 45, high: 12 },
  { time: "04:00", low: 98, medium: 38, high: 8 },
  { time: "08:00", low: 145, medium: 62, high: 18 },
  { time: "12:00", low: 178, medium: 78, high: 24 },
  { time: "16:00", low: 156, medium: 54, high: 15 },
  { time: "20:00", low: 134, medium: 48, high: 11 },
];

const fraudDistribution = [
  { name: "Low Risk", value: 68, color: "#00D4FF" },
  { name: "Medium Risk", value: 24, color: "#FBBF24" },
  { name: "High Risk", value: 8, color: "#FF2D55" },
];

const recentTransactions = [
  { id: "TXN-8372", account: "ACC-4721", amount: "$12,450", risk: 94.2, status: "high", time: "2m ago" },
  { id: "TXN-8371", account: "ACC-2156", amount: "$3,200", risk: 78.5, status: "high", time: "5m ago" },
  { id: "TXN-8370", account: "ACC-9834", amount: "$850", risk: 42.1, status: "medium", time: "8m ago" },
  { id: "TXN-8369", account: "ACC-5623", amount: "$15,700", risk: 12.3, status: "low", time: "12m ago" },
  { id: "TXN-8368", account: "ACC-7891", amount: "$920", risk: 8.7, status: "low", time: "15m ago" },
];

export function Overview() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2">Risk Overview</h1>
        <p className="text-muted-foreground">Real-time monitoring of fraud detection and risk analysis</p>
      </div>

      {/* FastAPI status pill */}
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-[#00D4FF] animate-pulse inline-block shadow-[0_0_6px_rgba(0,212,255,0.8)]" />
        <span className="text-xs text-muted-foreground font-mono">FastAPI Service: <span className="text-[#00D4FF]">Healthy</span></span>
        <span className="text-xs text-muted-foreground">·</span>
        <span className="text-xs text-muted-foreground font-mono">XGBoost Champion · v4.2.1</span>
      </div>

      {/* Metric Cards — 6 cards per spec */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {[
          { label: "Total Transactions Scored", value: "24,847", icon: CheckCircle, color: "#00D4FF", trend: "+12.5%", up: true },
          { label: "Fraud Alerts", value: "187", icon: AlertTriangle, color: "#FF2D55", trend: "+8.2%", up: true, danger: true },
          { label: "High Risk Value", value: "$2.4M", icon: DollarSign, color: "#FF2D55", trend: "+3.1%", up: true, danger: true },
          { label: "False Positive Watch", value: "14", icon: Eye, color: "#FBBF24", trend: "-2", up: false },
          { label: "Active Model", value: "XGBoost", icon: Cpu, color: "#00D4FF", sub: "v4.2.1 · 99.7% acc" },
          { label: "API Health", value: "99.99%", icon: Wifi, color: "#00D4FF", sub: "18ms avg latency" },
        ].map((card, i) => (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: i * 0.06 }}
          >
            <Card className={`bg-card p-5 border transition-all ${
              card.danger
                ? "border-[#FF2D55]/30 shadow-[0_0_16px_rgba(255,45,85,0.1)]"
                : "border-border hover:border-[#00D4FF]/30"
            }`}>
              <div className="flex items-start justify-between mb-3">
                <div className="text-xs text-muted-foreground leading-tight">{card.label}</div>
                <card.icon className="w-4 h-4 flex-shrink-0" style={{ color: card.color }} />
              </div>
              <div className="text-2xl font-bold mb-1" style={{ color: card.danger ? card.color : undefined }}>{card.value}</div>
              {card.trend && (
                <div className="flex items-center gap-1 text-xs">
                  {card.up ? <TrendingUp className="w-3 h-3" style={{ color: card.color }} /> : <TrendingDown className="w-3 h-3" style={{ color: card.color }} />}
                  <span style={{ color: card.color }}>{card.trend}</span>
                  <span className="text-muted-foreground">vs last hr</span>
                </div>
              )}
              {card.sub && <div className="text-xs text-muted-foreground">{card.sub}</div>}
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Activity Timeline */}
        <Card className="lg:col-span-2 bg-card border-border p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold mb-1">Risk Activity Timeline</h3>
              <p className="text-sm text-muted-foreground">Last 24 hours</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#00D4FF]" />
                <span className="text-muted-foreground">Low</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#FBBF24]" />
                <span className="text-muted-foreground">Medium</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#FF2D55]" />
                <span className="text-muted-foreground">High</span>
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={riskActivityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" stroke="var(--frix-muted-text)" style={{ fontSize: '12px' }} />
              <YAxis stroke="var(--frix-muted-text)" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--card)',
                  border: '1px solid var(--frix-border)',
                  borderRadius: '8px',
                  color: 'var(--frix-text)'
                }}
              />
              <Area type="monotone" dataKey="low" stroke="#00D4FF" fill="#00D4FF" fillOpacity={0.15} />
              <Area type="monotone" dataKey="medium" stroke="#FBBF24" fill="#FBBF24" fillOpacity={0.15} />
              <Area type="monotone" dataKey="high" stroke="#FF2D55" fill="#FF2D55" fillOpacity={0.15} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        {/* Fraud Probability Distribution */}
        <Card className="bg-card border-border p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-1">Risk Distribution</h3>
            <p className="text-sm text-muted-foreground">Current breakdown</p>
          </div>
          <ResponsiveContainer key="ov-pie" width="100%" height={200}>
            <PieChart>
              <Pie
                data={fraudDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {fraudDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-3 mt-4">
            {fraudDistribution.map((item) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-sm text-muted-foreground">{item.name}</span>
                </div>
                <span className="text-sm font-semibold">{item.value}%</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Recent High-Risk Transactions */}
      <Card className="bg-card border-border p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold mb-1">Recent High-Risk Transactions</h3>
            <p className="text-sm text-muted-foreground">Flagged for review</p>
          </div>
          <Button 
            variant="outline"
            className="border-white/10 hover:border-[#00D4FF]/50 hover:bg-white/5"
          >
            View All
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left text-xs font-medium text-muted-foreground pb-3">Transaction ID</th>
                <th className="text-left text-xs font-medium text-muted-foreground pb-3">Account</th>
                <th className="text-left text-xs font-medium text-muted-foreground pb-3">Amount</th>
                <th className="text-left text-xs font-medium text-muted-foreground pb-3">Risk Score</th>
                <th className="text-left text-xs font-medium text-muted-foreground pb-3">Status</th>
                <th className="text-left text-xs font-medium text-muted-foreground pb-3">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {recentTransactions.map((txn, i) => (
                <motion.tr
                  key={txn.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: i * 0.05 }}
                  className={`hover:bg-white/5 transition-colors ${
                    txn.status === 'high' ? 'border-l-2 border-l-[#FF2D55]' : ''
                  }`}
                >
                  <td className="py-4 font-mono text-sm">{txn.id}</td>
                  <td className="py-4 text-sm">{txn.account}</td>
                  <td className="py-4 text-sm font-semibold">{txn.amount}</td>
                  <td className="py-4">
                    <div className="flex items-center gap-2">
                      <span 
                        className={`text-sm font-bold ${
                          txn.status === 'high' 
                            ? 'text-[#FF2D55]' 
                            : txn.status === 'medium'
                            ? 'text-[#FBBF24]'
                            : 'text-[#00D4FF]'
                        }`}
                      >
                        {txn.risk}
                      </span>
                    </div>
                  </td>
                  <td className="py-4">
                    <span 
                      className={`px-2 py-1 rounded text-xs border ${
                        txn.status === 'high'
                          ? 'bg-[#FF2D55]/10 text-[#FF2D55] border-[#FF2D55]/30'
                          : txn.status === 'medium'
                          ? 'bg-[#FBBF24]/10 text-[#FBBF24] border-[#FBBF24]/30'
                          : 'bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]/30'
                      }`}
                    >
                      {txn.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-4 text-sm text-muted-foreground">{txn.time}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
