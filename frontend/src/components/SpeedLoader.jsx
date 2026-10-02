import React from "react";
import { Zap, Cpu, Sparkles } from "lucide-react";
import "./SpeedLoader.css";

export function SpeedLoader({
  title = "Loading FEESABILITY Intelligence",
  subtitle = "Synchronizing with institutional admissions database",
  fullScreen = true,
  onDismiss,
}) {
  const content = (
    <div className="relative w-full max-w-xl mx-auto flex flex-col items-center justify-center p-6 text-center select-none">
      {/* Background Long Fazers */}
      <div className="speed-longfazers">
        <span></span>
        <span></span>
        <span></span>
        <span></span>
      </div>

      {/* Runner Loader Graphic */}
      <div className="speed-loader-wrapper">
        <div className="speed-loader">
          <span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
          </span>
          <div className="speed-base">
            <span></span>
            <div className="speed-face"></div>
          </div>
        </div>
      </div>

      {/* Text & Progress State */}
      <div className="relative z-20 mt-4 space-y-3 w-full">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold tracking-wider uppercase border border-emerald-500/30 bg-emerald-500/10 text-emerald-500 dark:text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
          <span>Hyper-Speed Vector Protocol</span>
        </div>

        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-light-text dark:text-dark-text uppercase font-space">
          {title}
        </h2>

        <p className="text-xs sm:text-sm text-light-muted dark:text-dark-muted font-light max-w-md mx-auto">
          {subtitle}
        </p>

        {/* Progress Bar */}
        <div className="w-64 h-1.5 bg-light-surface2 dark:bg-dark-surface2 rounded-full mx-auto mt-6 overflow-hidden relative border border-light-border dark:border-dark-border">
          <div className="h-full bg-light-text dark:bg-dark-text w-1/3 rounded-full animate-loader-progress shadow-sm"></div>
        </div>
      </div>

      {/* Decorative Telemetry Badges */}
      <div className="w-full flex items-center justify-between pt-10 text-[10px] text-light-muted dark:text-dark-muted font-mono opacity-60">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>SYSTEMS NOMINAL</span>
        </div>
        <div className="hidden sm:flex items-center gap-1">
          <Cpu className="w-3 h-3" />
          <span>LATENCY: 12ms // 12-LAYER RAG</span>
        </div>
      </div>

      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="mt-6 text-[11px] font-medium text-light-muted dark:text-dark-muted hover:text-light-text dark:hover:text-dark-text underline underline-offset-4 transition-colors"
        >
          Skip animation →
        </button>
      )}
    </div>
  );

  if (!fullScreen) {
    return (
      <div className="relative w-full rounded-2xl glass-card border border-light-border dark:border-dark-border p-6 overflow-hidden my-4">
        {content}
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-light-bg/95 dark:bg-dark-bg/95 backdrop-blur-md transition-opacity duration-500">
      {content}
    </div>
  );
}

export default SpeedLoader;
