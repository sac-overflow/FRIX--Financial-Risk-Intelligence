import { useState } from "react";
import { motion } from "motion/react";
import { Code2, Copy, Play, CheckCircle, Lock, Zap, Globe, Container, GitBranch, ExternalLink } from "lucide-react";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  getHealthStatus,
  predictFraud,
  sampleFraudPayload,
  type FraudPredictionResponse,
  type HealthResponse,
} from "../../services/fraudApi";


const endpoints = [
  {
    method: "GET",
    path: "/",
    description: "Root endpoint — returns platform name, version, and model status.",
    tag: "System",
    latency: "2ms avg",
  },
  {
    method: "GET",
    path: "/health",
    description: "Health check for API service, model readiness, and database connectivity.",
    tag: "System",
    latency: "3ms avg",
  },
  {
    method: "POST",
    path: "/predict-fraud",
    description: "Submit a transaction payload for real-time fraud scoring. Returns fraud_prediction, fraud_probability, risk_level, risk_score_v1, and reason codes.",
    tag: "Prediction",
    latency: "18ms avg",
  },
];

const requestExample = `# Copy cURL
curl -X POST http://localhost:8000/predict-fraud \\
  -H "Content-Type: application/json" \\
  -d '{
    "amount": 245000.0,
    "transaction_type": "TRANSFER",
    "oldbalanceOrg": 245000.0,
    "newbalanceOrig": 0.0,
    "oldbalanceDest": 0.0,
    "newbalanceDest": 245000.0,
    "sender_txn_count": 3,
    "receiver_txn_count": 1
  }'`;

const responseExample = `{
  "fraud_prediction": 1,
  "fraud_probability": 0.942,
  "risk_level": "HIGH",
  "risk_score_v1": 94.2,
  "model_used": "XGBoost v4.2.1 (Champion)",
  "reason_codes": {
    "high_risk_transaction_type": true,
    "sender_emptied_account": true,
    "large_amount": true,
    "origin_balance_error": false,
    "dest_balance_error": false
  },
  "latency_ms": 17,
  "timestamp": "2026-06-10T14:32:11.842Z"
}`;

const methodColors: Record<string, string> = {
  GET: "text-[#00D4FF] bg-[#00D4FF]/10 border-[#00D4FF]/30",
  POST: "text-[#A78BFA] bg-[#A78BFA]/10 border-[#A78BFA]/30",
  PUT: "text-[#FBBF24] bg-[#FBBF24]/10 border-[#FBBF24]/30",
  DELETE: "text-[#FF2D55] bg-[#FF2D55]/10 border-[#FF2D55]/30",
};

const tagColors: Record<string, string> = {
  Prediction: "text-[#A78BFA]",
  Transactions: "text-[#00D4FF]",
  Models: "text-[#FBBF24]",
  Accounts: "text-[#34D399]",
  System: "text-muted-foreground",
};

export function APIConsole() {
const [activeEndpoint, setActiveEndpoint] = useState(0);
const [copied, setCopied] = useState<string | null>(null);
const [loading, setLoading] = useState(false);
const [apiError, setApiError] = useState<string | null>(null);
const [healthResult, setHealthResult] = useState<HealthResponse | null>(null);
const [predictionResult, setPredictionResult] = useState<FraudPredictionResponse | null>(null);

  const copy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(null), 2000);
  };
const runEndpoint = async () => {
  setLoading(true);
  setApiError(null);

  try {
    const endpoint = endpoints[activeEndpoint];

    if (endpoint.path === "/health") {
      const result = await getHealthStatus();
      setHealthResult(result);
      setPredictionResult(null);
    } else if (endpoint.path === "/predict-fraud") {
      const result = await predictFraud(sampleFraudPayload);
      setPredictionResult(result);
      setHealthResult(null);
    } else {
      const result = await getHealthStatus();
      setHealthResult(result);
      setPredictionResult(null);
    }
  } catch (err) {
    setHealthResult(null);
    setPredictionResult(null);
    setApiError(err instanceof Error ? err.message : "Failed to call FRIX API");
  } finally {
    setLoading(false);
  }
};

const selectedEndpoint = endpoints[activeEndpoint];

const liveRequest =
  selectedEndpoint.path === "/health"
    ? "curl http://127.0.0.1:8000/health"
    : selectedEndpoint.path === "/"
    ? "curl http://127.0.0.1:8000/"
    : requestExample;

const liveResponse =
  predictionResult || healthResult
    ? JSON.stringify(predictionResult || healthResult, null, 2)
    : responseExample;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">API Console</h1>
        <p className="text-muted-foreground">Explore, test, and integrate the FRIX REST API</p>
      </div>

      {/* Status cards row */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
        {[
          { label: "API Version", value: "v1.4.2", icon: Code2, color: "#00D4FF" },
          { label: "Avg Latency", value: "18ms", icon: Zap, color: "#00D4FF" },
          { label: "Uptime SLA", value: "99.99%", icon: CheckCircle, color: "#00D4FF" },
          { label: "Endpoints", value: "3", icon: Globe, color: "#A1A1AA" },
          { label: "Docker Status", value: "Healthy", icon: Container, color: "#34D399" },
          { label: "CI Status", value: "Passing", icon: GitBranch, color: "#34D399" },
        ].map((stat) => (
          <Card key={stat.label} className="bg-card border-border p-4">
            <div className="flex items-center gap-2">
              <stat.icon className="w-4 h-4 flex-shrink-0" style={{ color: stat.color }} />
              <div>
                <div className="text-xs text-muted-foreground">{stat.label}</div>
                <div className="text-lg font-bold">{stat.value}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* API Key */}
      <Card className="bg-card border-[#00D4FF]/20 p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Lock className="w-4 h-4 text-[#00D4FF]" />
            <div>
              <div className="text-sm font-semibold mb-0.5">API Key — Production</div>
              <code className="text-xs font-mono text-muted-foreground">frix_prod_sk_••••••••••••••••••••••</code>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs px-2 py-1 bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/30 rounded">
              ACTIVE
            </span>
            <Button variant="outline" className="border-border hover:border-[#00D4FF]/50 text-xs h-8 gap-1.5">
              <ExternalLink className="w-3.5 h-3.5" /> Open Swagger Docs
            </Button>
            <Button variant="outline" className="border-border hover:border-[#00D4FF]/50 text-xs h-8">
              Rotate Key
            </Button>
          </div>
        </div>
      </Card>

      {/* Main console layout */}
      <div className="grid grid-cols-5 gap-6 min-h-[600px]">
        {/* Endpoint list */}
        <div className="col-span-2 space-y-2">
          <div className="text-xs text-muted-foreground uppercase tracking-wider mb-3 px-1">Endpoints</div>
          {endpoints.map((ep, i) => (
            <motion.button
              key={i}
              onClick={() => setActiveEndpoint(i)}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: i * 0.04 }}
              className={`w-full text-left p-3 rounded-lg border transition-all ${
                activeEndpoint === i
                  ? "bg-[#00D4FF]/5 border-[#00D4FF]/30"
                  : "bg-card border-border hover:border-white/10"
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span
                  className={`text-xs px-1.5 py-0.5 rounded border font-mono font-semibold ${methodColors[ep.method]}`}
                >
                  {ep.method}
                </span>
                <span className={`text-xs font-semibold ${tagColors[ep.tag]}`}>{ep.tag}</span>
              </div>
              <div className="font-mono text-xs text-foreground">{ep.path}</div>
              <div className="text-xs text-muted-foreground mt-1 leading-snug">{ep.description}</div>
            </motion.button>
          ))}
        </div>

        {/* Request / Response */}
        <div className="col-span-3 space-y-5">
          <Card className="bg-card border-border overflow-hidden">
            <div className="flex items-center justify-between px-5 py-3 border-b border-border">
              <div className="flex items-center gap-3">
                <span className={`text-xs px-1.5 py-0.5 rounded border font-mono font-semibold ${methodColors[endpoints[activeEndpoint].method]}`}>
                  {endpoints[activeEndpoint].method}
                </span>
                <code className="text-sm font-mono text-foreground">{endpoints[activeEndpoint].path}</code>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">{endpoints[activeEndpoint].latency}</span>
                <Button
  onClick={runEndpoint}
  disabled={loading}
  className="bg-[#00D4FF] hover:bg-[#00B8E0] text-[#0F0F12] h-7 px-3 text-xs"
>
  <Play className="w-3 h-3 mr-1.5" />
  {loading ? "Running..." : "Run"}
</Button>
              </div>
            </div>
            <div className="relative">
              <div className="flex items-center justify-between px-5 py-2 border-b border-border bg-muted/40">
                <span className="text-xs text-muted-foreground font-mono uppercase tracking-wider">Request</span>
                <button
                  onClick={() => copy(liveRequest, "req")}
                  className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  {copied === "req" ? (
                    <CheckCircle className="w-3.5 h-3.5 text-[#00D4FF]" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                  {copied === "req" ? "Copied" : "Copy"}
                </button>
              </div>
              <pre className="p-5 text-xs font-mono text-muted-foreground leading-relaxed overflow-x-auto whitespace-pre">
                <code>{liveRequest}</code>
              </pre>
            </div>
          </Card>
		{apiError && (
  <Card className="bg-card border-[#FF2D55]/40 p-4 text-[#FF2D55] text-xs font-mono">
    {apiError}
  </Card>
)}
          <Card className="bg-card border-border overflow-hidden">
            <div className="relative">
              <div className="flex items-center justify-between px-5 py-2 border-b border-border bg-muted/40">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground font-mono uppercase tracking-wider">Response</span>
                  <span className="text-xs px-2 py-0.5 bg-[#00D4FF]/10 text-[#00D4FF] border border-[#00D4FF]/30 rounded font-mono">
                    200 OK
                  </span>
                </div>
                <button
                  onClick={() => copy(liveResponse, "res")}
                  className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  {copied === "res" ? (
                    <CheckCircle className="w-3.5 h-3.5 text-[#00D4FF]" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                  {copied === "res" ? "Copied" : "Copy"}
                </button>
              </div>
              <pre className="p-5 text-xs font-mono leading-relaxed overflow-x-auto whitespace-pre">
               <code className="text-[#34D399]">{liveResponse}</code>
              </pre>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
