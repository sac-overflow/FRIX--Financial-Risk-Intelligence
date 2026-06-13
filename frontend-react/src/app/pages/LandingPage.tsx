import { motion } from "motion/react";
import { Link } from "react-router";
import { Activity, Shield, TrendingUp, Zap } from "lucide-react";
import { Button } from "../components/ui/button";
import { ThemeToggle } from "../components/ThemeToggle";
import { useTheme } from "../context/ThemeContext";

export function LandingPage() {
  const { isDark } = useTheme();

  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden">
      {/* Header */}
      <header
        className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl"
        style={{
          background: isDark ? "rgba(15,15,18,0.85)" : "rgba(248,248,250,0.85)",
          borderBottom: "1px solid var(--frix-border)",
        }}
      >
        <div className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
  <div className="w-8 h-8 bg-gradient-to-br from-[#00D4FF] to-[#0099CC] rounded-md flex items-center justify-center">
    <Shield className="w-5 h-5 text-black" />
  </div>
  <span className="text-xl font-semibold tracking-tight">FRIX</span>
</Link>

<nav className="flex items-center gap-6">
  <a href="#features" className="text-sm text-muted-foreground hover:text-[#00D4FF] transition-colors">Features</a>

  <Link to="/dashboard" className="text-sm text-muted-foreground hover:text-[#00D4FF] transition-colors">
    Platform
  </Link>

  <Link to="/dashboard/model-engine" className="text-sm text-muted-foreground hover:text-[#00D4FF] transition-colors">
    Model Engine
  </Link>

  <ThemeToggle />

  <Link to="/login">
    <Button variant="ghost" className="text-sm">Sign In</Button>
  </Link>
</nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1
                className="text-6xl font-bold leading-tight mb-6 text-foreground"
              >
                Financial Risk Intelligence,{" "}
                <span className="bg-gradient-to-r from-[#00D4FF] to-[#0099CC] bg-clip-text text-transparent">
                  engineered
                </span>{" "}
                for modern fraud detection.
              </h1>
              <p className="text-lg text-muted-foreground mb-8 leading-relaxed max-w-xl">
                Detect fraud, expose mule-risk patterns, compare ML models, and operationalize
                real-time risk decisions from one intelligent platform.
              </p>
              <div className="flex gap-4">
                <Link to="/dashboard">
                  <Button
                    className="px-8 py-6 rounded-lg border border-[#00D4FF]/50 shadow-[0_0_20px_rgba(0,212,255,0.3)] hover:shadow-[0_0_30px_rgba(0,212,255,0.5)] transition-all"
                    style={{ background: isDark ? "#000" : "#0F0F12", color: "#fff" }}
                  >
                    Open Risk Console
                  </Button>
                </Link>
                <Link to="/dashboard/model-engine">
                  <Button variant="outline" className="px-8 py-6 rounded-lg transition-all hover:border-[#00D4FF]/50">
                    View Model Engine
                  </Button>
                </Link>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-8 mt-16">
                {[["99.7%", "Detection Rate"], ["<50ms", "Avg Latency"], ["24/7", "Monitoring"]].map(([val, label]) => (
                  <div key={label}>
                    <div className="text-3xl font-bold text-[#00D4FF]">{val}</div>
                    <div className="text-sm text-muted-foreground mt-1">{label}</div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Hero Visual */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              <div
                className="relative rounded-2xl p-8 shadow-2xl"
                style={{
                  background: isDark
                    ? "linear-gradient(135deg, #1A1A1E, #0F0F12)"
                    : "linear-gradient(135deg, #FFFFFF, #F0F0F4)",
                  border: "1px solid var(--frix-border)",
                }}
              >
                {/* Network Graph Visualization */}
                <div className="relative h-96 flex items-center justify-center">
                  <motion.div
                    animate={{
                      scale: [1, 1.1, 1],
                      boxShadow: [
                        "0 0 20px rgba(0,212,255,0.5)",
                        "0 0 40px rgba(0,212,255,0.8)",
                        "0 0 20px rgba(0,212,255,0.5)",
                      ],
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute w-20 h-20 bg-gradient-to-br from-[#00D4FF] to-[#0099CC] rounded-full flex items-center justify-center"
                  >
                    <Activity className="w-10 h-10 text-black" />
                  </motion.div>

                  {[0, 60, 120, 180, 240, 300].map((angle, i) => {
                    const isRisk = i === 1 || i === 4;
                    const radius = 140;
                    const x = Math.cos((angle * Math.PI) / 180) * radius;
                    const y = Math.sin((angle * Math.PI) / 180) * radius;
                    return (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1, scale: isRisk ? [1, 1.2, 1] : 1 }}
                        transition={{ duration: isRisk ? 1.5 : 0.6, delay: i * 0.1, repeat: isRisk ? Infinity : 0 }}
                        className="absolute"
                        style={{ left: `calc(50% + ${x}px)`, top: `calc(50% + ${y}px)`, transform: "translate(-50%, -50%)" }}
                      >
                        <div
                          className="absolute w-0.5"
                          style={{
                            height: `${radius}px`,
                            background: isRisk ? "rgba(255,45,85,0.3)" : "rgba(0,212,255,0.2)",
                            transformOrigin: "top center",
                            transform: `rotate(${angle + 180}deg)`,
                            left: "50%",
                            top: "50%",
                          }}
                        />
                        <div
                          className={`w-12 h-12 rounded-full flex items-center justify-center ${
                            isRisk
                              ? "bg-[#FF2D55]/20 border-2 border-[#FF2D55] shadow-[0_0_15px_rgba(255,45,85,0.6)]"
                              : "bg-[#00D4FF]/10 border border-[#00D4FF]/50"
                          }`}
                        >
                          {isRisk && <div className="w-2 h-2 bg-[#FF2D55] rounded-full" />}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>

                {/* Floating Card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.8 }}
                  className="absolute -bottom-4 -right-4 backdrop-blur-xl rounded-xl p-4 shadow-2xl"
                  style={{
                    background: isDark ? "rgba(0,0,0,0.9)" : "rgba(255,255,255,0.95)",
                    border: "1px solid var(--frix-border)",
                  }}
                >
                  <div className="text-xs text-muted-foreground mb-1">Real-time Risk Score</div>
                  <div className="text-3xl font-bold text-[#FF2D55]">87.4</div>
                  <div className="text-xs text-[#FF2D55] mt-1">⚠ High Risk Detected</div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </div>

        <div className="absolute inset-0 bg-gradient-to-b from-[#00D4FF]/5 via-transparent to-transparent pointer-events-none" />
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4">Enterprise-grade fraud detection</h2>
            <p className="text-muted-foreground text-lg">Powered by adaptive machine learning and real-time intelligence</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Shield, title: "Fraud Detection", description: "Real-time ML-powered fraud scoring with 99.7% accuracy", color: "#00D4FF" },
              { icon: Activity, title: "Mule Risk Analysis", description: "Graph-based network analysis to identify money mule patterns", color: "#FF2D55" },
              { icon: TrendingUp, title: "Adaptive Models", description: "Compare and deploy ML models with champion-challenger framework", color: "#00D4FF" },
              { icon: Zap, title: "Real-time API", description: "Sub-50ms latency for instant risk decisions at scale", color: "#00D4FF" },
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.1 }}
                className="rounded-xl p-6 transition-all"
                style={{
                  background: "var(--card)",
                  border: "1px solid var(--frix-border)",
                }}
              >
                <div
                  className="w-12 h-12 rounded-lg flex items-center justify-center mb-4"
                  style={{
                    background: `linear-gradient(135deg, ${feature.color}20, ${feature.color}10)`,
                    border: `1px solid ${feature.color}40`,
                  }}
                >
                  <feature.icon className="w-6 h-6" style={{ color: feature.color }} />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-8 mt-20" style={{ borderTop: "1px solid var(--frix-border)" }}>
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-[#00D4FF] to-[#0099CC] rounded-md flex items-center justify-center">
              <Shield className="w-5 h-5 text-black" />
            </div>
            <span className="text-lg font-semibold">FRIX</span>
          </div>
          <div className="text-sm text-muted-foreground">© 2026 FRIX. Financial Risk Intelligence Platform.</div>
        </div>
      </footer>
    </div>
  );
}
