import React, { useRef, useEffect, useState } from "react";
import {
  ShieldCheck,
  AlertCircle,
  Copy,
  Check,
  User,
  Sparkles,
} from "lucide-react";
import { FormattedAnswer } from "./FormattedAnswer";
import { useSmoothScroll } from "../hooks/useSmoothScroll";
import { FeesabilityLogo } from "./FeesabilityLogo";

export function ChatArea({
  messages,
  isBusy,
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

  if (messages.length === 0) {
    return null;
  }

  return (
    <div
      ref={scrollContainerRef}
      className="flex-1 min-h-0 overflow-y-auto overscroll-y-contain px-4 py-6"
      data-chat-scroll-container
    >
      <div className="min-h-full">
        {/* Active Conversation Message Stream */}
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
              <div className="w-6 h-6 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shrink-0 shadow-sm shadow-cyan-500/20">
                <Sparkles className="w-3.5 h-3.5 text-white animate-spin" />
              </div>
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
          <div className="flex flex-wrap items-center gap-2 px-1">
            <span className="text-xs font-bold text-light-text dark:text-dark-text flex items-center gap-1.5">
              <FeesabilityLogo className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span>FEESABILITY Assistant</span>
            </span>
            {data?.grounded && data?.predicted_intent !== "out_of_scope" && citationEnabled && (
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
          {isAssistant ? (
            <FormattedAnswer text={text} />
          ) : (
            <div className="whitespace-pre-wrap leading-relaxed">{text}</div>
          )}

          {/* Escalation notice */}
          {isAssistant && data?.escalated && data?.predicted_intent !== "out_of_scope" && (
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
