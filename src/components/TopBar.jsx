import React from "react";
import { Menu } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";

export function TopBar({
  onToggleSidebar,
  sidebarOpen,
  theme,
  onToggleTheme,
  onNewConversation,
  candidateName,
  onOpenAuth,
}) {

  return (
    <header className="h-16 px-4 sm:px-6 flex items-center justify-between border-b border-light-border dark:border-dark-border bg-light-surface/90 dark:bg-dark-surface/90 backdrop-blur-xl sticky top-0 z-30 transition-colors">

      {/* Left: Show hamburger only when sidebar is collapsed */}
      <div className="flex items-center">
        {!sidebarOpen && (
          <button
            type="button"
            onClick={onToggleSidebar}
            aria-label="Open navigation"
            className="p-2 rounded-xl border border-light-border dark:border-dark-border text-light-muted dark:text-dark-muted hover:text-light-text dark:hover:text-dark-text hover:bg-light-surface2 dark:hover:bg-dark-surface2 transition-all focus:outline-none"
          >
            <Menu className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Right: Theme & Profile */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Minimalist Theme Switcher */}
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />

        {/* Candidate Profile Avatar */}
        <button
          type="button"
          onClick={onOpenAuth}
          className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-white flex items-center justify-center font-bold text-sm shadow-md hover:scale-105 active:scale-95 transition-transform focus:outline-none focus:ring-2 focus:ring-violet-400 focus:ring-offset-2 focus:ring-offset-transparent"
          title={`${candidateName || "Candidate"} — Profile & Admissions Login`}
          aria-label="Open profile"
        >
          {(candidateName || "C").charAt(0).toUpperCase()}
        </button>
      </div>
    </header>
  );
}

export default TopBar;
