import React, { useState, useRef, useEffect } from "react";
import { Menu, Globe, ChevronDown, LogOut, RefreshCw, User } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import { LANGUAGE_OPTIONS } from "./Composer";
import { FeesabilityLogo } from "./FeesabilityLogo";

export function TopBar({
  onToggleSidebar,
  sidebarOpen,
  theme,
  onToggleTheme,
  onNewConversation,
  candidateName,
  onOpenAuth,
  firebaseUser,
  targetLanguage = "en",
  setTargetLanguage = () => {},
  onNavigateLanding,
  onLogout,
}) {
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const profileMenuRef = useRef(null);

  // Close profile dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target)) {
        setShowProfileMenu(false);
      }
    }
    if (showProfileMenu) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showProfileMenu]);

  const isGuest =
    typeof window !== "undefined" &&
    localStorage.getItem("campus_ai_is_guest") === "true";
  const userEmail =
    typeof window !== "undefined"
      ? localStorage.getItem("campus_ai_user_email") || ""
      : "";

  const currentLang =
    LANGUAGE_OPTIONS.find((l) => l.id === targetLanguage) ||
    LANGUAGE_OPTIONS[0];

  const isLoggedIn = Boolean(
    firebaseUser ||
    (typeof window !== "undefined" &&
      (localStorage.getItem("campus_ai_is_authenticated") === "true" ||
        localStorage.getItem("campus_ai_is_guest") === "true"))
  );

  const displayName = candidateName || firebaseUser?.displayName || "Candidate";
  const displayEmail = firebaseUser?.email || userEmail || (isGuest ? "Guest Session" : "");
  const avatarInitial = (displayName || "C").charAt(0).toUpperCase();

  return (
    <header className="h-16 px-4 sm:px-6 flex items-center justify-between border-b border-light-border dark:border-dark-border bg-light-surface/90 dark:bg-dark-surface/90 backdrop-blur-xl sticky top-0 z-30 transition-colors">
      {/* Left: Show hamburger and logo when sidebar is collapsed */}
      <div className="flex items-center gap-3">
        {!sidebarOpen && (
          <>
            <button
              type="button"
              onClick={onToggleSidebar}
              aria-label="Open navigation"
              className="p-2 rounded-xl border border-light-border dark:border-dark-border text-light-muted dark:text-dark-muted hover:text-light-text dark:hover:text-dark-text hover:bg-light-surface2 dark:hover:bg-dark-surface2 transition-all focus:outline-none"
            >
              <Menu className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={onNavigateLanding}
              className="flex items-center gap-2 cursor-pointer hover:opacity-85 transition-opacity select-none text-left"
              title="Return to Landing Page"
            >
              <FeesabilityLogo className="w-5 h-5 text-light-text dark:text-white shrink-0" />
              <span className="text-base font-extrabold tracking-[-0.03em] text-light-text dark:text-white" style={{ fontFamily: "'Outfit', sans-serif" }}>
                feesability<span className="text-white">.</span>
              </span>
            </button>
          </>
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

        {/* Candidate Profile Avatar & Dropdown */}
        <div className="relative" ref={profileMenuRef}>
          <button
            type="button"
            onClick={() => {
              if (isLoggedIn) {
                setShowProfileMenu((prev) => !prev);
              } else {
                onOpenAuth();
              }
            }}
            className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-white flex items-center justify-center font-bold text-sm shadow-md hover:scale-105 active:scale-95 transition-transform focus:outline-none focus:ring-2 focus:ring-violet-400 focus:ring-offset-2 focus:ring-offset-transparent cursor-pointer"
            title={isLoggedIn ? `${displayName} — Account` : "Sign In / Register"}
            aria-label={isLoggedIn ? "Account menu" : "Open login"}
          >
            {avatarInitial}
          </button>

          {showProfileMenu && (
            <div className="absolute right-0 top-full mt-2 w-56 p-2 rounded-2xl glass-card border border-light-border dark:border-dark-border shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-150">
              {/* User info header */}
              <div className="px-3 py-2.5 border-b border-light-border dark:border-dark-border mb-1">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 text-white flex items-center justify-center font-bold text-xs shrink-0 shadow-sm">
                    {avatarInitial}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-bold text-light-text dark:text-dark-text truncate">
                      {displayName}
                    </p>
                    <p className="text-[10px] text-light-muted dark:text-dark-muted truncate">
                      {displayEmail || (isGuest ? "Guest Session" : "Candidate")}
                    </p>
                  </div>
                </div>
                {isGuest && (
                  <span className="inline-block mt-2 px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wider rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    Guest Mode
                  </span>
                )}
              </div>

              {/* Actions */}
              <div className="py-1">
                <button
                  type="button"
                  onClick={() => {
                    setShowProfileMenu(false);
                    onOpenAuth();
                  }}
                  className="w-full px-3 py-2 text-xs font-semibold text-light-muted dark:text-dark-muted hover:text-purple-600 dark:hover:text-purple-400 hover:bg-light-surface2 dark:hover:bg-dark-surface2 rounded-xl flex items-center gap-2.5 transition-all text-left cursor-pointer"
                >
                  <RefreshCw className="w-3.5 h-3.5 shrink-0" />
                  <span>Switch Account</span>
                </button>
                {onLogout && (
                  <button
                    type="button"
                    onClick={() => {
                      setShowProfileMenu(false);
                      onLogout();
                    }}
                    className="w-full px-3 py-2 text-xs font-semibold text-red-500 dark:text-red-400 hover:bg-red-500/10 rounded-xl flex items-center gap-2.5 transition-colors text-left cursor-pointer"
                  >
                    <LogOut className="w-3.5 h-3.5 shrink-0" />
                    <span>Sign Out</span>
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default TopBar;
