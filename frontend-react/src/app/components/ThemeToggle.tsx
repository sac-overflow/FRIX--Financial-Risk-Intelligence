import { Sun, Moon } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export function ThemeToggle({ className = "" }: { className?: string }) {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      className={`relative w-14 h-7 rounded-full border transition-all duration-300 flex items-center px-1 ${
        isDark
          ? "bg-[#242428] border-white/10"
          : "bg-[#E4E4E8] border-black/10"
      } ${className}`}
    >
      <span
        className={`absolute flex items-center justify-center w-5 h-5 rounded-full shadow transition-all duration-300 ${
          isDark
            ? "translate-x-7 bg-[#00D4FF]"
            : "translate-x-0 bg-white"
        }`}
      >
        {isDark ? (
          <Moon className="w-3 h-3 text-[#0F0F12]" />
        ) : (
          <Sun className="w-3 h-3 text-[#F59E0B]" />
        )}
      </span>
    </button>
  );
}
