import React, { useRef, useEffect, useState } from "react";
import {
  ArrowUp,
  Sparkles,
  Mic,
  MicOff,
  MapPin,
  ChevronDown,
  Loader2,
} from "lucide-react";
import { CAMPUS_CHOICES } from "./CampusSelector";

export function Composer({
  input,
  setInput,
  onSubmit,
  isBusy,
  errorMessage,
  selectedCampus,
  setSelectedCampus,
  citationEnabled,
  setCitationEnabled,
}) {
  const textareaRef = useRef(null);
  const [isDeepThink, setIsDeepThink] = useState(false);
  const [writingStyle, setWritingStyle] = useState("Bilingual");
  const [showStyleMenu, setShowStyleMenu] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const currentCampus =
    CAMPUS_CHOICES.find((c) => c.id === selectedCampus) || CAMPUS_CHOICES[0];

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        150
      )}px`;
    }
  }, [input]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  const toggleVoice = () => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      alert("Voice speech recognition is not supported in this browser.");
      return;
    }

    try {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.lang = "en-IN";
      recognition.interimResults = false;

      if (!isListening) {
        setIsListening(true);
        recognition.start();

        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          setInput((prev) => (prev ? `${prev} ${transcript}` : transcript));
          setIsListening(false);
        };

        recognition.onerror = () => setIsListening(false);
        recognition.onend = () => setIsListening(false);
      } else {
        recognition.stop();
        setIsListening(false);
      }
    } catch {
      setIsListening(false);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4 pb-5">
      {errorMessage && (
        <div className="mb-2 p-2.5 rounded-xl bg-light-surface2 dark:bg-dark-surface2 border border-red-500/40 text-red-500 text-xs shadow-sm flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Outer Multi-color Neon Aura Container (Animated Glow - Image 2) */}
      <div className="neon-aura-container relative">
        <div className="relative z-10 rounded-2xl border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface p-3.5 sm:p-4 shadow-xl transition-all">
          {/* Main Input Text Area with Sparkle Icon */}
          <div className="flex items-start gap-2.5">
            <Sparkles className="w-4 h-4 text-light-text dark:text-dark-text mt-1 shrink-0 opacity-80" />
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              disabled={isBusy}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask AI a question or make a request (e.g., CSE fees, CUEE 2026, scholarships)..."
              className="w-full bg-transparent resize-none border-none text-xs sm:text-sm text-light-text dark:text-dark-text placeholder:text-light-muted dark:placeholder:text-dark-muted focus:outline-none max-h-36 py-0.5 leading-relaxed"
            />
          </div>

          {/* Bottom Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-light-border dark:border-dark-border mt-2">
            {/* Left Options Pills (Clean monochrome) */}
            <div className="flex flex-wrap items-center gap-1.5">
              {/* Campus Selector Pill */}
              <div className="relative group">
                <button
                  type="button"
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-light-border dark:border-dark-border bg-light-surface2 dark:bg-dark-surface2 text-[11px] font-medium text-light-text dark:text-dark-text hover:border-light-borderLight dark:hover:border-dark-borderLight transition-all"
                >
                  <MapPin className="w-3 h-3 opacity-70" />
                  <span className="hidden xs:inline text-light-muted dark:text-dark-muted">Campus:</span>
                  <span className="font-bold">{currentCampus.badge}</span>
                  <ChevronDown className="w-3 h-3 text-light-muted dark:text-dark-muted" />
                </button>

                {/* Dropdown Menu */}
                <div className="absolute left-0 bottom-full mb-1.5 w-52 py-1 rounded-xl glass-card border border-light-border dark:border-dark-border shadow-2xl opacity-0 translate-y-1 invisible group-hover:opacity-100 group-hover:translate-y-0 group-hover:visible transition-all duration-150 z-50">
                  {CAMPUS_CHOICES.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => setSelectedCampus(c.id)}
                      className={`w-full px-3 py-1.5 text-xs text-left flex items-center justify-between hover:bg-light-surface2 dark:hover:bg-dark-surface2 ${
                        selectedCampus === c.id ? "text-light-text dark:text-dark-text font-bold" : "text-light-muted dark:text-dark-muted"
                      }`}
                    >
                      <span>{c.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Mode Toggle: Normal / DeepThink */}
              <button
                type="button"
                onClick={() => setIsDeepThink((prev) => !prev)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-[11px] font-medium transition-all ${
                  isDeepThink
                    ? "bg-purple-500/15 border-purple-500/40 text-purple-600 dark:text-purple-300 font-bold"
                    : "border-light-border dark:border-dark-border bg-light-surface2 dark:bg-dark-surface2 text-light-muted dark:text-dark-muted hover:text-light-text dark:hover:text-dark-text"
                }`}
                title="DeepThink verification mode"
              >
                <Sparkles className="w-3 h-3" />
                <span>{isDeepThink ? "DeepThink" : "Normal"}</span>
              </button>

              {/* Writing Styles / Language */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowStyleMenu((prev) => !prev)}
                  className="flex items-center gap-1 px-2.5 py-1 rounded-lg border border-light-border dark:border-dark-border bg-light-surface2 dark:bg-dark-surface2 text-[11px] text-light-muted dark:text-dark-muted hover:text-light-text dark:hover:text-dark-text transition-all"
                >
                  <span>{writingStyle}</span>
                  <ChevronDown className="w-3 h-3" />
                </button>

                {showStyleMenu && (
                  <div className="absolute left-0 bottom-full mb-1.5 w-32 py-1 rounded-xl glass-card border border-light-border dark:border-dark-border shadow-2xl z-50">
                    {["Bilingual", "English", "Hinglish / Hindi"].map((style) => (
                      <button
                        key={style}
                        type="button"
                        onClick={() => {
                          setWritingStyle(style);
                          setShowStyleMenu(false);
                        }}
                        className={`w-full px-3 py-1.5 text-xs text-left hover:bg-light-surface2 dark:hover:bg-dark-surface2 ${
                          writingStyle === style ? "text-light-text dark:text-dark-text font-bold" : "text-light-muted dark:text-dark-muted"
                        }`}
                      >
                        {style}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Right Options: Citation, Voice, Send Button */}
            <div className="flex items-center gap-2">
              {/* Citation Switch */}
              <div className="flex items-center gap-1.5 cursor-pointer select-none">
                <button
                  type="button"
                  onClick={() => setCitationEnabled((prev) => !prev)}
                  className={`w-7 h-4 rounded-full p-0.5 transition-colors duration-200 ease-in-out ${
                    citationEnabled ? "bg-purple-600 dark:bg-purple-500" : "bg-light-border dark:bg-dark-border"
                  }`}
                  role="switch"
                  aria-checked={citationEnabled}
                >
                  <div
                    className={`w-3 h-3 rounded-full ${
                      citationEnabled ? "bg-white translate-x-3" : "bg-light-muted dark:bg-dark-muted translate-x-0"
                    } transition-transform duration-200 ease-in-out`}
                  />
                </button>
                <span className="text-[10px] font-medium text-light-muted dark:text-dark-muted">
                  Citation
                </span>
              </div>

              {/* Voice Mic Button */}
              <button
                type="button"
                onClick={toggleVoice}
                className={`p-1.5 rounded-full border border-light-border dark:border-dark-border bg-light-surface2 dark:bg-dark-surface2 text-light-text dark:text-dark-text transition-all ${
                  isListening ? "bg-red-500 text-white animate-pulse" : "hover:opacity-80"
                }`}
                title={isListening ? "Listening..." : "Voice input"}
              >
                {isListening ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
              </button>

              {/* Send Button */}
              <button
                type="button"
                disabled={isBusy || !input.trim()}
                onClick={onSubmit}
                aria-label="Send message"
                className="p-2 rounded-full bg-light-surface2 dark:bg-dark-surface2 border border-light-border dark:border-dark-border text-light-text dark:text-dark-text hover:bg-light-border dark:hover:bg-dark-surface3 disabled:opacity-30 shadow-sm active:scale-95 transition-all shrink-0 flex items-center justify-center"
              >
                {isBusy ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <ArrowUp className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Helper text */}
      <div className="flex items-center justify-between px-2 pt-2 text-[10px] text-light-muted dark:text-dark-muted font-mono">
        <span>AskCampus • Student Helpdesk</span>
        <span className="hidden sm:inline">
          Press <kbd className="px-1.5 py-0.5 rounded border border-light-border dark:border-dark-border text-[9px] bg-light-surface2 dark:bg-dark-surface2">Enter ↵</kbd>
        </span>
      </div>
    </div>
  );
}

export default Composer;
