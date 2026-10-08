import React, { useState, useEffect, useRef } from "react";
import { gsap } from "gsap";
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
  Loader2,
} from "lucide-react";
import { FeesabilityLogo } from "./FeesabilityLogo";
import { auth, googleProvider } from "../firebase";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  updateProfile,
  sendPasswordResetEmail,
} from "firebase/auth";

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

function getFirebaseErrorMessage(errorCode) {
  const messages = {
    "auth/email-already-in-use": "This email is already registered. Try logging in instead.",
    "auth/invalid-email": "Please enter a valid email address.",
    "auth/weak-password": "Password must be at least 6 characters.",
    "auth/user-not-found": "No account found with this email. Sign up first!",
    "auth/wrong-password": "Incorrect password. Please try again.",
    "auth/invalid-credential": "Invalid email or password. Please try again.",
    "auth/too-many-requests": "Too many attempts. Please wait a moment and try again.",
    "auth/popup-closed-by-user": "Google sign-in was cancelled.",
    "auth/network-request-failed": "Network error. Check your connection and try again.",
    "auth/popup-blocked": "Popup was blocked. Please allow popups for this site.",
  };
  return messages[errorCode] || "Authentication failed. Please verify your details.";
}

export function AuthModal({
  isOpen,
  onClose,
  candidateName,
  onSaveCandidate,
  onAuthSuccess,
}) {
  const [activeTab, setActiveTab] = useState("login"); // 'login' | 'signup' | 'guest'
  const [nameInput, setNameInput] = useState(candidateName || "");
  const [emailInput, setEmailInput] = useState("");
  const [passwordInput, setPasswordInput] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [keepLoggedIn, setKeepLoggedIn] = useState(true);
  const [authMessage, setAuthMessage] = useState("");
  const [authMessageType, setAuthMessageType] = useState("error"); // 'error' | 'success' | 'info'
  const [submitting, setSubmitting] = useState(false);

  // Slide Carousel State & Touch/Swipe logic
  const [currentSlide, setCurrentSlide] = useState(0);
  const touchStartX = useRef(0);
  const touchEndX = useRef(0);
  const isDragging = useRef(false);

  // Reset submitting when modal opens
  useEffect(() => {
    if (isOpen) {
      setSubmitting(false);
      setAuthMessage("");
    }
  }, [isOpen]);

  // Auto-advance slide every 5 seconds
  useEffect(() => {
    if (!isOpen) return;
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % SLIDES.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [isOpen]);

  const modalWrapperRef = useRef(null);
  const backdropRef = useRef(null);

  useEffect(() => {
    if (isOpen && modalWrapperRef.current && backdropRef.current) {
      gsap.fromTo(
        backdropRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.35, ease: "power2.out" }
      );
      gsap.fromTo(
        modalWrapperRef.current,
        { opacity: 0, scale: 0.95, y: 12 },
        { opacity: 1, scale: 1, y: 0, duration: 0.4, ease: "power3.out" }
      );
    }
  }, [isOpen]);

  const handleModalClose = () => {
    if (modalWrapperRef.current && backdropRef.current) {
      gsap.to(backdropRef.current, { opacity: 0, duration: 0.22, ease: "power2.in" });
      gsap.to(modalWrapperRef.current, {
        opacity: 0,
        scale: 0.96,
        y: 10,
        duration: 0.25,
        ease: "power2.in",
        onComplete: onClose,
      });
    } else {
      onClose();
    }
  };

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

  const handleAuthComplete = (displayName, email) => {
    onSaveCandidate(displayName);
    localStorage.setItem("campus_ai_candidate_name", displayName);
    if (email) localStorage.setItem("campus_ai_user_email", email);
    localStorage.setItem("campus_ai_is_authenticated", "true");
    localStorage.removeItem("campus_ai_is_guest");
    if (onAuthSuccess) {
      onAuthSuccess(displayName);
    } else {
      onClose();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;

    if (activeTab === "signup" && passwordInput !== confirmPassword) {
      setAuthMessage("Your passwords do not match.");
      setAuthMessageType("error");
      return;
    }

    setSubmitting(true);
    setAuthMessage("");

    if (!auth) {
      const fallbackName =
        (activeTab === "signup" ? nameInput.trim() : "") ||
        (emailInput ? emailInput.split("@")[0] : "") ||
        candidateName ||
        "Student";
      handleAuthComplete(fallbackName, emailInput);
      setSubmitting(false);
      return;
    }

    try {
      if (activeTab === "signup") {
        const userCredential = await createUserWithEmailAndPassword(
          auth,
          emailInput,
          passwordInput
        );
        const displayName = nameInput.trim() || emailInput.split("@")[0] || "Student";
        try {
          await updateProfile(userCredential.user, { displayName });
        } catch (_) {}
        handleAuthComplete(displayName, emailInput);
      } else {
        const userCredential = await signInWithEmailAndPassword(
          auth,
          emailInput,
          passwordInput
        );
        const displayName =
          userCredential.user.displayName || emailInput.split("@")[0] || "Student";
        handleAuthComplete(displayName, emailInput);
      }
    } catch (error) {
      console.error("Firebase auth error:", error);
      // Fallback: if Firebase config is invalid or fails, gracefully fallback
      if (error?.code && error.code.startsWith("auth/")) {
        setAuthMessage(getFirebaseErrorMessage(error.code));
        setAuthMessageType("error");
      } else {
        const fallbackName =
          (activeTab === "signup" ? nameInput.trim() : "") ||
          (emailInput ? emailInput.split("@")[0] : "") ||
          candidateName ||
          "Student";
        handleAuthComplete(fallbackName, emailInput);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleGuestSubmit = (e) => {
    if (e) e.preventDefault();
    const trimmedName = nameInput.trim();
    const trimmedEmail = emailInput.trim();

    if (!trimmedName) {
      setAuthMessage("Please enter your name to continue as a guest.");
      setAuthMessageType("error");
      return;
    }
    if (!trimmedEmail || !trimmedEmail.includes("@") || !trimmedEmail.includes(".")) {
      setAuthMessage("Please enter a valid email address to continue.");
      setAuthMessageType("error");
      return;
    }

    setSubmitting(true);
    onSaveCandidate(trimmedName);
    localStorage.setItem("campus_ai_candidate_name", trimmedName);
    localStorage.setItem("campus_ai_user_email", trimmedEmail);
    localStorage.setItem("campus_ai_is_guest", "true");
    localStorage.setItem("campus_ai_is_authenticated", "true");

    if (onAuthSuccess) {
      onAuthSuccess(trimmedName);
    } else {
      onClose();
    }
  };

  const handleGuestAccess = () => {
    setActiveTab("guest");
    setAuthMessage("");
  };

  const handleGoogleSignIn = async () => {
    setSubmitting(true);
    setAuthMessage("");

    if (!auth || !googleProvider) {
      setAuthMessage("Google sign-in is unavailable without Firebase setup. Please use email or guest mode.");
      setAuthMessageType("info");
      setSubmitting(false);
      return;
    }

    try {
      const result = await signInWithPopup(auth, googleProvider);
      const displayName =
        result.user.displayName || result.user.email?.split("@")[0] || "Student";
      handleAuthComplete(displayName, result.user.email);
    } catch (error) {
      console.error("Google sign-in error:", error);
      if (error?.code !== "auth/popup-closed-by-user") {
        setAuthMessage(getFirebaseErrorMessage(error?.code));
        setAuthMessageType("error");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleForgotPassword = async () => {
    if (!emailInput.trim()) {
      setAuthMessage("Enter your email above first, then click 'Forgot password?'");
      setAuthMessageType("info");
      return;
    }

    if (!auth) {
      setAuthMessage("Password reset is unavailable without Firebase configuration.");
      setAuthMessageType("info");
      return;
    }

    setSubmitting(true);
    setAuthMessage("");
    try {
      await sendPasswordResetEmail(auth, emailInput);
      setAuthMessage("Password reset email sent! Please check your inbox.");
      setAuthMessageType("success");
    } catch (error) {
      console.error("Password reset error:", error);
      setAuthMessage(getFirebaseErrorMessage(error?.code));
      setAuthMessageType("error");
    } finally {
      setSubmitting(false);
    }
  };

  const activeSlideData = SLIDES[currentSlide];
  const IconComponent = activeSlideData.icon;

  const messageStyles = {
    error: "border-red-400/20 bg-red-400/10 text-red-200",
    success: "border-emerald-400/20 bg-emerald-400/10 text-emerald-200",
    info: "border-cyan-400/20 bg-cyan-400/10 text-cyan-200",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 overflow-y-auto">
      {/* Dimmed Blurred Backdrop */}
      <div
        ref={backdropRef}
        onClick={handleModalClose}
        className="fixed inset-0 bg-black/75 backdrop-blur-md transition-opacity"
      />

      {/* Main Dialog Modal Container */}
      <div
        ref={modalWrapperRef}
        className="relative w-full max-w-4xl rounded-3xl bg-[#070e1b] border border-cyan-500/20 shadow-[0_20px_70px_rgba(0,0,0,0.85)] overflow-hidden flex flex-col md:flex-row z-10 my-auto text-left"
        style={{
          boxShadow:
            "0 25px 60px -15px rgba(6, 182, 212, 0.15), 0 0 40px rgba(0, 0, 0, 0.9)",
        }}
      >
        {/* Close Button */}
        <button
          type="button"
          onClick={handleModalClose}
          className="absolute top-4 right-4 z-30 p-2 rounded-full bg-slate-900/60 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-700/50 transition-all cursor-pointer"
          aria-label="Close auth dialog"
        >
          <X className="w-4 h-4" />
        </button>

        {/* ──────────────────── LEFT COLUMN: SLIDE SHOWCASE CAROUSEL ──────────────────── */}
        <div
          className="hidden md:flex md:w-5/12 bg-gradient-to-br from-[#0a172e] via-[#081224] to-[#040813] border-r border-slate-800/80 p-8 flex-col justify-between relative overflow-hidden select-none cursor-grab active:cursor-grabbing"
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        >
          {/* Ambient Lighting Orbs */}
          <div className="absolute top-0 -left-10 w-56 h-56 rounded-full bg-cyan-500/15 blur-3xl pointer-events-none" />
          <div className="absolute bottom-10 -right-10 w-56 h-56 rounded-full bg-blue-600/15 blur-3xl pointer-events-none" />

          {/* Top Branding Header */}
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <FeesabilityLogo className="w-6 h-6 text-white shrink-0" />
              <span className="text-sm font-extrabold tracking-[-0.03em] text-white" style={{ fontFamily: "'Outfit', sans-serif" }}>
                feesability<span className="text-white">.</span>
              </span>
            </div>
            <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              ADMISSIONS 2026
            </span>
          </div>

          {/* Center Dynamic Interactive Card */}
          <div className="relative z-10 my-6 transition-all duration-300">
            {/* Holographic Glowing Glass Card */}
            <div className="rounded-2xl p-4 bg-slate-900/60 backdrop-blur-xl border border-cyan-500/30 shadow-[0_8px_32px_rgba(0,0,0,0.5)] space-y-3 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-28 h-28 bg-gradient-to-bl from-cyan-400/15 to-transparent rounded-bl-full pointer-events-none" />

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-white shadow-md shadow-cyan-500/25">
                    <IconComponent className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">
                      {activeSlideData.cardTitle}
                    </h4>
                    <p className="text-[10px] text-slate-400">
                      {activeSlideData.cardSubtitle}
                    </p>
                  </div>
                </div>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  {activeSlideData.statusText}
                </span>
              </div>

              {/* Progress bar visual */}
              <div className="space-y-1">
                <div className="flex justify-between text-[10px] text-slate-400">
                  <span>Knowledge Graph</span>
                  <span>Centurion Univ</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-500 rounded-full transition-all duration-500 ${activeSlideData.progress}`}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-1 border-t border-slate-800/80 text-[10px] text-slate-400">
                <span className="flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-cyan-400" />
                  Verified Grounding
                </span>
                <span>{activeSlideData.footerText}</span>
              </div>
            </div>

            {/* Slide Text Content */}
            <div className="mt-5 space-y-1.5">
              <div className="inline-block px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400 text-[10px] font-semibold tracking-wide uppercase border border-cyan-500/20 mb-1">
                {activeSlideData.badge} • {activeSlideData.category}
              </div>
              <h3 className="text-base font-bold text-white leading-snug">
                {activeSlideData.title}
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                {activeSlideData.subtitle}
              </p>
            </div>
          </div>

          {/* Bottom Slide Indicators & Navigation Arrows */}
          <div className="relative z-10 flex items-center justify-between pt-3 border-t border-slate-800/60">
            {/* Indicators */}
            <div className="flex items-center gap-1.5">
              {SLIDES.map((_, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setCurrentSlide(idx)}
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
                className="p-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-slate-400 hover:text-white transition-colors cursor-pointer"
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
                className="p-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-slate-400 hover:text-white transition-colors cursor-pointer"
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
              <FeesabilityLogo className="w-5 h-5 text-white shrink-0" />
              <span className="text-xs font-extrabold tracking-[-0.03em] text-white" style={{ fontFamily: "'Outfit', sans-serif" }}>
                feesability<span className="text-white">.</span>
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
                {activeTab === "login"
                  ? "Welcome Back"
                  : activeTab === "signup"
                  ? "Create Account"
                  : "Guest Access"}
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                {activeTab === "login"
                  ? "Ready to continue your admissions quest?"
                  : activeTab === "signup"
                  ? "Create your FEESABILITY account"
                  : "Enter your name and email to proceed to the workspace"}
              </p>
            </div>

            {/* Tab Switcher (Login | Sign Up | Guest Mode) */}
            {activeTab !== "guest" ? (
              <div className="flex items-center border-b border-slate-800 text-sm font-semibold">
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("login");
                    setAuthMessage("");
                  }}
                  className={`pb-3 px-4 transition-all relative cursor-pointer ${
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
                  className={`pb-3 px-4 transition-all relative cursor-pointer ${
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
            ) : (
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 text-sm font-semibold">
                <span className="flex items-center gap-1.5 text-xs text-cyan-400 font-semibold">
                  <User className="w-3.5 h-3.5 text-cyan-400" />
                  Guest Information
                </span>
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("login");
                    setAuthMessage("");
                  }}
                  className="text-xs text-slate-400 hover:text-white transition-colors cursor-pointer"
                >
                  ← Back to Login
                </button>
              </div>
            )}

            {/* Form Inputs: Guest Mode or Login/Signup */}
            {activeTab === "guest" ? (
              <form onSubmit={handleGuestSubmit} className="space-y-4">
                {/* Name Field */}
                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-slate-300">
                    Full Name <span className="text-cyan-400">*</span>
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                    <input
                      type="text"
                      required
                      autoFocus
                      placeholder="Candidate / Student Name"
                      value={nameInput}
                      onChange={(e) => setNameInput(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700/80 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
                    />
                  </div>
                </div>

                {/* Email Address */}
                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-slate-300">
                    Email Address <span className="text-cyan-400">*</span>
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

                <p className="text-[11px] text-slate-400">
                  Guest access stores your conversation locally on this browser.
                </p>

                {/* Submit Guest */}
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-3 px-6 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:opacity-95 shadow-lg shadow-cyan-500/25 active:scale-[0.99] transition-all flex items-center justify-center gap-2 mt-2 cursor-pointer disabled:opacity-80"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Entering Workspace...</span>
                    </>
                  ) : (
                    <>
                      <span>Continue to Admissions Workspace</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>
            ) : (
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

                {/* Email Field */}
                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-slate-300">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                    <input
                      type="email"
                      required
                      placeholder="student@example.com"
                      value={emailInput}
                      onChange={(e) => setEmailInput(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700/80 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all"
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <label className="text-[11px] font-semibold text-slate-300">
                      Password
                    </label>
                    {activeTab === "login" && (
                      <button
                        type="button"
                        onClick={handleForgotPassword}
                        disabled={submitting}
                        className="text-[11px] text-cyan-400 hover:text-cyan-300 hover:underline transition-colors disabled:opacity-50 cursor-pointer"
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
                  disabled={submitting}
                  className="w-full py-3 px-6 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:opacity-95 shadow-lg shadow-cyan-500/25 active:scale-[0.99] transition-all flex items-center justify-center gap-2 mt-1 cursor-pointer disabled:opacity-80"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Please wait...</span>
                    </>
                  ) : (
                    <>
                      <span>{activeTab === "login" ? "Sign In" : "Create Account"}</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>
            )}

            {authMessage && (
              <p
                role="status"
                className={`rounded-xl border px-3 py-2 text-xs leading-relaxed ${messageStyles[authMessageType]}`}
              >
                {authMessage}
              </p>
            )}

            {/* OR CONTINUE AS Divider (shown for Login & Sign Up) */}
            {activeTab !== "guest" && (
              <>
                <div className="relative flex justify-center text-[10px] uppercase font-mono tracking-widest text-slate-500 my-3">
                  <span className="px-3 bg-[#070e1b] relative z-10">OR CONTINUE AS</span>
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-slate-800" />
                  </div>
                </div>

                {/* Social Logins / Guest Option */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <button
                    type="button"
                    onClick={handleGoogleSignIn}
                    disabled={submitting}
                    className="py-2.5 px-4 rounded-xl bg-slate-900/80 hover:bg-slate-800/90 border border-slate-700/80 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
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
                    <span>Google</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleGuestAccess}
                    disabled={submitting}
                    className="py-2.5 px-4 rounded-xl bg-slate-900/80 hover:bg-slate-800/90 border border-slate-700/80 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    <User className="w-4 h-4 flex-shrink-0" />
                    <span>Continue as Guest</span>
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Footer Tab Switch Link */}
          <div className="text-center pt-2 text-xs text-slate-400">
            {activeTab === "guest" ? (
              <span>
                Want to save your profile permanently?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("signup");
                    setAuthMessage("");
                  }}
                  className="text-cyan-400 font-bold hover:underline transition-colors ml-1 cursor-pointer"
                >
                  Create Account
                </button>
                {" or "}
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("login");
                    setAuthMessage("");
                  }}
                  className="text-cyan-400 font-bold hover:underline transition-colors cursor-pointer"
                >
                  Sign In
                </button>
              </span>
            ) : activeTab === "login" ? (
              <span>
                Don't have an account yet?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab("signup");
                    setAuthMessage("");
                  }}
                  className="text-cyan-400 font-bold hover:underline transition-colors ml-1 cursor-pointer"
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
                  className="text-cyan-400 font-bold hover:underline transition-colors ml-1 cursor-pointer"
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
