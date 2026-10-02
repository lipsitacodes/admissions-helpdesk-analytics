import React, { useState, useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import {
  ArrowRight,
  Zap,
  Shield,
  TrendingUp,
  GraduationCap,
  Phone,
  ChevronRight,
  Star,
  Award,
  Users,
  Building2,
  Sparkles,
  MessageSquare,
  IndianRupee,
  CheckCircle,
  BarChart3,
  Globe,
  Menu,
  X,
} from "lucide-react";
import { OrbLogo } from "./OrbLogo";
import { AuthModal } from "./AuthModal";
import CountUp from "./CountUp";
import SplitText from "./SplitText";
import LogoLoop from "./LogoLoop";
import SpecularButton from "./SpecularButton";
import MoltenMetal from "./MoltenMetal";

// ===========================================================================
// DATA
// ===========================================================================

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "Programs & Fees", href: "#programs" },
  { label: "Scholarships", href: "#scholarships" },
  { label: "Campuses", href: "#campuses" },
];

const STATS = [
  { value: "NAAC A+", label: "Accredited Grade", icon: Shield },
  { value: "15,000+", label: "Students Enrolled", icon: Users },
  { value: "900+", label: "Recruiting Companies", icon: Building2 },
  { value: "24/7", label: "AI Query Support", icon: Sparkles },
];

const FEATURE_CARDS = [
  {
    id: "fees",
    icon: IndianRupee,
    accent: "#06b6d4",
    label: "Fee Intelligence",
    title: "Instant Fee & Eligibility Data",
    description:
      "Get campus-wise fee breakdowns for B.Tech CSE, MBA, Agriculture and more. BBSR vs PKD comparisons in seconds.",
    stat: "₹1,85,000",
    statLabel: "B.Tech CSE BBSR / yr",
    query: "What is the fee for B.Tech CSE?",
    visual: "fees",
  },
  {
    id: "scholarships",
    icon: Award,
    accent: "#818cf8",
    label: "Scholarship Matching",
    title: "Amrit Kaal Merit Scholarships",
    description:
      "Discover your eligible scholarship tier based on 12th board marks or JEE rank. Up to 20% fee waiver available.",
    stat: "Up to 20%",
    statLabel: "Tuition Fee Waiver",
    query: "What is the Amrit Kaal Scholarship for B.Tech CSE?",
    visual: "scholarship",
  },
  {
    id: "cuee",
    icon: GraduationCap,
    accent: "#34d399",
    label: "CUEE 2026 Guidance",
    title: "CUEE 2026 Exam & Admissions",
    description:
      "Complete process walkthrough for Centurion University Entrance Exam — eligibility, registration, and key dates.",
    stat: "2026",
    statLabel: "CUEE Cycle Open",
    query: "What is the CUEE 2026 admission process?",
    visual: "cuee",
  },
];

const PROGRAMS = [
  { name: "B.Tech Computer Science (CSE)", campus: "BBSR + PKD", fee: "₹1,85,000/yr", tag: "Most Popular" },
  { name: "B.Tech Mechanical Engineering", campus: "BBSR + PKD", fee: "₹1,60,000/yr", tag: null },
  { name: "B.Tech Civil Engineering", campus: "BBSR + PKD", fee: "₹1,55,000/yr", tag: null },
  { name: "MBA (Business Administration)", campus: "BBSR", fee: "₹1,40,000/yr", tag: "Top Ranked" },
  { name: "B.Sc Agriculture", campus: "PKD", fee: "₹90,000/yr", tag: null },
  { name: "B.Pharm (Pharmacy)", campus: "BBSR + PKD", fee: "₹1,25,000/yr", tag: null },
];

const QUICK_PROMPTS = [
  "B.Tech CSE fees BBSR vs PKD",
  "CUEE 2026 exam dates",
  "Amrit Kaal Scholarship tiers",
  "Hostel & mess charges",
  "CSE eligibility criteria",
  "First year full fee breakup",
];

// ===========================================================================
// SUBCOMPONENTS
// ===========================================================================

function FeatureVisual({ type, accent }) {
  if (type === "fees") {
    return (
      <div className="relative h-28 flex items-end gap-2 px-1 mt-2">
        {[60, 85, 55, 100, 75, 90].map((h, i) => (
          <div
            key={i}
            className="flex-1 rounded-t-md transition-all duration-700"
            style={{
              height: `${h}%`,
              background: `linear-gradient(to top, ${accent}50, ${accent}15)`,
              border: `1px solid ${accent}30`,
            }}
          />
        ))}
        <div
          className="absolute top-2 right-2 text-[10px] font-bold px-2 py-0.5 rounded-full"
          style={{ background: `${accent}25`, color: accent, border: `1px solid ${accent}40` }}
        >
          ↑ 4.2% Enrollment Growth
        </div>
      </div>
    );
  }

  if (type === "scholarship") {
    const tiers = [
      { label: "70–80%", pct: "10%", w: "45%" },
      { label: "80–90%", pct: "15%", w: "65%" },
      { label: "90%+ / JEE", pct: "20%", w: "85%" },
    ];
    return (
      <div className="space-y-2 mt-2 px-1">
        {tiers.map((t) => (
          <div key={t.label} className="flex items-center gap-2">
            <span className="text-[9px] text-slate-400 w-16 shrink-0">{t.label}</span>
            <div className="flex-1 h-4 rounded-full bg-white/5 overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{
                  width: t.w,
                  background: `linear-gradient(90deg, ${accent}90, ${accent}40)`,
                }}
              />
            </div>
            <span className="text-[9px] font-bold w-7 shrink-0" style={{ color: accent }}>
              {t.pct}
            </span>
          </div>
        ))}
      </div>
    );
  }

  if (type === "cuee") {
    const steps = ["Apply Online", "CUEE Exam", "Merit List", "Admission"];
    return (
      <div className="flex items-center justify-between mt-3 px-1">
        {steps.map((s, i) => (
          <React.Fragment key={s}>
            <div className="flex flex-col items-center gap-1">
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-bold"
                style={{
                  background: i < 2 ? `${accent}30` : "rgba(255,255,255,0.04)",
                  border: `1px solid ${i < 2 ? accent + "60" : "rgba(255,255,255,0.1)"}`,
                  color: i < 2 ? accent : "#64748b",
                }}
              >
                {i + 1}
              </div>
              <span className="text-[8px] text-slate-400 text-center leading-tight max-w-[44px]">{s}</span>
            </div>
            {i < steps.length - 1 && (
              <div
                className="flex-1 h-px mx-1"
                style={{ background: i < 1 ? `${accent}60` : "rgba(255,255,255,0.08)" }}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    );
  }

  return null;
}

function AnimationSlot() {
  // ▶ ANIMATION HOOK POINT — Replace this component with your custom animation
  return (
    <div className="relative w-full max-w-2xl mx-auto aspect-[16/9] flex items-center justify-center">
      {/* Ambient glow rings */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-80 h-80 rounded-full" style={{ background: "radial-gradient(circle, rgba(6,182,212,0.12) 0%, rgba(59,130,246,0.08) 50%, transparent 70%)" }} />
      </div>
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        {[140, 200, 260, 320].map((size, i) => (
          <div
            key={i}
            className="absolute rounded-full border animate-spin"
            style={{
              width: size,
              height: size,
              borderColor: `rgba(6,182,212,${0.08 - i * 0.015})`,
              animationDuration: `${12 + i * 5}s`,
              animationDirection: i % 2 === 0 ? "normal" : "reverse",
            }}
          />
        ))}
      </div>
      {/* Central Orb */}
      <div className="relative z-10 flex flex-col items-center gap-4">
        <OrbLogo size="xl" animated={true} />
        <div className="text-center space-y-1">
          <p className="text-xs font-bold tracking-widest uppercase" style={{ color: "#06b6d4" }}>
            FEESABILITY
          </p>
          <p className="text-[10px] text-slate-500">Admissions Intelligence Core</p>
        </div>
      </div>
      {/* Floating data chips */}
      {[
        { label: "B.Tech CSE", val: "₹1.85L/yr", x: "-left-8 top-1/4", delay: "0s" },
        { label: "Scholarship", val: "Up to 20%", x: "-right-8 top-1/3", delay: "0.4s" },
        { label: "CUEE 2026", val: "Now Open", x: "left-0 bottom-1/4", delay: "0.8s" },
        { label: "NAAC A+", val: "Accredited", x: "right-0 bottom-1/3", delay: "1.2s" },
      ].map(({ label, val, x, delay }) => (
        <div
          key={label}
          className={`absolute ${x} px-3 py-1.5 rounded-xl text-left`}
          style={{
            background: "rgba(10, 20, 40, 0.85)",
            border: "1px solid rgba(56, 189, 248, 0.2)",
            backdropFilter: "blur(12px)",
            animation: `floatChip 4s ease-in-out infinite`,
            animationDelay: delay,
          }}
        >
          <p className="text-[9px] text-slate-400 leading-none">{label}</p>
          <p className="text-[11px] font-bold leading-tight mt-0.5" style={{ color: "#06b6d4" }}>{val}</p>
        </div>
      ))}
    </div>
  );
}

// ===========================================================================
// MAIN LANDING PAGE
// ===========================================================================

export function LandingPage({ onLaunchChat, onSaveCandidate, theme }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const pageRef = useRef(null);

  // Register GSAP plugin
  gsap.registerPlugin(ScrollTrigger);

  // Scroll-reveal: fade + slide up for every [data-reveal] element
  useEffect(() => {
    if (!pageRef.current) return;
    const ctx = gsap.context(() => {
      // Batch-animate all reveal targets
      gsap.utils.toArray("[data-reveal]", pageRef.current).forEach((el) => {
        gsap.fromTo(
          el,
          { opacity: 0, y: 48, scale: 0.97 },
          {
            opacity: 1,
            y: 0,
            scale: 1,
            duration: 0.85,
            ease: "power3.out",
            scrollTrigger: {
              trigger: el,
              start: "top 88%",
              toggleActions: "play none none none",
            },
          }
        );
      });

      // Stagger children inside [data-stagger] containers
      gsap.utils.toArray("[data-stagger]", pageRef.current).forEach((container) => {
        const children = gsap.utils.toArray(container.children);
        gsap.fromTo(
          children,
          { opacity: 0, y: 36 },
          {
            opacity: 1,
            y: 0,
            duration: 0.7,
            ease: "power2.out",
            stagger: 0.12,
            scrollTrigger: {
              trigger: container,
              start: "top 85%",
              toggleActions: "play none none none",
            },
          }
        );
      });
    }, pageRef);

    return () => ctx.revert();
  }, []);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handlePromptClick = (prompt) => {
    onLaunchChat(prompt);
  };

  return (
    <div
      ref={pageRef}
      className="min-h-screen w-full relative overflow-x-hidden"
      style={{
        background: "linear-gradient(135deg, #050a14 0%, #080d1a 50%, #05080f 100%)",
        color: "#f1f5f9",
        fontFamily: "'DM Sans', 'Inter', sans-serif",
      }}
    >
      {/* Molten-metal shader background for the landing page */}
      <div className="fixed inset-0 z-0" aria-hidden="true">
        <MoltenMetal
          color1="#5227FF"
          color2="#d560d2"
          color3="#FFFFFF"
          speed={0.35}
          scale={4}
          detail={3}
          glow={1.6}
          coreSize={0.1}
          swirl={1}
          fold={-0.2}
          blackPoint={0.05}
          brightness={1.3}
          colorMode="molten"
          grain={true}
          grainIntensity={0.05}
          mouseInteraction={true}
          mouseStrength={0.3}
          opacity={0.55}
          className="absolute inset-0"
        />
      </div>

      {/* Global ambient glow */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div
          className="absolute -top-40 -left-40 w-96 h-96 rounded-full opacity-20"
          style={{ background: "radial-gradient(circle, #06b6d4 0%, transparent 70%)", filter: "blur(80px)" }}
        />
        <div
          className="absolute top-1/3 -right-20 w-80 h-80 rounded-full opacity-15"
          style={{ background: "radial-gradient(circle, #3b82f6 0%, transparent 70%)", filter: "blur(80px)" }}
        />
        <div
          className="absolute bottom-0 left-1/3 w-64 h-64 rounded-full opacity-10"
          style={{ background: "radial-gradient(circle, #818cf8 0%, transparent 70%)", filter: "blur(60px)" }}
        />
      </div>

      {/* ──────────────────── NAVBAR ──────────────────── */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
        style={{
          background: scrolled ? "rgba(5, 10, 20, 0.88)" : "transparent",
          backdropFilter: scrolled ? "blur(20px)" : "none",
          borderBottom: scrolled ? "1px solid rgba(56, 189, 248, 0.12)" : "1px solid transparent",
        }}
      >
        <div className="w-full px-6 sm:px-12 h-16 flex items-center justify-between">
          {/* Brand */}
          <div className="flex items-center gap-2.5">
            <OrbLogo size="sm" animated={false} />
            <div>
              <span className="text-sm font-extrabold tracking-tight text-white font-heading">FEESABILITY</span>
            </div>
          </div>

          {/* CTA: Sign In / Register Button */}
          <div className="flex items-center gap-3">
            <SpecularButton
              size="sm"
              radius={24}
              tint="#06b6d4"
              tintOpacity={0.15}
              blur={12}
              textColor="#ffffff"
              lineColor="#38bdf8"
              baseColor="#0e7490"
              intensity={1.2}
              speed={0.4}
              followMouse={true}
              proximity={180}
              onClick={() => setAuthOpen(true)}
              className="text-xs sm:text-sm font-bold"
            >
              Sign In / Register
            </SpecularButton>
          </div>
        </div>
      </nav>

      {/* ──────────────────── HERO SECTION ──────────────────── */}
      <section className="relative pt-32 pb-16 px-4 sm:px-8 text-center max-w-7xl mx-auto">
        {/* Headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl tracking-tight leading-tight mb-6" style={{ fontFamily: "'DM Serif Display', serif", fontWeight: 400 }}>
          <SplitText
            text="Admissions Intelligence"
            tag="span"
            className="text-white block sm:inline"
            delay={30}
            duration={0.6}
            splitType="chars"
            from={{ opacity: 0, y: 25 }}
            to={{ opacity: 1, y: 0 }}
          />
          <br />
          <span
            className="inline-block"
            style={{
              fontStyle: "italic",
              background: "linear-gradient(90deg, #38bdf8 0%, #06b6d4 50%, #3b82f6 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            <SplitText
              text="that shapes your future."
              tag="span"
              delay={30}
              duration={0.7}
              splitType="chars"
              from={{ opacity: 0, y: 25 }}
              to={{ opacity: 1, y: 0 }}
            />
          </span>
        </h1>

        {/* Subheading with animated word split */}
        <div className="max-w-2xl mx-auto mb-10">
          <SplitText
            text="Get instant, verified answers on B.Tech CSE fees, CUEE 2026 eligibility, Amrit Kaal scholarships, and multi-campus admissions — powered by official Centurion University policies."
            tag="p"
            className="text-base sm:text-lg text-slate-400 leading-relaxed"
            delay={15}
            duration={0.8}
            splitType="words"
            from={{ opacity: 0, y: 20 }}
            to={{ opacity: 1, y: 0 }}
          />
        </div>

        {/* CTA Buttons */}
        <div className="flex items-center justify-center mb-16">
          <SpecularButton
            size="lg"
            radius={32}
            tint="#06b6d4"
            tintOpacity={0.2}
            blur={16}
            textColor="#ffffff"
            lineColor="#38bdf8"
            baseColor="#0891b2"
            intensity={1.5}
            speed={0.4}
            followMouse={true}
            proximity={250}
            onClick={() => handlePromptClick("")}
            className="font-bold text-sm sm:text-base group"
          >
            <span>Ask Admissions AI</span>
            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
          </SpecularButton>
        </div>

        {/* Animation Slot */}
        <AnimationSlot />

        {/* Quick prompt continuous loop marquee */}
        <div className="mt-12 flex flex-col items-center justify-center gap-3 max-w-4xl mx-auto overflow-hidden">
          <span className="text-xs text-slate-400 font-medium">Try asking →</span>
          <div className="w-full relative py-2">
            <LogoLoop
              logos={QUICK_PROMPTS.map((p) => ({
                node: (
                  <button
                    type="button"
                    onClick={() => handlePromptClick(p)}
                    className="px-4 py-1.5 rounded-full text-xs font-medium transition-all hover:scale-105 active:scale-95 whitespace-nowrap"
                    style={{
                      background: "rgba(6,182,212,0.12)",
                      border: "1px solid rgba(56,189,248,0.25)",
                      color: "#cbd5e1",
                    }}
                  >
                    {p}
                  </button>
                ),
                title: p,
              }))}
              speed={45}
              direction="left"
              gap={24}
              pauseOnHover={true}
              scaleOnHover={false}
              fadeOut={true}
              fadeOutColor="rgba(5, 10, 20, 1)"
              ariaLabel="Suggested admission queries"
            />
          </div>
        </div>
      </section>

      {/* ──────────────────── FEATURE CARDS ──────────────────── */}
      <section id="features" className="py-20 px-4 sm:px-8 max-w-7xl mx-auto">
        <div className="text-center mb-14" data-reveal>
          <p className="text-xs font-bold tracking-widest uppercase mb-2" style={{ color: "#06b6d4" }}>
            What the AI Knows
          </p>
          <h2 className="text-3xl sm:text-4xl text-white" style={{ fontFamily: "'DM Serif Display', serif", fontWeight: 400 }}>
            Your complete admissions command center
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6" data-stagger>
          {FEATURE_CARDS.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.id}
                className="rounded-2xl p-6 flex flex-col justify-between group hover:-translate-y-1 transition-all duration-300 cursor-pointer"
                style={{
                  background: "rgba(10, 18, 35, 0.7)",
                  border: "1px solid rgba(56, 189, 248, 0.12)",
                  backdropFilter: "blur(16px)",
                  boxShadow: "0 4px 40px rgba(0,0,0,0.4)",
                }}
                onClick={() => handlePromptClick(card.query)}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div
                      className="w-9 h-9 rounded-xl flex items-center justify-center"
                      style={{ background: `${card.accent}20`, border: `1px solid ${card.accent}35` }}
                    >
                      <Icon className="w-4.5 h-4.5" style={{ color: card.accent }} />
                    </div>
                    <span
                      className="text-[10px] font-bold tracking-wider uppercase px-2.5 py-0.5 rounded-full"
                      style={{ background: `${card.accent}18`, color: card.accent, border: `1px solid ${card.accent}30` }}
                    >
                      {card.label}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white mb-2">{card.title}</h3>
                  <p className="text-sm text-slate-400 leading-relaxed mb-4">{card.description}</p>

                  <FeatureVisual type={card.visual} accent={card.accent} />
                </div>

                <div className="flex items-end justify-between mt-5 pt-4" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
                  <div>
                    <p className="text-lg font-extrabold" style={{ color: card.accent }}>{card.stat}</p>
                    <p className="text-[10px] text-slate-500">{card.statLabel}</p>
                  </div>
                  <div
                    className="flex items-center gap-1 text-[10px] font-semibold group-hover:gap-2 transition-all"
                    style={{ color: card.accent }}
                  >
                    <span>Ask AI</span>
                    <ArrowRight className="w-3 h-3" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ──────────────────── PROGRAMS SECTION ──────────────────── */}
      <section id="programs" className="py-20 px-4 sm:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <p className="text-xs font-bold tracking-widest uppercase mb-3" style={{ color: "#818cf8" }}>
              Programs & Fee Structure
            </p>
            <h2 className="text-3xl sm:text-4xl text-white mb-4" style={{ fontFamily: "'DM Serif Display', serif", fontWeight: 400 }}>
              Explore programs across
              <span style={{ fontStyle: "italic", background: "linear-gradient(90deg, #38bdf8, #06b6d4, #3b82f6)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}> two campuses.</span>
            </h2>
            <p className="text-sm text-slate-400 leading-relaxed mb-6">
              Centurion University offers UG, PG, and diploma programs across Engineering, Management, Agriculture, and Allied Health Sciences at our Bhubaneswar (BBSR) and Paralakhemundi (PKD) campuses.
            </p>
            <button
              type="button"
              onClick={() => handlePromptClick("Tell me about all available programs and fee structure at Centurion University")}
              className="flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold transition-all hover:scale-105"
              style={{ background: "rgba(129,140,248,0.15)", border: "1px solid rgba(129,140,248,0.3)", color: "#a5b4fc" }}
            >
              <span>View All Programs</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2.5">
            {PROGRAMS.map((prog) => (
              <button
                key={prog.name}
                type="button"
                onClick={() => handlePromptClick(`What is the fee for ${prog.name} at Centurion University?`)}
                className="w-full flex items-center justify-between px-4 py-3 rounded-xl text-left transition-all hover:scale-[1.01] group"
                style={{
                  background: "rgba(10, 18, 35, 0.6)",
                  border: "1px solid rgba(56, 189, 248, 0.1)",
                }}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: "#06b6d4" }} />
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-white truncate">{prog.name}</p>
                    <p className="text-[10px] text-slate-500">{prog.campus}</p>
                  </div>
                  {prog.tag && (
                    <span className="shrink-0 text-[9px] font-bold px-1.5 py-0.5 rounded-full" style={{ background: "rgba(6,182,212,0.15)", color: "#06b6d4" }}>
                      {prog.tag}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 shrink-0 ml-3">
                  <span className="text-xs font-bold" style={{ color: "#06b6d4" }}>{prog.fee}</span>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-slate-400 transition-colors" />
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ──────────────────── STATS / TRUST RIBBON ──────────────────── */}
      <section className="py-16 px-4 sm:px-8 max-w-7xl mx-auto">
        <div
          className="rounded-2xl p-8 grid grid-cols-2 md:grid-cols-4 gap-8"
          data-stagger
          style={{
            background: "rgba(10, 18, 35, 0.6)",
            border: "1px solid rgba(56, 189, 248, 0.12)",
            backdropFilter: "blur(20px)",
          }}
        >
          {STATS.map((stat) => {
            const Icon = stat.icon;
            let displayVal = stat.value;
            if (stat.value === "15,000+") {
              displayVal = <><CountUp from={0} to={15000} separator="," duration={2} />+</>;
            } else if (stat.value === "900+") {
              displayVal = <><CountUp from={0} to={900} duration={2} />+</>;
            } else if (stat.value === "24/7") {
              displayVal = <><CountUp from={0} to={24} duration={1.5} />/7</>;
            }

            return (
              <div key={stat.value} className="flex flex-col items-center text-center gap-2">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center mb-1"
                  style={{ background: "rgba(6,182,212,0.12)", border: "1px solid rgba(6,182,212,0.2)" }}
                >
                  <Icon className="w-4.5 h-4.5" style={{ color: "#06b6d4" }} />
                </div>
                <p className="text-xl sm:text-2xl font-extrabold text-white">{displayVal}</p>
                <p className="text-[11px] text-slate-500">{stat.label}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* ──────────────────── CTA BANNER ──────────────────── */}
      <section id="cta-banner" className="py-16 px-4 sm:px-8 max-w-7xl mx-auto">
        <div
          className="rounded-3xl px-8 py-14 text-center relative overflow-hidden"
          data-reveal
          style={{
            background: "linear-gradient(135deg, rgba(6,182,212,0.15) 0%, rgba(59,130,246,0.12) 50%, rgba(129,140,248,0.12) 100%)",
            border: "1px solid rgba(56, 189, 248, 0.2)",
          }}
        >
          <div className="absolute inset-0 pointer-events-none" style={{ background: "radial-gradient(ellipse at 50% 0%, rgba(6,182,212,0.12) 0%, transparent 60%)" }} />
          <p className="text-xs font-bold tracking-widest uppercase mb-3" style={{ color: "#06b6d4" }}>
            Get Started Now
          </p>
          <h2 className="text-3xl sm:text-4xl text-white mb-4" style={{ fontFamily: "'DM Serif Display', serif", fontWeight: 400 }}>
            Your FEESABILITY journey begins
            <span style={{ fontStyle: "italic", background: "linear-gradient(90deg, #38bdf8, #06b6d4, #3b82f6)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}> with one question.</span>
          </h2>
          <p className="text-sm text-slate-400 max-w-lg mx-auto mb-8">
            Ask about fees, eligibility, scholarships, or campus life. Our AI gives you official, verified answers — instantly.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <SpecularButton
              size="md"
              radius={24}
              tint="#06b6d4"
              tintOpacity={0.1}
              blur={12}
              textColor="#ffffff"
              lineColor="#38bdf8"
              baseColor="#0891b2"
              intensity={1.2}
              speed={0.4}
              followMouse={true}
              proximity={200}
              onClick={() => { window.location.href = "tel:8260077222"; }}
              className="font-semibold text-sm"
            >
              <Phone className="w-4 h-4 mr-1 text-cyan-400" />
              <span>Call: 8260077222</span>
            </SpecularButton>
          </div>
        </div>
      </section>

      {/* ──────────────────── FOOTER ──────────────────── */}
      <footer
        className="mt-4 px-4 sm:px-8 py-10 max-w-7xl mx-auto"
        style={{ borderTop: "1px solid rgba(56, 189, 248, 0.08)" }}
      >
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5">
            <OrbLogo size="sm" animated={false} />
            <div>
              <p className="text-sm font-bold text-white">FEESABILITY</p>
              <p className="text-[11px] text-slate-500">Student Helpdesk</p>
            </div>
          </div>
          <div className="flex items-center gap-6 text-xs text-slate-500">
            <span>UGC Recognized</span>
            <span>AICTE Approved</span>
            <span>NAAC A+ Grade</span>
          </div>
          <p className="text-xs text-slate-600">© FEESABILITY</p>
        </div>
      </footer>

      {/* Floating chat bubble button */}
      <button
        type="button"
        onClick={() => {
          const el = document.getElementById("cta-banner");
          if (el) el.scrollIntoView({ behavior: "smooth" });
        }}
        className="fixed bottom-8 right-8 z-50 w-14 h-14 rounded-full flex items-center justify-center shadow-2xl transition-all hover:scale-110 active:scale-95"
        style={{
          background: "linear-gradient(135deg, #06b6d4, #3b82f6)",
          boxShadow: "0 0 25px rgba(6,182,212,0.5)",
        }}
        title="Scroll to Admissions AI"
      >
        <MessageSquare className="w-5 h-5 text-white" />
      </button>

      {/* Auth Modal Card */}
      <AuthModal
        isOpen={authOpen}
        onClose={() => setAuthOpen(false)}
        candidateName=""
        onSaveCandidate={onSaveCandidate}
        onAuthSuccess={() => {
          setAuthOpen(false);
          onLaunchChat("");
        }}
      />

      {/* Keyframes for floating animation */}
      <style>{`
        @keyframes floatChip {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-8px); }
        }
      `}</style>
    </div>
  );
}

export default LandingPage;
