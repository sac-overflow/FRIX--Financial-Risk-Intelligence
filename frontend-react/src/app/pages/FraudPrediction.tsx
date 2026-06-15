import { motion } from "motion/react";
import { useState } from "react";
import { AlertTriangle, CheckCircle, Play, Zap } from "lucide-react";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { predictFraud, type FraudPredictionResponse } from "../../services/fraudApi";

const TRANSACTION_TYPES = ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"];

type Prediction = FraudPredictionResponse;

const riskGradient = (score: number) => {
  if (score >= 80) return "#FF2D55";
  if (score >= 50) return "#FBBF24";
  return "#00D4FF";
};

export function FraudPrediction() {
  const [form, setForm] = useState({
    amount: "",
    transaction_type: "TRANSFER",
    oldbalanceOrg: "",
    newbalanceOrig: "",
    oldbalanceDest: "",
    newbalanceDest: "",
    sender_txn_count: "",
    receiver_txn_count: "",
  });

  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

const set = (key: string, val: string) => {
  setForm((f) => ({ ...f, [key]: val }));
  setPrediction(null);
  setError(null);
};

const handlePredict = async () => {
  setLoading(true);
  setError(null);

  try {
    const payload = {
      amount: Number(form.amount || 0),
      transaction_type: form.transaction_type,
      oldbalanceOrg: Number(form.oldbalanceOrg || 0),
      newbalanceOrig: Number(form.newbalanceOrig || 0),
      oldbalanceDest: Number(form.oldbalanceDest || 0),
      newbalanceDest: Number(form.newbalanceDest || 0),
      sender_txn_count: Number(form.sender_txn_count || 1),
      receiver_txn_count: Number(form.receiver_txn_count || 1),
    };

    const result = await predictFraud(payload);
    setPrediction(result);
  } catch (err) {
    setPrediction(null);
    setError(err instanceof Error ? err.message : "Failed to connect to FRIX API");
  } finally {
    setLoading(false);
  }
};


  const rc = prediction?.reason_codes;
  const reasonLabels: Record<keyof NonNullable<typeof rc>, string> = {
    high_risk_transaction_type: "High-risk transaction type",
    sender_emptied_account: "Sender emptied account",
    large_amount: "Large transaction amount",
    origin_balance_error: "Origin balance discrepancy",
    dest_balance_error: "Destination balance discrepancy",
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">Fraud Prediction Console</h1>
        <p className="text-muted-foreground">Submit a transaction for real-time ML fraud scoring</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <Card className="bg-card border-border p-8">
          <h3 className="text-lg font-semibold mb-6">Transaction Input</h3>
          <div className="space-y-4">
            {/* Transaction Type */}
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">transaction_type</Label>
              <div className="flex gap-2 flex-wrap">
                {TRANSACTION_TYPES.map((t) => (
                  <button
                    key={t}
                    onClick={() => set("transaction_type", t)}
                    className={`px-3 py-1.5 rounded text-xs font-mono border transition-all ${
                      form.transaction_type === t
                        ? "bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]/40"
                        : "bg-muted/40 text-muted-foreground border-border hover:border-[#00D4FF]/30"
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            {/* Amount */}
            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">amount</Label>
              <Input
                type="number"
                placeholder="e.g. 245000.00"
                value={form.amount}
                onChange={(e) => set("amount", e.target.value)}
                className="font-mono text-sm focus:border-[#00D4FF]/50 focus:ring-2 focus:ring-[#00D4FF]/20"
              />
            </div>

            {/* Balance grid */}
            <div className="grid grid-cols-2 gap-3">
              {[
                { key: "oldbalanceOrg", placeholder: "e.g. 500000.00" },
                { key: "newbalanceOrig", placeholder: "e.g. 255000.00" },
                { key: "oldbalanceDest", placeholder: "e.g. 0.00" },
                { key: "newbalanceDest", placeholder: "e.g. 245000.00" },
              ].map(({ key, placeholder }) => (
                <div key={key} className="space-y-1.5">
                  <Label className="text-xs text-muted-foreground">{key}</Label>
                  <Input
                    type="number"
                    placeholder={placeholder}
                    value={form[key as keyof typeof form]}
                    onChange={(e) => set(key, e.target.value)}
                    className="font-mono text-sm text-xs focus:border-[#00D4FF]/50"
                  />
                </div>
              ))}
            </div>

            {/* Transaction counts */}
            <div className="grid grid-cols-2 gap-3">
              {[
                { key: "sender_txn_count", placeholder: "e.g. 3" },
                { key: "receiver_txn_count", placeholder: "e.g. 1" },
              ].map(({ key, placeholder }) => (
                <div key={key} className="space-y-1.5">
                  <Label className="text-xs text-muted-foreground">{key}</Label>
                  <Input
                    type="number"
                    placeholder={placeholder}
                    value={form[key as keyof typeof form]}
                    onChange={(e) => set(key, e.target.value)}
                    className="font-mono text-sm focus:border-[#00D4FF]/50"
                  />
                </div>
              ))}
            </div>

            <Button
              onClick={handlePredict}
              disabled={loading}
              className="w-full bg-[#00D4FF] hover:bg-[#00B8E0] text-[#0F0F12] font-semibold py-5 mt-2 shadow-[0_0_20px_rgba(0,212,255,0.3)] hover:shadow-[0_0_30px_rgba(0,212,255,0.5)] transition-all"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-[#0F0F12]/30 border-t-[#0F0F12] rounded-full animate-spin" />
                  Running Model…
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Play className="w-4 h-4" /> Run Fraud Prediction
                </span>
              )}
            </Button>
          </div>
        </Card>

        {/* Output */}
<div className="space-y-5">
  {error && (
    <Card className="bg-card border-[#FF2D55]/40 p-5 text-[#FF2D55] text-sm font-mono">
      {error}
    </Card>
  )}

  {prediction ? (
            < motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="space-y-5"
            >
              {/* Main result card */}
              <Card
                className={`bg-card p-8 border ${
                  prediction.fraud_prediction === 1
                    ? "border-[#FF2D55]/40 shadow-[0_0_30px_rgba(255,45,85,0.15)]"
                    : "border-[#00D4FF]/30 shadow-[0_0_20px_rgba(0,212,255,0.1)]"
                }`}
              >
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <div className="text-xs text-muted-foreground mb-1 font-mono">fraud_prediction</div>
                    <div className="flex items-center gap-2">
                      {prediction.fraud_prediction === 1 ? (
                        <AlertTriangle className="w-5 h-5 text-[#FF2D55]" />
                      ) : (
                        <CheckCircle className="w-5 h-5 text-[#00D4FF]" />
                      )}
                      <span className={`text-2xl font-bold ${prediction.fraud_prediction === 1 ? "text-[#FF2D55]" : "text-[#00D4FF]"}`}>
                        {prediction.fraud_prediction === 1 ? "FRAUD DETECTED" : "LEGITIMATE"}
                      </span>
                    </div>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded border font-semibold ${
                      prediction.risk_level === "CRITICAL" || prediction.risk_level === "HIGH"
                        ? "bg-[#FF2D55]/10 text-[#FF2D55] border-[#FF2D55]/30"
                        : prediction.risk_level === "MEDIUM"
                        ? "bg-[#FBBF24]/10 text-[#FBBF24] border-[#FBBF24]/30"
                        : "bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]/30"
                    }`}
                  >
                    {prediction.risk_level}
                  </span>
                </div>

                {/* Metrics grid */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  {[
                    { label: "fraud_probability", value: prediction.fraud_probability.toFixed(3), color: riskGradient(prediction.risk_score_v1) },
                    { label: "risk_score_v1", value: prediction.risk_score_v1.toFixed(1), color: riskGradient(prediction.risk_score_v1) },
                    { label: "risk_level", value: prediction.risk_level, color: riskGradient(prediction.risk_score_v1) },
                    { label: "model_used", value: prediction.model_used, color: "#00D4FF" },
                  ].map((m) => (
                    <div key={m.label} className="p-3 rounded-lg bg-muted/40 border border-border">
                      <div className="text-xs text-muted-foreground font-mono mb-1">{m.label}</div>
                      <div
  className="text-lg font-bold font-mono break-words overflow-hidden"
  style={{ color: m.color }}
>
  {m.value}
</div>
                    </div>
                  ))}
                </div>

                {/* Risk Meter */}
                <div>
                  <div className="flex justify-between text-xs text-muted-foreground mb-2">
                    <span>LOW</span><span>MEDIUM</span><span>HIGH</span><span>CRITICAL</span>
                  </div>
                  <div className="relative h-3 rounded-full overflow-hidden bg-muted/40">
                    <div className="absolute inset-0 bg-gradient-to-r from-[#00D4FF] via-[#FBBF24] to-[#FF2D55] opacity-30" />
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${prediction.risk_score_v1}%` }}
                      transition={{ duration: 0.8, ease: "easeOut" }}
                      className="absolute top-0 left-0 h-full rounded-full"
                      style={{
                        background: `linear-gradient(90deg, #00D4FF, ${riskGradient(prediction.risk_score_v1)})`,
                        boxShadow: `0 0 12px ${riskGradient(prediction.risk_score_v1)}`,
                      }}
                    />
                  </div>
                  <div className="text-right text-xs font-mono mt-1" style={{ color: riskGradient(prediction.risk_score_v1) }}>
                    {prediction.risk_score_v1}
                  </div>
                </div>
              </Card>

              {/* Reason Codes */}
              <Card className="bg-card border-border p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Zap className="w-4 h-4 text-[#00D4FF]" />
                  <h3 className="font-semibold">Reason Codes</h3>
                </div>
                <div className="space-y-2">
                  {(Object.keys(rc!) as Array<keyof typeof rc>).map((key) => (
                    <div
                      key={key}
                      className={`flex items-center justify-between px-4 py-3 rounded-lg border ${
                        rc![key]
                          ? "bg-[#FF2D55]/5 border-[#FF2D55]/20"
                          : "bg-muted/30 border-border"
                      }`}
                    >
                      <span className="text-sm font-mono text-xs">{key}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">{reasonLabels[key]}</span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded border font-semibold ${
                            rc![key]
                              ? "bg-[#FF2D55]/10 text-[#FF2D55] border-[#FF2D55]/30"
                              : "bg-[#00D4FF]/10 text-[#00D4FF] border-[#00D4FF]/30"
                          }`}
                        >
                          {rc![key] ? "TRUE" : "FALSE"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </motion.div>
          ) : (
            <Card className="bg-card border-border p-12 flex flex-col items-center justify-center text-center h-full min-h-[400px]">
              <div className="w-16 h-16 rounded-full bg-[#00D4FF]/10 border border-[#00D4FF]/20 flex items-center justify-center mb-4">
                <Play className="w-7 h-7 text-[#00D4FF]" />
              </div>
              <h3 className="font-semibold mb-2">Ready to Score</h3>
              <p className="text-sm text-muted-foreground max-w-xs">Fill in the transaction fields and click "Run Fraud Prediction" to get a real-time risk assessment.</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
