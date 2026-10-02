import React, { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";

export function OrbLogo({
  size = "md",
  animated = true,
  className = "",
  onClick,
  title,
  interactive = true,
}) {
  const sizeClasses = {
    sm: "w-7 h-7",
    md: "w-12 h-12",
    lg: "w-20 h-20",
    xl: "w-28 h-28",
  };

  const [isPlayMode, setIsPlayMode] = useState(false);
  const containerRef = useRef(null);
  const mainOrbRef = useRef(null);
  const trail1Ref = useRef(null);
  const trail2Ref = useRef(null);
  const isPlayModeRef = useRef(isPlayMode);

  useEffect(() => {
    isPlayModeRef.current = isPlayMode;
  }, [isPlayMode]);

  const handleMouseMove = useCallback((e) => {
    if (!isPlayModeRef.current || !containerRef.current || !mainOrbRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const homeCenterX = rect.left + rect.width / 2;
    const homeCenterY = rect.top + rect.height / 2;

    const mouseX = e.clientX;
    const mouseY = e.clientY;

    const dx = mouseX - homeCenterX;
    const dy = mouseY - homeCenterY;

    // Smooth GSAP trailing follow for pink/purple orb
    gsap.to(mainOrbRef.current, {
      x: dx,
      y: dy,
      duration: 0.15,
      ease: "power2.out",
      overwrite: "auto",
    });

    if (trail1Ref.current) {
      gsap.to(trail1Ref.current, {
        x: dx,
        y: dy,
        duration: 0.35,
        ease: "power2.out",
        overwrite: "auto",
      });
    }

    if (trail2Ref.current) {
      gsap.to(trail2Ref.current, {
        x: dx,
        y: dy,
        duration: 0.55,
        ease: "power1.out",
        overwrite: "auto",
      });
    }
  }, []);

  // Return to home resting position
  const returnToHome = useCallback(() => {
    setIsPlayMode(false);
    const elements = [mainOrbRef.current, trail1Ref.current, trail2Ref.current].filter(Boolean);
    gsap.to(elements, {
      x: 0,
      y: 0,
      duration: 0.8,
      ease: "elastic.out(1, 0.4)",
      overwrite: "auto",
    });
  }, []);

  useEffect(() => {
    if (!isPlayMode) return;

    window.addEventListener("mousemove", handleMouseMove, { passive: true });

    const handleKeyDown = (e) => {
      if (e.key === "Escape") returnToHome();
    };
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isPlayMode, handleMouseMove, returnToHome]);

  const handleClick = (e) => {
    if (onClick) onClick(e);
    if (!interactive) return;

    if (isPlayMode) {
      returnToHome();
    } else {
      setIsPlayMode(true);
    }
  };

  const orbSizePx = {
    sm: 28,
    md: 48,
    lg: 80,
    xl: 112,
  }[size] || 48;

  return (
    <div
      ref={containerRef}
      onClick={handleClick}
      title={title || (interactive ? (isPlayMode ? "Click to release orb" : "Click to play with orb!") : undefined)}
      className={`relative flex items-center justify-center shrink-0 select-none ${
        interactive || onClick ? "cursor-pointer" : ""
      } ${animated && !isPlayMode ? "animate-float-orb" : ""} ${className}`}
    >
      {/* Background Neon Halo */}
      <div
        className={`absolute rounded-full bg-purple-500/40 blur-xl transition-all duration-300 ${
          animated && !isPlayMode ? "animate-pulse-glow" : ""
        } ${isPlayMode ? "scale-125 bg-purple-400/60 blur-2xl" : ""} ${
          size === "xl" ? "w-36 h-36" : size === "lg" ? "w-28 h-28" : "w-16 h-16"
        }`}
      />

      {/* Play Mode Trail Micro Orb 2 */}
      {isPlayMode && (
        <div
          ref={trail2Ref}
          className="absolute rounded-full orb-glow-purple pointer-events-none opacity-40 blur-[1px]"
          style={{
            width: orbSizePx * 0.5,
            height: orbSizePx * 0.5,
            zIndex: 40,
          }}
        />
      )}

      {/* Play Mode Trail Micro Orb 1 */}
      {isPlayMode && (
        <div
          ref={trail1Ref}
          className="absolute rounded-full orb-glow-purple pointer-events-none opacity-65"
          style={{
            width: orbSizePx * 0.75,
            height: orbSizePx * 0.75,
            zIndex: 45,
          }}
        />
      )}

      {/* Main 3D Pink/Purple Iridescent Sphere */}
      <div
        ref={mainOrbRef}
        className={`relative rounded-full orb-glow-purple transition-transform duration-200 ${
          isPlayMode ? "scale-110 shadow-2xl ring-2 ring-purple-300/50" : "hover:scale-110"
        } ${sizeClasses[size] || sizeClasses.md}`}
        style={{ zIndex: 50 }}
      >
        {/* Soft specular highlight reflection */}
        <div className="absolute top-1.5 left-2 w-3 h-2.5 rounded-full bg-white/80 blur-[1px] transform -rotate-45 pointer-events-none" />

        {/* Play mode indicator ring */}
        {isPlayMode && (
          <div className="absolute -inset-2 rounded-full border border-purple-300/60 animate-ping pointer-events-none opacity-75" />
        )}
      </div>

      {/* Interactive Tooltip Badge when playing */}
      {isPlayMode && (
        <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap bg-purple-900/90 text-purple-100 text-[10px] font-medium px-2.5 py-0.5 rounded-full border border-purple-400/40 shadow-lg pointer-events-none animate-bounce z-50">
          ✨ Playing! Click orb to place back
        </div>
      )}
    </div>
  );
}

export default OrbLogo;
