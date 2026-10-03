import React, { useState, useEffect, useRef } from "react";
import {
  X,
  Lock,
  Mail,
  User,
  ArrowRight,
  Sparkles,
  Bot,
  Award,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { OrbLogo } from "./OrbLogo";

const SLIDES = [
  {
    id: 0,
    badge: "INITIALIZING",
    category: "Student Helpdesk",
    title: "Your admissions journey starts here.",
    subtitle:
      "Get instant verified data on B.Tech CSE fees, CUEE 2026 eligibility, and Amrit Kaal merit scholarships.",
    cardTitle: "New Candidate",
    cardSubtitle: "Student Helpdesk",
    statusText: "100% Ready",
    footerText: "24/7 AI query engine active",
    icon: User,
    progress: "w-full",
  },
  {
    id: 1,
    badge: "24/7 ACTIVE",
    category: "AI Query Engine",
    title: "Instant answers for all your queries.",
    subtitle:
      "Ask about cutoffs, campus facilities, hostel fees, and step-by-step application procedures in real time.",
    cardTitle: "Smart Assistant",
    cardSubtitle: "Admission Knowledge Base",
    statusText: "Online",
    footerText: "Over 500+ admission FAQs indexed",
    icon: Bot,
    progress: "w-4/5",
  },
  {
    id: 2,
    badge: "UP TO 100%",
    category: "Merit Scholarships",
    title: "Unlock scholarships tailored for you.",
    subtitle:
      "Calculate your scholarship eligibility based on board marks, JEE Main percentile, and CUEE entrance ranks.",
    cardTitle: "Scholarship Finder",
    cardSubtitle: "Amrit Kaal & Merit Quota",
    statusText: "Verified",
    footerText: "Direct fee waiver breakdown available",
    icon: Award,
    progress: "w-11/12",
  },
];

export function AuthModal({
  isOpen,
  onClose,
  candidateName,
  onSaveCandidate,
  onAuthSuccess,
}) {
  const [activeTab, setActiveTab] = useState("login"); // 'login' | 'signup'
  const [nameInput, setNameInput] = useState(candidateName || "");
  const [emailInput, setEmailInput] = useState("");
  const [passwordInput, setPasswordInput] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [keepLoggedIn, setKeepLoggedIn] = useState(true);
  const [authMessage, setAuthMessage] = useState("");

  // Slide Carousel State & Touch/Swipe logic
  const [currentSlide, setCurrentSlide] = useState(0);
  const touchStartX = useRef(0);
  const touchEndX = useRef(0);
  const isDragging = useRef(false);

  // Auto-advance slide every 5 seconds
  useEffect(() => {
    if (!isOpen) return;
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % SLIDES.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [isOpen]);

  if (!isOpen) return null;

  const handleNextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % SLIDES.length);
  };

  const handlePrevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + SLIDES.length) % SLIDES.length);
  };

  const processSwipe = () => {
    if (!touchStartX.current || !touchEndX.current) return;
    const diffX = touchStartX.current - touchEndX.current;
    const minSwipeDistance = 30; // pixels
    if (diffX > minSwipeDistance) {
      handleNextSlide(); // Swipe left -> Next
    } else if (diffX < -minSwipeDistance) {
      handlePrevSlide(); // Swipe right -> Previous
    }
    touchStartX.current = 0;
    touchEndX.current = 0;
  };

  const handleTouchStart = (e) => {
    touchStartX.current = e.targetTouches[0].clientX;
  };

  const handleTouchMove = (e) => {
    touchEndX.current = e.targetTouches[0].clientX;
  };

  const handleTouchEnd = () => {
    processSwipe();
  };

  const handleMouseDown = (e) => {
    isDragging.current = true;
    touchStartX.current = e.clientX;
  };

  const handleMouseMove = (e) => {
    if (isDragging.current) {
      touchEndX.current = e.clientX;
    }
  };

  const handleMouseUp = () => {
    if (isDragging.current) {
      processSwipe();
      isDragging.current = false;
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (activeTab === "signup" && passwordInput !== confirmPassword) {
      setAuthMessage("Your passwords do not match.");
      return;
    }
    setAuthMessage(
      "Account authentication will be available after the database is connected. Continue as a guest for now."
    );
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
    setAuthMessage(
      "Google sign-in will be available when database authentication is integrated."
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 overflow-y-auto">
      {/* Deep Dark Blurred Backdrop */}
      <div
        className="fixed inset-0 bg-[#030712]/85 backdrop-blur-2xl transition-opacity"
        onClick={onClose}
      />

      {/* Decorative Ambient Radial Glows */}
      <div className="fixed top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-72 sm:w-96 h-72 sm:h-96 rounded-full bg-cyan-500/15 blur-[120px] pointer-events-none" />
      <div className="fixed bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-72 sm:w-96 h-72 sm:h-96 rounded-full bg-blue-600/15 blur-[120px] pointer-events-none" />

      {/* Split-Layout Glassmorphic Modal Card */}
      <div className="relative w-full max-w-4xl bg-[#0a1424]/95 backdrop-blur-3xl rounded-2xl sm:rounded-3xl text-white shadow-2xl border border-slate-700/60 z-10 overflow-hidden flex flex-col md:flex-row max-h-[92vh] md:max-h-[88vh]">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-3.5 right-3.5 sm:top-4 sm:right-4 z-30 p-2 rounded-full bg-slate-800/70 hover:bg-slate-700/90 text-slate-400 hover:text-white transition-colors"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* ──────────────────── LEFT COLUMN: INTERACTIVE VISUAL SLIDE CAROUSEL ──────────────────── */}
        <div
          className="hidden md:flex md:w-5/12 p-6 lg:p-8 flex-col justify-between relative overflow-hidden bg-gradient-to-br from-[#071324] via-[#091a30] to-[#040a14] border-r border-slate-800/60 select-none cursor-grab active:cursor-grabbing group"
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        >
          {/* Subtle Radial Glow Effect */}
          <div className="absolute inset-0 pointer-events-none opacity-40 bg-[radial-gradient(circle_at_50%_40%,#06b6d4_0%,transparent_60%)] filter blur-3xl" />

          {/* Top Brand Header */}
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <OrbLogo size="sm" animated={false} interactive={false} />
              <span className="text-sm font-extrabold tracking-tight text-white font-heading">
                FEESABILITY
              </span>
            </div>
            <span className="text-[10px] text-slate-400 opacity-60 group-hover:opacity-100 transition-opacity">
              Swipe &rarr;
            </span>
          </div>

          {/* Middle Floating Glass Showcase Card Carousel Track */}
          <div className="relative z-10 my-auto py-4 overflow-hidden w-full">
            <div
              className="flex w-full transition-transform duration-300 ease-[cubic-bezier(0.25,1,0.5,1)]"
              style={{ transform: `translateX(-${currentSlide * 100}%)` }}
            >
              {SLIDES.map((slide) => {
                const SlideIcon = slide.icon;
                return (
                  <div
                    key={slide.id}
                    className="w-full flex-shrink-0 space-y-4 px-0.5"
                  >
                    {/* Glassmorphic Badge / Progress Card */}
                    <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-700/50 backdrop-blur-md shadow-xl space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-md">
                            <SlideIcon className="w-4 h-4" />
                          </div>
                          <div>
                            <div className="text-xs font-bold text-white">
                              {slide.cardTitle}
                            </div>
                            <div className="text-[10px] text-slate-400">
                              {slide.cardSubtitle}
                            </div>
                          </div>
                        </div>
                        <span className="text-[9px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                          {slide.badge}
                        </span>
                      </div>

                      {/* Progress Bar Indicator */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px] text-slate-400">
                          <span>{slide.category}</span>
                          <span className="text-cyan-400 font-mono">
                            {slide.statusText}
                          </span>
                        </div>
                        <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden flex">
                          <div
                            className={`h-full bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-500 rounded-full transition-all duration-500 ${slide.progress}`}
                          />
                        </div>
                      </div>
                      <div className="text-[10px] text-slate-400 flex items-center gap-1.5">
                        <Sparkles className="w-3 h-3 text-cyan-400" />
                        <span>{slide.footerText}</span>
                      </div>
                    </div>

                    {/* Headline & Description */}
                    <div className="space-y-2 mt-4">
                      <h3 className="text-xl lg:text-2xl font-extrabold tracking-tight leading-snug font-heading text-white">
                        {slide.title}
                      </h3>
                      <p className="text-xs text-slate-400 leading-relaxed">
                        {slide.subtitle}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Bottom Slide Pagination Controls & Chevrons */}
          <div className="relative z-10 flex items-center justify-between pt-2">
            {/* Clickable Dots */}
            <div className="flex items-center gap-2">
              {SLIDES.map((slide, idx) => (
                <button
                  key={slide.id}
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setCurrentSlide(idx);
                  }}
                  className={`h-2 rounded-full transition-all duration-300 focus:outline-none ${
                    currentSlide === idx
                      ? "w-6 bg-gradient-to-r from-cyan-400 to-blue-500 shadow-[0_0_8px_rgba(6,182,212,0.6)]"
                      : "w-2 bg-slate-700 hover:bg-slate-500"
                  }`}
                  aria-label={`Go to slide ${idx + 1}`}
                />
              ))}
            </div>

            {/* Previous / Next Arrow Controls */}
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  handlePrevSlide();
                }}
                className="p-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-slate-400 hover:text-white transition-colors"
                aria-label="Previous slide"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleNextSlide();
                }}
                className="p-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-slate-400 hover:text-white transition-colors"
                aria-label="Next slide"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* ──────────────────── RIGHT COLUMN: RESPONSIVE AUTH FORM ──────────────────── */}
        <div className="w-full md:w-7/12 p-5 sm:p-8 lg:p-10 flex flex-col justify-between space-y-5 overflow-y-auto">
          {/* Mobile Header (Visible on small screens where left showcase is hidden) */}
          <div className="flex md:hidden items-center justify-between pb-3 border-b border-slate-800/60 pr-8">
            <div className="flex items-center gap-2">
              <OrbLogo size="sm" animated={false} interactive={false} />
              <span className="text-xs font-extrabold tracking-tight text-white font-heading">
                FEESABILITY
              </span>
            </div>
            <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              ADMISSIONS 2026
            </span>
          </div>

          <div className="space-y-5">
            {/* Form Header */}
            <div>
              <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold tracking-tight text-white">
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
                onClick={() => {
                  setActiveTab("login");
                  setAuthMessage("");
                }}
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
                onClick={() => {
                  setActiveTab("signup");
                  setAuthMessage("");
                }}
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
            <form onSubmit={handleSubmit} className="space-y-3.5">
              {/* Name Field (for Sign Up) */}
              {activeTab === "signup" && (
                <div className="space-y-1">
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

              {/* Email Address */}
              <div className="space-y-1">
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
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <label className="text-[11px] font-semibold text-slate-300">
                    Password
                  </label>
                  {activeTab === "login" && (
                    <button
                      type="button"
                      onClick={() =>
                        setAuthMessage(
                          "Password recovery will be available after account authentication is integrated."
                        )
                      }
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
                <div className="space-y-1">
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

              {/* Checkbox Option */}
              <div className="flex items-center gap-2 pt-0.5">
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
                className="w-full py-3 px-6 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:opacity-95 shadow-lg shadow-cyan-500/25 active:scale-[0.99] transition-all flex items-center justify-center gap-2 mt-1"
              >
                <span>{activeTab === "login" ? "Sign In" : "Create Account"}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>

            {authMessage && (
              <p
                role="status"
                className="rounded-xl border border-amber-400/20 bg-amber-400/10 px-3 py-2 text-xs leading-relaxed text-amber-100"
              >
                {authMessage}
              </p>
            )}

            {/* OR CONTINUE AS Divider */}
            <div className="relative flex justify-center text-[10px] uppercase font-mono tracking-widest text-slate-500 my-3">
              <span className="px-3 bg-[#0a1424] relative z-10">OR CONTINUE AS</span>
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-800" />
              </div>
            </div>

            {/* Social Logins / Guest Option */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <button
                type="button"
                onClick={handleGoogleSignIn}
                className="py-2.5 px-4 rounded-xl bg-slate-900/80 hover:bg-slate-800/90 border border-slate-700/80 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center justify-center gap-2"
              >
                <svg className="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24">
                  <path
                    fill="#EA4335"
                    d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.7 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.3 9 5 12 5z"
                  />
                  <path
                    fill="#4285F4"
                    d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.6 14.8c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.9 7.3C.7 9.7 0 12 0 14.5s.7 4.8 1.9 7.2l3.7-2.9z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.3-6.4-5.2L1.9 16C3.7 19.7 7.5 23 12 23z"
                  />
                </svg>
                <span>Google (soon)</span>
              </button>

              <button
                type="button"
                onClick={handleGuestAccess}
                className="py-2.5 px-4 rounded-xl bg-slate-900/80 hover:bg-slate-800/90 border border-slate-700/80 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center justify-center gap-2"
              >
                <User className="w-4 h-4 flex-shrink-0" />
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
                  onClick={() => {
                    setActiveTab("signup");
                    setAuthMessage("");
                  }}
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
                  onClick={() => {
                    setActiveTab("login");
                    setAuthMessage("");
                  }}
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

