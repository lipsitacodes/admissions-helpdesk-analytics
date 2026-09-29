import React, { useRef, useEffect, useState } from "react";
import {
  ShieldCheck,
  AlertCircle,
  Copy,
  Check,
  Volume2,
  Code,
  Mail,
  Award,
  MessageSquare,
  User,
} from "lucide-react";
import { OrbLogo } from "./OrbLogo";
import { useSmoothScroll } from "../hooks/useSmoothScroll";

const QUICK_CATEGORY_PILLS = [
  { label: "B.Tech CSE Fees", query: "What is the fee for B.Tech CSE in Bhubaneswar?" },
  { label: "Scholarships", query: "What are the Amrit Kaal scholarship percentage tiers?" },
  { label: "CUEE 2026 Process", query: "How do I apply for CUEE 2026 entrance exam?" },
  { label: "Eligibility Criteria", query: "What is the eligibility criteria for B.Tech engineering?" },
];

const DISCOVERY_EXAMPLE_CARDS = [
  {
    title: "B.Tech CSE Fee Structure",
    subtitle: "Check 4-year annual fees for BBSR (₹185k) & PKD (₹150k)",
    query: "What is the fee for B.Tech CSE?",
    icon: Code,
  },
  {
    title: "CUEE 2026 Entrance Exam",
    subtitle: "Learn how to register online & view scheduled test dates",
    query: "What is the CUEE 2026 admission process?",
    icon: Mail,
  },
  {
    title: "Amrit Kaal Scholarships",
    subtitle: "10%–20% tuition fee waiver based on 12th / JEE rank",
    query: "What is the Amrit Kaal Scholarship for B.Tech CSE?",
    icon: Award,
  },
  {
    title: "Hostel & First Year Other Fees",
    subtitle: "Explore accommodation amenities & ₹25,000 fee breakup",
    query: "What is the first year other fee breakup and hostel structure?",
    icon: MessageSquare,
  },
];

export function ChatArea({
  messages,
  isBusy,
  onSelectPrompt,
  candidateName,
  theme,
  citationEnabled,
}) {
  const bottomRef = useRef(null);
  const scrollContainerRef = useRef(null);

  useSmoothScroll(scrollContainerRef);

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (container) {
      container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
    }
  }, [messages, isBusy]);

  const displayName = candidateName || "Candidate";

  return (
    <div
      ref={scrollContainerRef}
      className="flex-1 min-h-0 overflow-y-auto overscroll-y-contain px-4 py-6"
      data-chat-scroll-container
    >
      <div className="min-h-full">
      {messages.length === 0 ? (
        /* Hero Welcome Interface matching Reference Images 1 & 3 */
        <div className="max-w-3xl mx-auto py-8 sm:py-12 px-2 text-center space-y-8">
          {/* Animated Colorful 3D Glowing Orb */}
          <div className="flex justify-center">
            <OrbLogo size="lg" animated={true} />
          </div>

          {/* Heading in High-Contrast Black & White */}
          <div className="space-y-2">
            <h2 className="text-2xl sm:text-4xl text-light-text dark:text-dark-text tracking-tight" style={{ fontFamily: "'DM Serif Display', serif", fontWeight: 400 }}>
              <span>Ready to Explore </span>
              <span style={{ fontStyle: "italic", background: "linear-gradient(90deg, #38bdf8, #06b6d4, #3b82f6)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                AskCampus?
              </span>
            </h2>
            <p className="text-xs sm:text-sm text-light-muted dark:text-dark-muted max-w-lg mx-auto">
              Ask any question about academic programmes, campus-wise fees, CUEE 2026, scholarships, and campus living.
            </p>
          </div>

          {/* Quick Action Pills in Clean Monochrome */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
            {QUICK_CATEGORY_PILLS.map((pill, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onSelectPrompt(pill.query)}
                className="px-3.5 py-1.5 rounded-full border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface hover:bg-light-surface2 dark:hover:bg-dark-surface2 text-xs font-semibold text-light-text dark:text-dark-text transition-all shadow-sm active:scale-95 flex items-center gap-1.5"
              >
                <span>{pill.label}</span>
              </button>
            ))}
          </div>

          {/* "GET STARTED WITH AN EXAMPLE BELOW" Section */}
          <div className="space-y-3 text-left pt-4">
            <div className="text-[11px] font-bold tracking-wider text-light-muted dark:text-dark-muted uppercase px-1">
              Get Started with an Example Below
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {DISCOVERY_EXAMPLE_CARDS.map((card, idx) => {
                const Icon = card.icon;
                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => onSelectPrompt(card.query)}
                    className="p-4 rounded-2xl glass-card hover:border-light-borderLight dark:hover:border-dark-borderLight hover:bg-light-surface2/80 dark:hover:bg-dark-surface2/80 text-left transition-all duration-200 shadow-sm group flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1.5">
                        <h3 className="text-xs sm:text-sm font-bold text-light-text dark:text-dark-text group-hover:opacity-80 transition-opacity">
                          {card.title}
                        </h3>
                      </div>
                      <p className="text-[11px] text-light-muted dark:text-dark-muted line-clamp-2">
                        {card.subtitle}
                      </p>
                    </div>
                    <div className="mt-3 flex items-center justify-between pt-2 border-t border-light-border dark:border-dark-border">
                      <span className="text-[10px] text-light-text dark:text-dark-text font-bold">
                        Ask Helpdesk ↵
                      </span>
                      <Icon className="w-3.5 h-3.5 text-light-muted dark:text-dark-muted group-hover:text-light-text dark:group-hover:text-dark-text transition-colors" />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      ) : (
        /* Active Conversation Message Stream */
        <div className="space-y-6 max-w-3xl mx-auto py-2">
          {messages.map((msg) => (
            <MessageRow
              key={msg.id}
              message={msg}
              citationEnabled={citationEnabled}
            />
          ))}

          {/* Thinking State */}
          {isBusy && (
            <div className="flex items-center gap-3 max-w-3xl mx-auto p-4 rounded-2xl glass-card border border-light-border dark:border-dark-border text-xs text-light-muted dark:text-dark-muted animate-pulse">
              <OrbLogo size="sm" animated={true} />
              <div className="space-y-0.5">
                <p className="font-bold text-light-text dark:text-dark-text">
                  Retrieving Verified Admissions Records...
                </p>
                <p className="text-[11px]">
                  Cross-referencing 2025–26 official fee and eligibility policies
                </p>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      )}
      </div>
    </div>
  );
}

function MessageRow({ message, citationEnabled }) {
  const { role, text, timestamp, data } = message;
  const isAssistant = role === "assistant";
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  };

  const handleSpeak = () => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <article
      className={`flex gap-3 max-w-3xl w-full mx-auto ${
        isAssistant ? "justify-start" : "justify-end"
      }`}
    >
      <div
        className={`flex flex-col space-y-1.5 max-w-[88%] sm:max-w-[80%] ${
          isAssistant ? "items-start" : "items-end"
        }`}
      >
        {isAssistant && (
          <div className="flex items-center gap-2 px-1">
            <span className="text-xs font-bold text-light-text dark:text-dark-text">
              AskCampus Assistant
            </span>
            {data?.grounded && citationEnabled && (
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-light-text dark:text-dark-text border border-light-border dark:border-dark-border bg-light-surface2 dark:bg-dark-surface2 px-2 py-0.5 rounded-full">
                <ShieldCheck className="w-3 h-3 text-emerald-500" />
                <span>Verified Source</span>
              </span>
            )}
          </div>
        )}

        {/* Message Bubble (Theme Cohesive) */}
        <div
          className={`px-4 py-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-sm transition-all ${
            isAssistant
              ? "glass-card text-light-text dark:text-dark-text border border-light-border dark:border-dark-border"
              : "bg-light-surface2 dark:bg-dark-surface2 text-light-text dark:text-dark-text border border-light-borderLight dark:border-dark-borderLight font-medium rounded-br-sm shadow-sm"
          }`}
        >
          <div className="whitespace-pre-wrap leading-relaxed">{text}</div>

          {/* Escalation notice */}
          {isAssistant && data?.escalated && (
            <div className="mt-3 p-2.5 rounded-xl border border-light-border dark:border-dark-border bg-light-surface2 dark:bg-dark-surface2 text-light-text dark:text-dark-text text-xs flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-amber-500" />
              <div>
                <p className="font-bold text-[11px]">Admissions Office Assistance</p>
                <p className="text-[11px] opacity-90 mt-0.5">
                  For personalized application verification, please contact the helpline at <strong>8260077222</strong>.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center gap-3 px-1.5 text-[10px] text-light-muted dark:text-dark-muted font-mono">
          <time>{timestamp}</time>
          {isAssistant && (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleCopy}
                className="flex items-center gap-1 hover:text-light-text dark:hover:text-dark-text transition-colors"
                title="Copy response"
              >
                {copied ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-500" />
                    <span className="text-emerald-500 font-bold">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span>Copy</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleSpeak}
                className="flex items-center gap-1 hover:text-light-text dark:hover:text-dark-text transition-colors"
                title="Read aloud"
              >
                <Volume2 className="w-3 h-3" />
                <span>Listen</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {!isAssistant && (
        <div className="w-7 h-7 rounded-full bg-light-surface2 dark:bg-dark-surface2 border border-light-border dark:border-dark-border text-light-text dark:text-dark-text flex items-center justify-center font-bold text-xs shrink-0 mt-0.5 shadow-sm">
          <User className="w-3.5 h-3.5" />
        </div>
      )}
    </article>
  );
}

export default ChatArea;
