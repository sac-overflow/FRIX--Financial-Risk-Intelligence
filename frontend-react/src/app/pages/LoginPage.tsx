import { motion } from "motion/react";
import { Link, useNavigate } from "react-router";
import { Shield, Github } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { ThemeToggle } from "../components/ThemeToggle";
import { useTheme } from "../context/ThemeContext";
import { useState } from "react";

export function LoginPage() {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-background text-foreground grid grid-cols-1 lg:grid-cols-2">
      {/* Left Side - Visual */}
      <div
        className="relative hidden lg:flex items-center justify-center p-12 overflow-hidden"
        style={{ borderRight: "1px solid var(--frix-border)" }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-[#00D4FF]/10 via-transparent to-[#FF2D55]/5" />

        <motion.div
          className="relative z-10"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
        >
          <div className="relative w-96 h-96">
            {Array.from({ length: 6 }).map((_, row) =>
              Array.from({ length: 6 }).map((_, col) => {
                const isActive = (row + col) % 3 === 0;
                const isFraud = row === 2 && col === 3;
                return (
                  <motion.div
                    key={`${row}-${col}`}
                    className={`absolute w-3 h-3 rounded-full ${
                      isFraud
                        ? "bg-[#FF2D55]"
                        : isActive
                        ? "bg-[#00D4FF]"
                        : isDark
                        ? "bg-white/10"
                        : "bg-black/10"
                    }`}
                    style={{ left: `${col * 16.66}%`, top: `${row * 16.66}%` }}
                    animate={
                      isFraud
                        ? {
                            scale: [1, 1.5, 1],
                            boxShadow: [
                              "0 0 10px rgba(255,45,85,0.5)",
                              "0 0 25px rgba(255,45,85,0.9)",
                              "0 0 10px rgba(255,45,85,0.5)",
                            ],
                          }
                        : isActive
                        ? { opacity: [0.3, 1, 0.3] }
                        : {}
                    }
                    transition={{ duration: isFraud ? 1.5 : 2, repeat: Infinity, delay: (row + col) * 0.1 }}
                  />
                );
              })
            )}
            {Array.from({ length: 8 }).map((_, i) => (
              <motion.div
                key={i}
                className="absolute h-px bg-gradient-to-r from-transparent via-[#00D4FF]/30 to-transparent"
                style={{ width: "120%", left: "-10%", top: `${i * 12.5}%`, transform: `rotate(${i * 15}deg)`, transformOrigin: "center" }}
                animate={{ opacity: [0.1, 0.3, 0.1] }}
                transition={{ duration: 3, repeat: Infinity, delay: i * 0.2 }}
              />
            ))}
          </div>
          <div className="mt-12 text-center">
            <h2 className="text-2xl font-bold mb-2">Secure Access</h2>
            <p className="text-muted-foreground">Enterprise-grade authentication</p>
          </div>
        </motion.div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex items-center justify-center p-8 relative">
        {/* Theme toggle top-right */}
        <div className="absolute top-6 right-6">
          <ThemeToggle />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md"
        >
          <div className="flex items-center justify-center gap-2 mb-12">
            <div className="w-10 h-10 bg-gradient-to-br from-[#00D4FF] to-[#0099CC] rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-black" />
            </div>
            <span className="text-2xl font-bold tracking-tight">FRIX</span>
          </div>

          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">Welcome back</h1>
            <p className="text-muted-foreground">Sign in to access your risk console</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="rounded-lg px-4 py-3 focus:border-[#00D4FF] focus:ring-2 focus:ring-[#00D4FF]/20 transition-all"
                required
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password" className="text-sm font-medium">Password</Label>
                <a href="#" className="text-xs text-[#00D4FF] hover:underline">Forgot password?</a>
              </div>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="rounded-lg px-4 py-3 focus:border-[#00D4FF] focus:ring-2 focus:ring-[#00D4FF]/20 transition-all"
                required
              />
            </div>

            <Button
              type="submit"
              className="w-full py-6 rounded-lg border border-[#00D4FF]/50 shadow-[0_0_20px_rgba(0,212,255,0.3)] hover:shadow-[0_0_30px_rgba(0,212,255,0.5)] transition-all"
              style={{ background: isDark ? "#000" : "#0F0F12", color: "#fff" }}
            >
              Sign in
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-background px-2 text-muted-foreground">or continue with</span>
              </div>
            </div>

            <Button
              type="button"
              variant="outline"
              className="w-full py-6 rounded-lg transition-all hover:border-[#00D4FF]/50"
            >
              <Github className="w-5 h-5 mr-2" />
              Continue with GitHub
            </Button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-sm text-muted-foreground">
              Need access?{" "}
              <a href="#" className="text-[#00D4FF] hover:underline">Request enterprise access</a>
            </p>
          </div>

          <div className="mt-12 text-center">
            <Link to="/" className="text-sm text-muted-foreground hover:text-[#00D4FF] transition-colors">
              ← Back to home
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
