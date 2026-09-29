import React from "react";
import { Sun, Moon } from "lucide-react";

export function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === "dark";

  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={`Switch to ${isDark ? "light" : "dark"} mode`}
      className="p-2 rounded-xl border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface text-light-text dark:text-dark-text hover:bg-light-surface2 dark:hover:bg-dark-surface2 transition-all shadow-sm flex items-center justify-center"
      title={`Switch to ${isDark ? "light" : "dark"} mode`}
    >
      {isDark ? (
        <Sun className="w-4 h-4 hover:rotate-45 transition-transform duration-300" />
      ) : (
        <Moon className="w-4 h-4 hover:-rotate-12 transition-transform duration-300" />
      )}
    </button>
  );
}

export default ThemeToggle;
