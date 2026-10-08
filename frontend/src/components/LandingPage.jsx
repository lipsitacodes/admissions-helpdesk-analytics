import { ArrowRight, User } from "lucide-react";
import { motion } from "motion/react";
import { useState, useEffect } from "react";
import { AuthModal } from "./AuthModal";
import { FeesabilityLogo } from "./FeesabilityLogo";
import { LightRays } from "./LightRays";
import { TextAnimate } from "./TextAnimate";

export function LandingPage({
  onLaunchChat,
  onSaveCandidate,
  isAuthenticated: propIsAuth,
}) {
  const [authOpen, setAuthOpen] = useState(false);

  // Check authentication status (persisted in localStorage or passed from parent)
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    if (typeof window === "undefined") return false;
    const hasStorage =
      localStorage.getItem("campus_ai_is_authenticated") === "true" ||
      localStorage.getItem("campus_ai_is_guest") === "true";
    return propIsAuth !== undefined ? Boolean(propIsAuth) && hasStorage : hasStorage;
  });

  useEffect(() => {
    const hasStorage =
      localStorage.getItem("campus_ai_is_authenticated") === "true" ||
      localStorage.getItem("campus_ai_is_guest") === "true";
    const isAuth =
      propIsAuth !== undefined ? Boolean(propIsAuth) && hasStorage : hasStorage;
    setIsAuthenticated(isAuth);
  }, [propIsAuth, authOpen]);

  const handleWorkspaceEnter = () => {
    setAuthOpen(false);
    onLaunchChat("");
  };

  return (
    <div
      className="fixed inset-0 w-screen h-screen overflow-hidden select-none flex flex-col justify-between items-center"
      style={{
        background: "linear-gradient(180deg, #020409 0%, #030611 35%, #081628 68%, #162f4a 100%)",
      }}
    >
      {/* ──────────────────── TOP BAR (LOGO & SIGN IN) ──────────────────── */}
      {/* Top Left: Logo with Smooth Fade-In Animation */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
        className="absolute top-6 left-6 sm:top-8 sm:left-10 z-30"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="inline-flex items-center gap-2.5 sm:gap-3 cursor-pointer group">
          <FeesabilityLogo className="w-7 h-7 sm:w-8 sm:h-8 text-white group-hover:scale-105 transition-transform" />
          <span
            className="text-2xl sm:text-3xl font-extrabold text-white tracking-[-0.03em] select-none hover:opacity-90 transition-opacity inline-flex items-center"
            style={{ fontFamily: "'Outfit', sans-serif" }}
          >
            feesability<span className="text-white">.</span>
          </span>
        </div>
      </motion.div>

      {/* Top Right: Glassmorphism Sign In / Workspace Button with Smooth Fade-In Animation */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.25, ease: [0.16, 1, 0.3, 1] }}
        className="absolute top-6 right-6 sm:top-8 sm:right-10 z-30"
        onClick={(e) => e.stopPropagation()}
      >
        {isAuthenticated ? (
          <motion.button
            type="button"
            onClick={handleWorkspaceEnter}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
            className="group relative px-5 py-2 sm:px-6 sm:py-2.5 rounded-full flex items-center gap-2.5 text-xs sm:text-sm font-medium text-white/95 hover:text-white transition-all duration-300"
            style={{
              background: "rgba(255, 255, 255, 0.04)",
              backdropFilter: "blur(24px)",
              WebkitBackdropFilter: "blur(24px)",
              border: "1px solid rgba(56, 189, 248, 0.35)",
              boxShadow:
                "0 8px 32px 0 rgba(0, 0, 0, 0.25), inset 0 1px 1px 0 rgba(255, 255, 255, 0.15)",
              fontFamily: "'Outfit', sans-serif",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(56, 189, 248, 0.12)";
              e.currentTarget.style.borderColor = "rgba(56, 189, 248, 0.6)";
              e.currentTarget.style.boxShadow =
                "0 8px 32px 0 rgba(14, 165, 233, 0.3), inset 0 1px 1px 0 rgba(255, 255, 255, 0.25)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.04)";
              e.currentTarget.style.borderColor = "rgba(56, 189, 248, 0.35)";
              e.currentTarget.style.boxShadow =
                "0 8px 32px 0 rgba(0, 0, 0, 0.25), inset 0 1px 1px 0 rgba(255, 255, 255, 0.15)";
            }}
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="tracking-wide">Workspace</span>
            <ArrowRight className="w-3.5 h-3.5 text-cyan-400 group-hover:translate-x-0.5 transition-transform" />
          </motion.button>
        ) : (
          <motion.button
            type="button"
            onClick={() => setAuthOpen(true)}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
            className="group relative px-5 py-2 sm:px-6 sm:py-2.5 rounded-full flex items-center gap-2.5 text-xs sm:text-sm font-medium text-white/90 hover:text-white transition-all duration-300"
            style={{
              background: "rgba(255, 255, 255, 0.03)",
              backdropFilter: "blur(24px)",
              WebkitBackdropFilter: "blur(24px)",
              border: "1px solid rgba(255, 255, 255, 0.10)",
              boxShadow:
                "0 8px 32px 0 rgba(0, 0, 0, 0.25), inset 0 1px 1px 0 rgba(255, 255, 255, 0.12)",
              fontFamily: "'Outfit', sans-serif",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)";
              e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.24)";
              e.currentTarget.style.boxShadow =
                "0 8px 32px 0 rgba(0, 0, 0, 0.35), inset 0 1px 1px 0 rgba(255, 255, 255, 0.18)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.03)";
              e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.10)";
              e.currentTarget.style.boxShadow =
                "0 8px 32px 0 rgba(0, 0, 0, 0.25), inset 0 1px 1px 0 rgba(255, 255, 255, 0.12)";
            }}
          >
            <User className="w-3.5 h-3.5 text-cyan-400/90 group-hover:text-cyan-400 group-hover:scale-110 transition-transform" />
            <span className="tracking-wide">Sign In</span>
          </motion.button>
        )}
      </motion.div>

      {/* ──────────────────── WEBGL LIGHT RAYS BACKGROUND EFFECT ──────────────────── */}
      <div className="pointer-events-none absolute inset-0 z-0 overflow-hidden">
        <LightRays
          raysOrigin="top-center"
          raysColor="#00e5ff"
          raysSpeed={1.3}
          lightSpread={1.2}
          rayLength={1.8}
          followMouse={true}
          mouseInfluence={0.25}
          noiseAmount={0.02}
          distortion={0.06}
          className="opacity-75 mix-blend-screen"
        />
      </div>

      {/* ──────────────────── STUDIO SWEEP ATMOSPHERIC LIGHTING ──────────────────── */}
      {/* Wide soft oceanic-cyan studio floor sweep */}
      <div
        className="pointer-events-none absolute bottom-0 left-1/2 -translate-x-1/2 w-[160vw] md:w-[130vw] h-[65vh]"
        style={{
          background:
            "radial-gradient(ellipse 110% 70% at 50% 100%, rgba(68, 126, 168, 0.55) 0%, rgba(35, 75, 110, 0.4) 30%, rgba(15, 38, 64, 0.22) 58%, rgba(2, 4, 9, 0) 85%)",
        }}
      />

      {/* Intense inner horizon light bar reflection */}
      <div
        className="pointer-events-none absolute bottom-0 left-1/2 -translate-x-1/2 w-[90vw] md:w-[70vw] h-[36vh]"
        style={{
          background:
            "radial-gradient(ellipse 85% 55% at 50% 105%, rgba(115, 185, 230, 0.42) 0%, rgba(55, 120, 175, 0.22) 42%, transparent 75%)",
        }}
      />

      {/* Top half darkness vignette */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 90% 70% at 50% 20%, transparent 40%, rgba(1, 2, 5, 0.75) 100%)",
        }}
      />

      {/* Subtle fine film grain texture from reference */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.045] mix-blend-screen"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Top spacing spacer */}
      <div className="w-full flex-1" />

      {/* ──────────────────── MAIN CENTERPIECE CLUSTER ──────────────────── */}
      <div className="relative z-10 flex flex-col items-center justify-center text-center px-4 select-none">
        {/* Top small category label: SS'25 / NEW LOOK */}
        <div className="mb-6 sm:mb-8">
          <TextAnimate
            as="p"
            animation="fadeIn"
            by="character"
            delay={0.32}
            duration={0.45}
            startOnView={false}
            className="text-[10px] sm:text-[11px] font-semibold text-white tracking-[0.22em] uppercase"
            style={{ fontFamily: "'Unbounded', 'Syncopate', sans-serif" }}
          >
            WELCOME TO FEESABILITY
          </TextAnimate>
        </div>

        {/* Hero Title: SIMPLIFYING YOUR , Every Choice (Modius Font) */}
        <div className="my-1 flex flex-col items-center justify-center text-center">
          <TextAnimate
            as="h1"
            animation="fadeIn"
            by="character"
            delay={0.42}
            duration={0.65}
            startOnView={false}
            className="font-semibold text-white leading-tight uppercase tracking-[0.05em] sm:tracking-[0.07em] whitespace-nowrap"
            style={{
              fontFamily: "'Modius', sans-serif",
              fontSize: "clamp(1.75rem, 3.4vw, 3.2rem)",
              textShadow: "0 0 30px rgba(255, 255, 255, 0.12)",
            }}
          >
            SIMPLIFYING YOUR,
          </TextAnimate>

          <TextAnimate
            as="span"
            animation="fadeIn"
            by="word"
            delay={0.52}
            duration={0.55}
            startOnView={false}
            className="italic font-normal text-white/95 leading-tight tracking-[0.02em] whitespace-nowrap mt-1 sm:mt-1.5"
            style={{
              fontFamily: "'Modius', sans-serif",
              fontSize: "clamp(1.85rem, 3.6vw, 3.4rem)",
              textShadow: "0 0 30px rgba(255, 255, 255, 0.12)",
            }}
          >
            Every Choice
          </TextAnimate>
        </div>

        {/* ──────── Glassmorphism Get Started / Continue to Workspace Button (Smooth Fade-In Animation) ──────── */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.58, ease: [0.16, 1, 0.3, 1] }}
          className="mt-8 sm:mt-10"
          onClick={(e) => e.stopPropagation()}
        >
          <motion.button
            type="button"
            onClick={isAuthenticated ? handleWorkspaceEnter : () => setAuthOpen(true)}
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.98 }}
            className="group relative px-7 py-3 sm:px-8 sm:py-3.5 rounded-full flex items-center gap-3 text-xs sm:text-sm font-medium text-white transition-all duration-300"
            style={{
              background: "rgba(255, 255, 255, 0.05)",
              backdropFilter: "blur(20px)",
              WebkitBackdropFilter: "blur(20px)",
              border: "1px solid rgba(255, 255, 255, 0.16)",
              boxShadow:
                "0 8px 32px 0 rgba(0, 0, 0, 0.35), inset 0 1px 1px 0 rgba(255, 255, 255, 0.2)",
              fontFamily: "'Outfit', sans-serif",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.10)";
              e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.28)";
              e.currentTarget.style.boxShadow =
                "0 10px 36px 0 rgba(0, 0, 0, 0.45), inset 0 1px 1px 0 rgba(255, 255, 255, 0.25)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)";
              e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.16)";
              e.currentTarget.style.boxShadow =
                "0 8px 32px 0 rgba(0, 0, 0, 0.35), inset 0 1px 1px 0 rgba(255, 255, 255, 0.2)";
            }}
          >
            <span className="tracking-wider uppercase text-[11px] sm:text-xs font-semibold">
              {isAuthenticated ? "Continue to Workspace" : "Get Started"}
            </span>
            <ArrowRight className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-cyan-400 group-hover:translate-x-1.5 transition-transform duration-300" />
          </motion.button>
        </motion.div>
      </div>

      {/* Bottom spacing spacer to balance the optical center */}
      <div className="w-full flex-1" />

      {/* ──────────────────── BOTTOM 2-LINE FOOTER ──────────────────── */}
      <footer className="relative z-10 w-full px-4 pb-6 sm:pb-8 flex flex-col items-center text-center">
        <TextAnimate
          as="p"
          animation="fadeIn"
          by="line"
          delay={0.72}
          duration={0.5}
          startOnView={false}
          className="text-[8px] sm:text-[9.5px] tracking-[0.04em] text-white/50 max-w-3xl leading-relaxed font-sans"
        >
          Verified fee structures , and merit scholarship evaluation across partner university campuses.
        </TextAnimate>
        <TextAnimate
          as="p"
          animation="fadeIn"
          by="line"
          delay={0.84}
          duration={0.5}
          startOnView={false}
          className="text-[8px] sm:text-[9.5px] tracking-[0.04em] text-white/50 max-w-3xl leading-relaxed font-sans mt-0.5"
        >
          Empowering candidates and parents with intelligent 24/7 AI-guided admission fees & clarity with verified university data.
        </TextAnimate>
      </footer>

      {/* ──────────────────── AUTH MODAL ──────────────────── */}
      <AuthModal
        isOpen={authOpen}
        onClose={() => setAuthOpen(false)}
        candidateName=""
        onSaveCandidate={onSaveCandidate}
        onAuthSuccess={(name) => {
          if (name && onSaveCandidate) {
            onSaveCandidate(name);
          }
          onLaunchChat("");
        }}
      />
    </div>
  );
}

export default LandingPage;
