import { motion } from "motion/react";
import { useState } from "react";
import { AlertTriangle, Users, TrendingUp, ExternalLink } from "lucide-react";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";

const networkNodes = [
  { id: 1, x: 50, y: 50, type: "mule", label: "ACC-4721", risk: 94 },
  { id: 2, x: 20, y: 30, type: "normal", label: "ACC-2156", risk: 15 },
  { id: 3, x: 80, y: 30, type: "mule", label: "ACC-9834", risk: 87 },
  { id: 4, x: 35, y: 70, type: "normal", label: "ACC-5623", risk: 22 },
  { id: 5, x: 65, y: 70, type: "normal", label: "ACC-7891", risk: 18 },
  { id: 6, x: 50, y: 20, type: "suspect", label: "ACC-3421", risk: 68 },
  { id: 7, x: 15, y: 85, type: "normal", label: "ACC-8912", risk: 12 },
  { id: 8, x: 85, y: 85, type: "normal", label: "ACC-5647", risk: 9 },
];

const connections = [
  { from: 1, to: 2 },
  { from: 1, to: 3 },
  { from: 1, to: 4 },
  { from: 1, to: 5 },
  { from: 1, to: 6 },
  { from: 3, to: 8 },
  { from: 6, to: 2 },
  { from: 4, to: 7 },
];

export function MuleGraph() {
  const [selectedNode, setSelectedNode] = useState(networkNodes[0]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold mb-2">Mule Network Analysis</h1>
        <p className="text-muted-foreground">Graph-based detection of money mule patterns and networks</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-card border-[#FF2D55]/30 p-6 shadow-[0_0_20px_rgba(255,45,85,0.1)]">
          <div className="flex items-start justify-between mb-4">
            <div className="text-sm text-muted-foreground">Mule Accounts</div>
            <AlertTriangle className="w-5 h-5 text-[#FF2D55]" />
          </div>
          <div className="text-3xl font-bold text-[#FF2D55]">247</div>
          <div className="text-xs text-muted-foreground mt-2">+12 in last 24h</div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="text-sm text-muted-foreground">Network Clusters</div>
            <Users className="w-5 h-5 text-[#00D4FF]" />
          </div>
          <div className="text-3xl font-bold">42</div>
          <div className="text-xs text-muted-foreground mt-2">Active networks</div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="text-sm text-muted-foreground">Avg Cluster Size</div>
            <TrendingUp className="w-5 h-5 text-[#00D4FF]" />
          </div>
          <div className="text-3xl font-bold">8.4</div>
          <div className="text-xs text-muted-foreground mt-2">Accounts per cluster</div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="text-sm text-muted-foreground">Total Volume</div>
            <ExternalLink className="w-5 h-5 text-[#00D4FF]" />
          </div>
          <div className="text-3xl font-bold">$2.4M</div>
          <div className="text-xs text-muted-foreground mt-2">Flagged transfers</div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Graph Canvas */}
        <Card className="lg:col-span-2 bg-card border-border p-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold mb-1">Network Graph</h3>
              <p className="text-sm text-muted-foreground">Interactive account relationship mapping</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#FF2D55] shadow-[0_0_10px_rgba(255,45,85,0.8)]" />
                <span className="text-muted-foreground">Mule Account</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#FBBF24]" />
                <span className="text-muted-foreground">Suspect</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#00D4FF]/30 border border-[#00D4FF]" />
                <span className="text-muted-foreground">Normal</span>
              </div>
            </div>
          </div>

          {/* SVG Graph */}
          <div className="relative h-[500px] bg-black/30 rounded-lg border border-border overflow-hidden">
            <svg className="w-full h-full">
              {/* Connection lines */}
              {connections.map((conn, i) => {
                const fromNode = networkNodes.find(n => n.id === conn.from)!;
                const toNode = networkNodes.find(n => n.id === conn.to)!;
                const isMuleConnection = fromNode.type === 'mule' || toNode.type === 'mule';
                
                return (
                  <motion.line
                    key={i}
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ pathLength: 1, opacity: 0.3 }}
                    transition={{ duration: 1, delay: i * 0.1 }}
                    x1={`${fromNode.x}%`}
                    y1={`${fromNode.y}%`}
                    x2={`${toNode.x}%`}
                    y2={`${toNode.y}%`}
                    stroke={isMuleConnection ? "#FF2D55" : "#00D4FF"}
                    strokeWidth="2"
                    strokeDasharray={isMuleConnection ? "5,5" : "0"}
                  />
                );
              })}

              {/* Nodes */}
              {networkNodes.map((node, i) => (
                <g key={node.id}>
                  {/* Glow effect for mule nodes */}
                  {node.type === 'mule' && (
                    <motion.circle
                      cx={`${node.x}%`}
                      cy={`${node.y}%`}
                      r="25"
                      fill="#FF2D55"
                      opacity="0.2"
                      animate={{
                        r: [25, 35, 25],
                        opacity: [0.2, 0.4, 0.2],
                      }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  )}
                  
                  {/* Node circle */}
                  <motion.circle
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.5, delay: i * 0.1 }}
                    cx={`${node.x}%`}
                    cy={`${node.y}%`}
                    r="16"
                    fill={
                      node.type === 'mule' 
                        ? '#FF2D55' 
                        : node.type === 'suspect'
                        ? '#FBBF24'
                        : 'rgba(0, 212, 255, 0.2)'
                    }
                    stroke={
                      node.type === 'mule' 
                        ? '#FF2D55' 
                        : node.type === 'suspect'
                        ? '#FBBF24'
                        : '#00D4FF'
                    }
                    strokeWidth="2"
                    className="cursor-pointer hover:r-20 transition-all"
                    onClick={() => setSelectedNode(node)}
                  />
                  
                  {/* Label */}
                  <text
                    x={`${node.x}%`}
                    y={`${node.y + 6}%`}
                    textAnchor="middle"
                    fill="#F4F4F5"
                    fontSize="10"
                    fontWeight="600"
                    className="pointer-events-none"
                  >
                    {node.label}
                  </text>
                </g>
              ))}
            </svg>

            {/* Zoom Controls */}
            <div className="absolute bottom-4 right-4 flex gap-2">
              <Button size="sm" variant="outline" className="bg-black/50 border-white/10">
                +
              </Button>
              <Button size="sm" variant="outline" className="bg-black/50 border-white/10">
                -
              </Button>
            </div>
          </div>
        </Card>

        {/* Account Details Panel */}
        <motion.div
          key={selectedNode.id}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Card className={`bg-card border-border p-6 ${
            selectedNode.type === 'mule' 
              ? 'border-[#FF2D55]/30 shadow-[0_0_25px_rgba(255,45,85,0.2)]' 
              : ''
          }`}>
            <div className="flex items-start justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold mb-1">Account Details</h3>
                <p className="text-sm text-muted-foreground">{selectedNode.label}</p>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-xs font-semibold border ${
                  selectedNode.type === 'mule'
                    ? 'bg-[#FF2D55]/10 text-[#FF2D55] border-[#FF2D55]/30'
                    : selectedNode.type === 'suspect'
                    ? 'bg-[#FBBF24]/10 text-[#FBBF24] border-[#FBBF24]/30'
                    : 'bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]/30'
                }`}
              >
                {selectedNode.type.toUpperCase()}
              </span>
            </div>

            {/* Mule Risk Score */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-muted-foreground">Mule Risk Score</span>
                <span 
                  className={`text-2xl font-bold ${
                    selectedNode.risk > 70 ? 'text-[#FF2D55]' : 
                    selectedNode.risk > 40 ? 'text-[#FBBF24]' : 'text-[#00D4FF]'
                  }`}
                >
                  {selectedNode.risk}
                </span>
              </div>
              <div className="relative h-3 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${selectedNode.risk}%` }}
                  transition={{ duration: 0.8 }}
                  className={`absolute inset-y-0 left-0 rounded-full ${
                    selectedNode.risk > 70 
                      ? 'bg-gradient-to-r from-[#FF2D55] to-[#FF2D55]/70 shadow-[0_0_10px_rgba(255,45,85,0.6)]' 
                      : selectedNode.risk > 40
                      ? 'bg-gradient-to-r from-[#FBBF24] to-[#FBBF24]/70'
                      : 'bg-gradient-to-r from-[#00D4FF] to-[#00D4FF]/70'
                  }`}
                />
              </div>
            </div>

            {/* Spec-defined metrics */}
            <div className="space-y-2 mb-6">
              {[
                { label: "receiver_in_degree", value: selectedNode.type === "mule" ? "47" : "8" },
                { label: "sender_out_degree", value: selectedNode.type === "mule" ? "3" : "12" },
                { label: "receiver_total_amount", value: selectedNode.type === "mule" ? "$142,450" : "$18,200" },
                { label: "receiver_avg_amount", value: selectedNode.type === "mule" ? "$3,031" : "$2,275" },
                { label: "mule_risk_score_v1", value: String(selectedNode.risk), highlight: true },
                { label: "mule_alert_v1", value: selectedNode.type === "mule" ? "ALERT" : "CLEAR", alert: selectedNode.type === "mule" },
              ].map((m) => (
                <div key={m.label} className="flex items-center justify-between py-2.5 border-b border-border">
                  <span className="text-xs font-mono text-muted-foreground">{m.label}</span>
                  <span className={`text-sm font-bold font-mono ${
                    m.alert ? "text-[#FF2D55]" :
                    m.highlight && selectedNode.risk > 70 ? "text-[#FF2D55]" :
                    m.highlight ? "text-[#FBBF24]" : "text-foreground"
                  }`}>{m.value}</span>
                </div>
              ))}
            </div>

            {/* Graph Insight Summary */}
            <div className="bg-muted/40 border border-border rounded-lg p-4 mb-5">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Graph Insight Summary</h4>
              <div className="space-y-2 text-xs">
                {selectedNode.type === "mule" ? (
                  <>
                    <div className="flex items-start gap-2 text-[#FF2D55]"><AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" /><span>Potential mule receiver behavior detected</span></div>
                    <div className="flex items-start gap-2 text-[#FF2D55]"><AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" /><span>High-risk transaction concentration</span></div>
                    <div className="flex items-start gap-2 text-[#FBBF24]"><AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" /><span>Network exposure score: {selectedNode.risk}/100</span></div>
                  </>
                ) : (
                  <div className="flex items-start gap-2 text-[#00D4FF]"><span className="w-3 h-3 mt-0.5 flex-shrink-0">✓</span><span>No suspicious patterns detected</span></div>
                )}
              </div>
            </div>

            {/* Risk Indicators */}
            {selectedNode.type === 'mule' && (
              <div className="bg-[#FF2D55]/10 border border-[#FF2D55]/30 rounded-lg p-4 mb-6">
                <h4 className="text-sm font-semibold text-[#FF2D55] mb-3">Mule Indicators</h4>
                <ul className="space-y-2 text-xs text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-3 h-3 text-[#FF2D55] mt-0.5 flex-shrink-0" />
                    <span>Rapid fund movement (avg 2.3 hrs)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-3 h-3 text-[#FF2D55] mt-0.5 flex-shrink-0" />
                    <span>New account with high volume</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <AlertTriangle className="w-3 h-3 text-[#FF2D55] mt-0.5 flex-shrink-0" />
                    <span>Multiple geographic locations</span>
                  </li>
                </ul>
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-col gap-2">
              <Button className="w-full bg-[#FF2D55] hover:bg-[#FF2D55]/80 text-white rounded-lg">
                Flag for Investigation
              </Button>
              <Button variant="outline" className="w-full border-white/10 hover:bg-white/5 rounded-lg">
                View Full Report
              </Button>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
