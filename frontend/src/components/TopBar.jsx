import React, { useState, useRef, useEffect } from "react";
import { Menu, Globe, ChevronDown, LogOut, RefreshCw } from "lucide-react";
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
  onLogout,
  firebaseUser,
  targetLanguage = "en",
  setTargetLanguage = () => {},
}) {
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const userMenuRef = useRef(null);

  const currentLang =
    LANGUAGE_OPTIONS.find((l) => l.id === targetLanguage) ||
    LANGUAGE_OPTIONS[0];

  const avatarInitial = (candidateName || "C").charAt(0).toUpperCase();
  const isLoggedIn = Boolean(firebaseUser);

  // Close user dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setShowUserMenu(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="h-16 px-4 sm:px-6 flex items-center justify-between border-b border-light-border dark:border-dark-border bg-light-surface/90 dark:bg-dark-surface/90 backdrop-blur-xl sticky top-0 z-30 transition-colors">
      {/* Left: hamburger when sidebar is collapsed */}
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

      {/* Right: Language, Theme, Profile */}
      <div className="flex items-center gap-2 sm:gap-3">

        {/* Language Dropdown */}
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
                  className={`w-full px-3 py-2 text-xs text-left flex items-center justify-between hover:text-purple-600 dark:hover:text-purple-400 hover:translate-x-1 transition-all duration-200 ${
                    targetLanguage === lang.id
                      ? "text-purple-600 dark:text-purple-300 font-bold"
                      : "text-light-muted dark:text-dark-muted"
                  }`}
                >
                  <span>{lang.label}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Theme Toggle */}
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />

        {/* Profile Avatar */}
        <div className="relative" ref={userMenuRef}>
          <button
            type="button"
            onClick={() => {
              if (isLoggedIn) {
                setShowUserMenu((prev) => !prev);
              } else {
                onOpenAuth();
              }
            }}
            className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-white flex items-center justify-center font-bold text-sm shadow-md hover:scale-105 active:scale-95 transition-transform focus:outline-none focus:ring-2 focus:ring-violet-400 focus:ring-offset-2 focus:ring-offset-transparent"
            title={isLoggedIn ? `${candidateName} — Account` : "Sign In / Register"}
            aria-label={isLoggedIn ? "Account menu" : "Open login"}
          >
            {avatarInitial}
          </button>

          {/* Dropdown — only shown when logged in */}
          {isLoggedIn && showUserMenu && (
            <div className="absolute right-0 top-full mt-2 w-56 rounded-xl border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface shadow-2xl z-50 overflow-hidden">
              {/* User info */}
              <div className="px-4 py-3 border-b border-light-border dark:border-dark-border">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
                    {avatarInitial}
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-light-text dark:text-dark-text truncate">{candidateName}</p>
                    <p className="text-[10px] text-light-muted dark:text-dark-muted truncate">
                      {firebaseUser?.email || "Logged in"}
                    </p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="py-1.5">
                <button
                  type="button"
                  onClick={() => {
                    setShowUserMenu(false);
                    onOpenAuth();
                  }}
                  className="w-full px-4 py-2.5 text-xs text-left flex items-center gap-2.5 text-light-muted dark:text-dark-muted hover:text-purple-600 dark:hover:text-purple-400 hover:translate-x-1 transition-all duration-200"
                >
                  <RefreshCw className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>Switch Account</span>
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowUserMenu(false);
                    if (onLogout) onLogout();
                  }}
                  className="w-full px-4 py-2.5 text-xs text-left flex items-center gap-2.5 text-red-500 hover:text-red-400 hover:translate-x-1 transition-all duration-200"
                >
                  <LogOut className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          )}
        </div>

      </div>
    </header>
  );
}

export default TopBar;
