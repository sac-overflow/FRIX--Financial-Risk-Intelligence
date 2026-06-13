import { useState } from "react";
import { motion } from "motion/react";
import {
  GitBranch, GitCommit, CheckCircle, XCircle, Clock, Play,
  RefreshCw, Package, Shield, Cpu, Zap, ChevronRight, ExternalLink
} from "lucide-react";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";

type StageStatus = "success" | "running" | "failed" | "pending";

interface Stage {
  name: string;
  status: StageStatus;
  duration: string;
  icon: React.ElementType;
}

interface Pipeline {
  id: string;
  branch: string;
  commit: string;
  author: string;
  message: string;
  triggered: string;
  status: StageStatus;
  stages: Stage[];
}

const pipelines: Pipeline[] = [
  {
    id: "run-4821",
    branch: "main",
    commit: "a9f3b2c",
    author: "Elena Vargas",
    message: "feat: promote XGBoost v4.2.1 to champion",
    triggered: "2 min ago",
    status: "running",
    stages: [
      { name: "Push to GitHub", status: "success", duration: "—", icon: Shield },
      { name: "Run Tests", status: "success", duration: "0:48", icon: CheckCircle },
      { name: "Build Docker Image", status: "running", duration: "—", icon: Cpu },
      { name: "Push Image", status: "pending", duration: "—", icon: Zap },
      { name: "Deploy Service", status: "pending", duration: "—", icon: Package },
    ],
  },
  {
    id: "run-4820",
    branch: "release/lightgbm-v3.1",
    commit: "e7d1a4f",
    author: "Amir Patel",
    message: "chore: update LightGBM hyperparams — lower min_child_samples",
    triggered: "47 min ago",
    status: "success",
    stages: [
      { name: "Push to GitHub", status: "success", duration: "—", icon: Shield },
      { name: "Run Tests", status: "success", duration: "0:52", icon: CheckCircle },
      { name: "Build Docker Image", status: "success", duration: "1:44", icon: Cpu },
      { name: "Push Image", status: "success", duration: "0:38", icon: Zap },
      { name: "Deploy Service", status: "success", duration: "0:55", icon: Package },
    ],
  },
  {
    id: "run-4819",
    branch: "feature/graph-risk-v2.2",
    commit: "b2c8d5e",
    author: "Nadia Chen",
    message: "fix: reduce GNN inference memory footprint by 30%",
    triggered: "2 hr ago",
    status: "failed",
    stages: [
      { name: "Push to GitHub", status: "success", duration: "—", icon: Shield },
      { name: "Run Tests", status: "success", duration: "0:44", icon: CheckCircle },
      { name: "Build Docker Image", status: "failed", duration: "2:47", icon: Cpu },
      { name: "Push Image", status: "pending", duration: "—", icon: Zap },
      { name: "Deploy Service", status: "pending", duration: "—", icon: Package },
    ],
  },
  {
    id: "run-4818",
    branch: "main",
    commit: "f1a3c6d",
    author: "Luca Romano",
    message: "perf: batch inference pipeline — 2× throughput on GPU nodes",
    triggered: "5 hr ago",
    status: "success",
    stages: [
      { name: "Push to GitHub", status: "success", duration: "—", icon: Shield },
      { name: "Run Tests", status: "success", duration: "0:51", icon: CheckCircle },
      { name: "Build Docker Image", status: "success", duration: "1:38", icon: Cpu },
      { name: "Push Image", status: "success", duration: "0:41", icon: Zap },
      { name: "Deploy Service", status: "success", duration: "0:29", icon: Package },
    ],
  },
];

const statusColor: Record<StageStatus, string> = {
  success: "text-[#00D4FF]",
  running: "text-[#FBBF24]",
  failed: "text-[#FF2D55]",
  pending: "text-muted-foreground",
};

const statusBg: Record<StageStatus, string> = {
  success: "bg-[#00D4FF]/10 border-[#00D4FF]/30",
  running: "bg-[#FBBF24]/10 border-[#FBBF24]/30",
  failed: "bg-[#FF2D55]/10 border-[#FF2D55]/30 shadow-[0_0_12px_rgba(255,45,85,0.15)]",
  pending: "bg-muted/40 border-border",
};

const StageIcon = ({ stage }: { stage: Stage }) => {
  if (stage.status === "running") return <RefreshCw className={`w-4 h-4 ${statusColor[stage.status]} animate-spin`} />;
  if (stage.status === "success") return <CheckCircle className={`w-4 h-4 ${statusColor[stage.status]}`} />;
  if (stage.status === "failed") return <XCircle className={`w-4 h-4 ${statusColor[stage.status]}`} />;
  return <Clock className={`w-4 h-4 ${statusColor[stage.status]}`} />;
};

export function CICD() {
  const [selected, setSelected] = useState<string | null>("run-4821");

  const selectedPipeline = pipelines.find((p) => p.id === selected);

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">CI/CD Pipeline</h1>
          <p className="text-muted-foreground">Model deployment workflows, shadow testing, and champion promotion</p>
        </div>
        <Button className="bg-[#00D4FF] hover:bg-[#00B8E0] text-[#0F0F12] gap-2">
          <Play className="w-4 h-4" /> Trigger Deploy
        </Button>
      </div>

      {/* Spec summary cards */}
      <div className="grid grid-cols-5 gap-4">
        {[
          { label: "CI Pipeline", value: "GitHub Actions", sub: "Passed ✓", color: "#34D399" },
          { label: "Docker Build", value: "frix-fastapi", sub: "Healthy · latest", color: "#00D4FF" },
          { label: "Test Coverage", value: "3 / 3 passed", sub: "pytest · 100%", color: "#34D399" },
          { label: "Deployment Target", value: "Production", sub: "us-east-1", color: "#00D4FF" },
          { label: "Model Artifact Strategy", value: "Versioned", sub: "S3 · joblib", color: "#A1A1AA" },
        ].map((s) => (
          <Card key={s.label} className="bg-card border-border p-5">
            <div className="text-xs text-muted-foreground mb-1">{s.label}</div>
            <div className="text-sm font-bold" style={{ color: s.color }}>{s.value}</div>
            <div className="text-xs text-muted-foreground mt-0.5 font-mono">{s.sub}</div>
          </Card>
        ))}
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total Runs", value: "4,821", color: "#00D4FF" },
          { label: "Success Rate", value: "97.2%", color: "#00D4FF" },
          { label: "Avg Duration", value: "3m 58s", color: "#A1A1AA" },
          { label: "Active Runs", value: "1", color: "#FBBF24" },
        ].map((s) => (
          <Card key={s.label} className="bg-card border-border p-5">
            <div className="text-xs text-muted-foreground mb-1">{s.label}</div>
            <div className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-5 gap-6">
        {/* Pipeline list */}
        <div className="col-span-2 space-y-3">
          <div className="text-xs text-muted-foreground uppercase tracking-wider mb-2">Recent Runs</div>
          {pipelines.map((pipeline, i) => (
            <motion.button
              key={pipeline.id}
              onClick={() => setSelected(pipeline.id)}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: i * 0.07 }}
              className={`w-full text-left p-4 rounded-lg border transition-all ${
                selected === pipeline.id
                  ? "bg-[#00D4FF]/5 border-[#00D4FF]/30"
                  : `${statusBg[pipeline.status]} hover:border-white/15`
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {pipeline.status === "running" && (
                    <RefreshCw className="w-3.5 h-3.5 text-[#FBBF24] animate-spin" />
                  )}
                  {pipeline.status === "success" && (
                    <CheckCircle className="w-3.5 h-3.5 text-[#00D4FF]" />
                  )}
                  {pipeline.status === "failed" && (
                    <XCircle className="w-3.5 h-3.5 text-[#FF2D55]" />
                  )}
                  <span className="text-xs font-mono text-muted-foreground">#{pipeline.id}</span>
                </div>
                <span className="text-xs text-muted-foreground">{pipeline.triggered}</span>
              </div>
              <div className="text-sm font-medium leading-snug mb-1 text-foreground">{pipeline.message}</div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <GitBranch className="w-3 h-3" />
                <span className="font-mono">{pipeline.branch}</span>
                <span>·</span>
                <GitCommit className="w-3 h-3" />
                <span className="font-mono">{pipeline.commit}</span>
              </div>
            </motion.button>
          ))}
        </div>

        {/* Stage detail */}
        <div className="col-span-3">
          {selectedPipeline && (
            <motion.div
              key={selectedPipeline.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="bg-card border-border p-6">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className={`text-xs px-2 py-0.5 rounded border font-semibold ${
                          statusBg[selectedPipeline.status]
                        } ${statusColor[selectedPipeline.status]}`}
                      >
                        {selectedPipeline.status.toUpperCase()}
                      </span>
                      <span className="text-xs font-mono text-muted-foreground">#{selectedPipeline.id}</span>
                    </div>
                    <h3 className="text-base font-semibold leading-snug max-w-md">{selectedPipeline.message}</h3>
                    <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                      <span>{selectedPipeline.author}</span>
                      <span>·</span>
                      <GitBranch className="w-3 h-3" />
                      <span className="font-mono">{selectedPipeline.branch}</span>
                      <span>·</span>
                      <span>{selectedPipeline.triggered}</span>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    className="border-white/10 hover:border-white/20 text-xs h-8 gap-1.5"
                  >
                    <ExternalLink className="w-3.5 h-3.5" /> Logs
                  </Button>
                </div>

                {/* Pipeline stages visualization */}
                <div className="flex items-center gap-0 mb-8">
                  {selectedPipeline.stages.map((stage, i) => (
                    <div key={stage.name} className="flex items-center flex-1">
                      <div className="flex-1">
                        <div
                          className={`h-1.5 rounded-full ${
                            stage.status === "success"
                              ? "bg-[#00D4FF]"
                              : stage.status === "running"
                              ? "bg-[#FBBF24] animate-pulse"
                              : stage.status === "failed"
                              ? "bg-[#FF2D55]"
                              : "bg-white/10"
                          }`}
                        />
                      </div>
                      {i < selectedPipeline.stages.length - 1 && (
                        <ChevronRight className="w-3 h-3 text-muted-foreground flex-shrink-0 mx-1" />
                      )}
                    </div>
                  ))}
                </div>

                {/* Stage cards */}
                <div className="space-y-3">
                  {selectedPipeline.stages.map((stage, i) => (
                    <motion.div
                      key={stage.name}
                      initial={{ opacity: 0, x: 12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.25, delay: i * 0.06 }}
                      className={`flex items-center gap-4 p-4 rounded-lg border ${statusBg[stage.status]}`}
                    >
                      <StageIcon stage={stage} />
                      <stage.icon className="w-4 h-4 text-muted-foreground" />
                      <div className="flex-1">
                        <div className="text-sm font-semibold">{stage.name}</div>
                        {stage.status === "running" && (
                          <div className="text-xs text-[#FBBF24] mt-0.5">In progress…</div>
                        )}
                        {stage.status === "failed" && (
                          <div className="text-xs text-[#FF2D55] mt-0.5">Build failed — check logs</div>
                        )}
                      </div>
                      <div className="text-xs font-mono text-muted-foreground">{stage.duration}</div>
                    </motion.div>
                  ))}
                </div>
              </Card>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
