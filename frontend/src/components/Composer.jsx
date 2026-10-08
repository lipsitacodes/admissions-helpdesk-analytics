import React, { useRef, useEffect, useState } from "react";
import {
  ArrowUp,
  Sparkles,
  Mic,
  MicOff,
  ChevronDown,
  Loader2,
  Globe,
} from "lucide-react";
import { FeesabilityLogo } from "./FeesabilityLogo";

export const LANGUAGE_OPTIONS = [
  { id: "en", label: "English", display: "English" },
  { id: "or", label: "ଓଡ଼ିଆ Odia", display: "ଓଡ଼ିଆ Odia" },
  { id: "hi", label: "हिन्दी Hindi", display: "हिन्दी Hindi" },
];

export function Composer({
  input,
  setInput,
  onSubmit,
  isBusy,
  errorMessage,
  citationEnabled,
  setCitationEnabled,
  targetLanguage = "en",
  setTargetLanguage = () => {},
}) {
  const textareaRef = useRef(null);
  const [isDeepThink, setIsDeepThink] = useState(false);
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const currentLang =
    LANGUAGE_OPTIONS.find((l) => l.id === targetLanguage) ||
    LANGUAGE_OPTIONS.find((l) => l.id === "en") ||
    LANGUAGE_OPTIONS[0];

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

  const toggleVoice = async () => {
    if (isRecording) {
      // Stop recording and let onstop dispatch to Whisper /transcribe
      try {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
          mediaRecorderRef.current.stop();
        }
      } catch {
        setIsRecording(false);
      }
      return;
    }

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Audio recording is not supported in this browser. Please type your question.");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];

      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "";

      const options = mimeType ? { mimeType } : undefined;
      const recorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        setIsRecording(false);
        // Release hardware audio tracks
        try {
          stream.getTracks().forEach((track) => track.stop());
        } catch {
          // ignore
        }

        const audioBlob = new Blob(audioChunksRef.current, {
          type: mimeType || "audio/webm",
        });

        if (audioBlob.size === 0) return;

        setIsTranscribing(true);
        try {
          const formData = new FormData();
          formData.append("audio", audioBlob, "user_speech.webm");

          const response = await fetch("/transcribe", {
            method: "POST",
            body: formData,
          });

          const data = await response.json().catch(() => null);

          if (response.ok && data?.transcription) {
            setInput((prev) => {
              const text = data.transcription.trim();
              return prev ? `${prev} ${text}` : text;
            });
          } else {
            alert(
              data?.error ||
                "Unable to transcribe audio. Please try again or type your question."
            );
          }
        } catch {
          alert("Unable to transcribe audio. Please try again or type your question.");
        } finally {
          setIsTranscribing(false);
        }
      };

      recorder.start();
      setIsRecording(true);
    } catch (err) {
      console.warn("Microphone access error:", err);
      alert("Unable to access microphone. Please allow microphone permissions or type your question.");
      setIsRecording(false);
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

      {/* Outer Multi-color Neon Aura Container */}
      <div className="neon-aura-container relative">
        <div className="relative z-10 rounded-2xl border border-light-border dark:border-dark-border bg-light-surface dark:bg-dark-surface p-3.5 sm:p-4 shadow-xl transition-all">
          {/* Main Input Text Area with Sparkle Icon */}
          <div className="flex items-start gap-2.5">
            <Sparkles className="w-4 h-4 text-light-text dark:text-dark-text mt-1 shrink-0 opacity-80" />
            <textarea
              ref={textareaRef}
              rows={1}
              autoFocus
              value={input}
              disabled={isBusy || isTranscribing}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                isRecording
                  ? "Listening to voice input... Click mic again when finished speaking."
                  : isTranscribing
                  ? "Transcribing audio with Whisper AI..."
                  : "Ask a question (e.g., CSE fees, CUEE 2026, hostel, scholarships)..."
              }
              className="w-full bg-transparent resize-none border-none text-xs sm:text-sm text-light-text dark:text-dark-text placeholder:text-light-muted dark:placeholder:text-dark-muted focus:outline-none max-h-36 py-0.5 leading-relaxed"
            />
          </div>

          {/* Bottom Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-light-border dark:border-dark-border mt-2">
            {/* Left Options Pills */}
            <div className="flex flex-wrap items-center gap-1.5">
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

              {/* Language Dropdown Selector (English, ଓଡ଼ିଆ Odia, हिन्दी Hindi) */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowLangMenu((prev) => !prev)}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-light-border dark:border-dark-border bg-light-surface2 dark:bg-dark-surface2 text-[11px] font-medium text-light-text dark:text-dark-text hover:border-light-borderLight dark:hover:border-dark-borderLight transition-all"
                  title="Target Response Language"
                >
                  <Globe className="w-3 h-3 text-purple-500 opacity-80" />
                  <span className="font-semibold">{currentLang.display}</span>
                  <ChevronDown className="w-3 h-3 text-light-muted dark:text-dark-muted" />
                </button>

                {showLangMenu && (
                  <div className="absolute left-0 bottom-full mb-1.5 w-36 py-1 rounded-xl glass-card border border-light-border dark:border-dark-border shadow-2xl z-50">
                    {LANGUAGE_OPTIONS.map((lang) => (
                      <button
                        key={lang.id}
                        type="button"
                        onClick={() => {
                          setTargetLanguage(lang.id);
                          setShowLangMenu(false);
                        }}
                        className={`w-full px-3 py-1.5 text-xs text-left flex items-center justify-between hover:bg-light-surface2 dark:hover:bg-dark-surface2 ${
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

              {/* Voice Mic Button with Whisper Integration */}
              <button
                type="button"
                onClick={toggleVoice}
                disabled={isTranscribing || isBusy}
                className={`p-1.5 rounded-full border border-light-border dark:border-dark-border bg-light-surface2 dark:bg-dark-surface2 text-light-text dark:text-dark-text transition-all ${
                  isRecording
                    ? "bg-red-500 text-white animate-pulse"
                    : isTranscribing
                    ? "opacity-50"
                    : "hover:opacity-80"
                }`}
                title={
                  isRecording
                    ? "Recording voice... Click to transcribe with Whisper"
                    : isTranscribing
                    ? "Transcribing audio with Whisper AI..."
                    : "Voice input (Whisper)"
                }
              >
                {isTranscribing ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : isRecording ? (
                  <MicOff className="w-3.5 h-3.5" />
                ) : (
                  <Mic className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Send Button */}
              <button
                type="button"
                disabled={isBusy || !input.trim() || isTranscribing}
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
        <span className="flex items-center gap-1.5">
          <FeesabilityLogo className="w-3.5 h-3.5 text-light-muted dark:text-dark-muted shrink-0" />
          <span>FEESABILITY • Student Helpdesk</span>
        </span>
        <span className="hidden sm:inline">
          Press <kbd className="px-1.5 py-0.5 rounded border border-light-border dark:border-dark-border text-[9px] bg-light-surface2 dark:bg-dark-surface2">Enter ↵</kbd>
        </span>
      </div>
    </div>
  );
}

export default Composer;
