import React, { useState } from "react";
import { X, Lock, Mail, User, ArrowRight, Sparkles, CheckCircle2, ShieldCheck } from "lucide-react";
import { OrbLogo } from "./OrbLogo";

export function AuthModal({ isOpen, onClose, candidateName, onSaveCandidate, onAuthSuccess }) {
  const [activeTab, setActiveTab] = useState("login"); // 'login' | 'signup'
  const [nameInput, setNameInput] = useState(candidateName || "");
  const [emailInput, setEmailInput] = useState("");
  const [passwordInput, setPasswordInput] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [keepLoggedIn, setKeepLoggedIn] = useState(true);
  const [authMessage, setAuthMessage] = useState("");

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (activeTab === "signup" && passwordInput !== confirmPassword) {
      setAuthMessage("Your passwords do not match.");
      return;
    }
    setAuthMessage("Account authentication will be available after the database is connected. Continue as a guest for now.");
  };

  const handleGuestAccess = () => {
    const displayName = nameInput.trim() || candidateName || "Guest";
    onSaveCandidate(displayName);
    if (onAuthSuccess) {
      onAuthSuccess(displayName);
    } else {
      onClose();
    }
  };

  const handleGoogleSignIn = () => {
    setAuthMessage("Google sign-in will be available when database authentication is integrated.");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
      {/* Deep Dark Blurred Backdrop */}
      <div
        className="fixed inset-0 bg-[#030712]/85 backdrop-blur-2xl transition-opacity"
        onClick={onClose}
      />

      {/* Decorative Ambient Radial Glows */}
      <div className="fixed top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-cyan-500/15 blur-[120px] pointer-events-none" />
      <div className="fixed bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-96 h-96 rounded-full bg-blue-600/15 blur-[120px] pointer-events-none" />

      {/* Split-Layout Glassmorphic Modal Card */}
      <div className="relative w-full max-w-4xl bg-[#0a1424]/95 backdrop-blur-3xl rounded-3xl text-white shadow-2xl border border-slate-700/60 z-10 overflow-hidden grid grid-cols-1 lg:grid-cols-12 min-h-[580px]">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 z-30 p-2 rounded-full bg-slate-800/60 hover:bg-slate-700/80 text-slate-400 hover:text-white transition-colors"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* ──────────────────── LEFT COLUMN: VISUAL SHOWCASE ──────────────────── */}
        <div className="lg:col-span-5 p-6 sm:p-8 flex flex-col justify-between relative overflow-hidden bg-gradient-to-br from-[#071324] via-[#091a30] to-[#040a14] border-b lg:border-b-0 lg:border-r border-slate-800/60">
          {/* Subtle Grid / Radial Effect */}
          <div className="absolute inset-0 pointer-events-none opacity-40 bg-[radial-gradient(circle_at_50%_40%,#06b6d4_0%,transparent_60%)] filter blur-3xl" />

          {/* Top Brand Header */}
          <div className="relative z-10 flex items-center gap-2.5">
            <OrbLogo size="sm" animated={false} interactive={false} />
            <span className="text-sm font-extrabold tracking-tight text-white font-heading">
              FEESABILITY
            </span>
          </div>

          {/* Middle Floating Glass Stats Card */}
          <div className="relative z-10 my-8 space-y-6">
            {/* Glassmorphic User Readiness Badge */}
            <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-700/50 backdrop-blur-md shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-md">
                    <User className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white">New Candidate</div>
                    <div className="text-[10px] text-slate-400">Student Helpdesk</div>
                  </div>
                </div>
                <span className="text-[9px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  INITIALIZING
                </span>
              </div>

              {/* Readiness Progress Bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-[10px] text-slate-400">
                  <span>Admissions Readiness</span>
                  <span className="text-cyan-400 font-mono">100% Ready</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden flex">
                  <div className="w-full bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-500 rounded-full" />
                </div>
              </div>
              <div className="text-[10px] text-slate-400 flex items-center gap-1.5">
                <Sparkles className="w-3 h-3 text-cyan-400" />
                <span>24/7 AI query engine active</span>
              </div>
            </div>

            {/* Left Headline */}
            <div className="space-y-2">
              <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight leading-snug font-heading">
                Your admissions journey{" "}
                <span className="italic text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400">
                  starts here.
                </span>
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Get instant verified data on B.Tech CSE fees, CUEE 2026 eligibility, and Amrit Kaal merit scholarships.
              </p>
            </div>
          </div>

          {/* Bottom Pagination Dots */}
          <div className="relative z-10 flex items-center gap-1.5 pt-2">
            <span className="w-5 h-1.5 rounded-full bg-cyan-400" />
            <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
            <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
          </div>
        </div>

        {/* ──────────────────── RIGHT COLUMN: AUTH FORM ──────────────────── */}
        <div className="lg:col-span-7 p-6 sm:p-10 flex flex-col justify-between space-y-6">
          <div className="space-y-6">
            {/* Form Header */}
            <div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
                {activeTab === "login" ? "Welcome Back" : "Create Account"}
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                {activeTab === "login"
                  ? "Ready to continue your admissions quest?"
                  : "Create your FEESABILITY account"}
              </p>
            </div>

            {/* Tab Switcher (Login | Sign Up) */}
            <div className="flex items-center border-b border-slate-800 text-sm font-semibold">
              <button
                type="button"
                onClick={() => { setActiveTab("login"); setAuthMessage(""); }}
                className={`pb-3 px-4 transition-all relative ${
                  activeTab === "login"
                    ? "text-white font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Login
                {activeTab === "login" && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
                )}
              </button>
              <button
                type="button"
                onClick={() => { setActiveTab("signup"); setAuthMessage(""); }}
                className={`pb-3 px-4 transition-all relative ${
                  activeTab === "signup"
                    ? "text-white font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Sign Up
                {activeTab === "signup" && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
                )}
              </button>
            </div>

            {/* Form Inputs */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Name Field (for Sign Up or optional) */}
              {activeTab === "signup" && (
                <div className="space-y-1.5">
                  <label className="text-[11px] font-semibold text-slate-300">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                    <input
                      type="text"
                      required
                      placeholder="Candidate / Student Name"
                      value={nameInput}
                      onChange={(e) => setNameInput(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700/80 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
                    />
                  </div>
                </div>
              )}

              {/* Email Address / Application ID */}
              <div className="space-y-1.5">
                <label className="text-[11px] font-semibold text-slate-300">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="email"
                    required
                    placeholder="hero@example.com"
                    value={emailInput}
                    onChange={(e) => setEmailInput(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700/80 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <label className="text-[11px] font-semibold text-slate-300">
                    Password
                  </label>
                  {activeTab === "login" && (
                    <button
                      type="button"
                      onClick={() => setAuthMessage("Password recovery will be available after account authentication is integrated.")}
                      className="text-[11px] text-cyan-400 hover:text-cyan-300 hover:underline transition-colors"
                    >
                      Forgot password?
                    </button>
                  )}
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    value={passwordInput}
                    onChange={(e) => setPasswordInput(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700/80 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
                  />
                </div>
              </div>

              {/* Confirm Password (for Sign Up) */}
              {activeTab === "signup" && (
                <div className="space-y-1.5">
                  <label className="text-[11px] font-semibold text-slate-300">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                    <input
                      type="password"
                      required
                      placeholder="••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700/80 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
                    />
                  </div>
                </div>
              )}

              {/* Checkbox Options */}
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="keep-logged"
                  checked={keepLoggedIn}
                  onChange={(e) => setKeepLoggedIn(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-0 focus:ring-offset-0 cursor-pointer"
                />
                <label
                  htmlFor="keep-logged"
                  className="text-xs text-slate-400 select-none cursor-pointer"
                >
                  {activeTab === "login"
                    ? "Keep me logged in to the portal"
                    : "I agree to Admissions Terms & Privacy Policy"}
                </label>
              </div>

              {/* Primary Action CTA Button */}
              <button
                type="submit"
                className="w-full py-3 px-6 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:opacity-95 shadow-lg shadow-cyan-500/25 active:scale-[0.99] transition-all flex items-center justify-center gap-2 mt-2"
              >
                <span>{activeTab === "login" ? "Sign In" : "Create Account"}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>

            {authMessage && (
              <p role="status" className="rounded-xl border border-amber-400/20 bg-amber-400/10 px-3 py-2 text-xs leading-relaxed text-amber-100">
                {authMessage}
              </p>
            )}

            {/* OR CONTINUE WITH Divider */}
            <div className="relative flex justify-center text-[10px] uppercase font-mono tracking-widest text-slate-500 my-4">
              <span className="px-3 bg-[#0a1424] relative z-10">OR CONTINUE AS</span>
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-800" />
              </div>
            </div>

            {/* Social Logins / Guest Option */}
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={handleGoogleSignIn}
                className="py-2.5 px-4 rounded-xl bg-slate-900/80 hover:bg-slate-800/90 border border-slate-700/80 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center justify-center gap-2"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.7 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.3 9 5 12 5z" />
                  <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z" />
                  <path fill="#FBBC05" d="M5.6 14.8c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.9 7.3C.7 9.7 0 12 0 14.5s.7 4.8 1.9 7.2l3.7-2.9z" />
                  <path fill="#34A853" d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.3-6.4-5.2L1.9 16C3.7 19.7 7.5 23 12 23z" />
                </svg>
                <span>Google (soon)</span>
              </button>

              <button
                type="button"
                onClick={handleGuestAccess}
                className="py-2.5 px-4 rounded-xl bg-slate-900/80 hover:bg-slate-800/90 border border-slate-700/80 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center justify-center gap-2"
              >
                <User className="w-4 h-4" />
                <span>Continue as Guest</span>
              </button>
            </div>
          </div>

          {/* Footer Tab Switch Link */}
          <div className="text-center pt-2 text-xs text-slate-400">
            {activeTab === "login" ? (
              <span>
                Don't have an account yet?{" "}
                <button
                  type="button"
                  onClick={() => { setActiveTab("signup"); setAuthMessage(""); }}
                  className="text-cyan-400 font-bold hover:underline transition-colors ml-1"
                >
                  Create Account
                </button>
              </span>
            ) : (
              <span>
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => { setActiveTab("login"); setAuthMessage(""); }}
                  className="text-cyan-400 font-bold hover:underline transition-colors ml-1"
                >
                  Sign In
                </button>
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AuthModal;
