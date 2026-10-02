import React, { useState } from "react";
import { Menu, Globe, ChevronDown } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import { LANGUAGE_OPTIONS } from "./Composer";

export function TopBar({
  onToggleSidebar,
  sidebarOpen,
  theme,
  onToggleTheme,
  onNewConversation,
  candidateName,
  onOpenAuth,
  targetLanguage = "en",
  setTargetLanguage = () => {},
}) {
  const [showLangMenu, setShowLangMenu] = useState(false);

  const currentLang =
    LANGUAGE_OPTIONS.find((l) => l.id === targetLanguage) ||
    LANGUAGE_OPTIONS[0];

  return (
    <header className="h-16 px-4 sm:px-6 flex items-center justify-between border-b border-light-border dark:border-dark-border bg-light-surface/90 dark:bg-dark-surface/90 backdrop-blur-xl sticky top-0 z-30 transition-colors">
      {/* Left: Show hamburger only when sidebar is collapsed */}
      <div className="flex items-center gap-2">
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

      {/* Right: Language Dropdown, Theme & Profile */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* TopBar Language Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowLangMenu((prev) => !prev)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-light-border dark:border-dark-border bg-light-surface2 dark:bg-dark-surface2 text-xs font-semibold text-light-text dark:text-dark-text hover:border-light-borderLight dark:hover:border-dark-borderLight transition-all"
            title="Select target response language"
          >
            <Globe className="w-3.5 h-3.5 text-purple-500 opacity-90" />
            <span className="hidden sm:inline font-medium text-light-muted dark:text-dark-muted">Lang:</span>
            <span>{currentLang.label}</span>
            <ChevronDown className="w-3 h-3 text-light-muted dark:text-dark-muted" />
          </button>

          {showLangMenu && (
            <div className="absolute right-0 top-full mt-1.5 w-40 py-1.5 rounded-xl glass-card border border-light-border dark:border-dark-border shadow-2xl z-50">
              {LANGUAGE_OPTIONS.map((lang) => (
                <button
                  key={lang.id}
                  type="button"
                  onClick={() => {
                    setTargetLanguage(lang.id);
                    setShowLangMenu(false);
                  }}
                  className={`w-full px-3 py-2 text-xs text-left flex items-center justify-between hover:bg-light-surface2 dark:hover:bg-dark-surface2 ${
                    targetLanguage === lang.id
                      ? "text-purple-600 dark:text-purple-300 font-bold bg-purple-500/10"
                      : "text-light-muted dark:text-dark-muted"
                  }`}
                >
                  <span>{lang.label}</span>
                </button>
              ))}
            </div>
          )}
        </div>

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
