"use client";

import { useEffect, useRef, useState } from "react";

interface MascotCharacterProps {
  currentQuestionIndex: number;
  isLoading: boolean;
}

export function MascotCharacter({
  currentQuestionIndex,
  isLoading,
}: MascotCharacterProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const leftPupilRef = useRef<SVGCircleElement>(null);
  const rightPupilRef = useRef<SVGCircleElement>(null);
  const [speechText, setSpeechText] = useState("Initializing systems...");
  const [isBlinking, setIsBlinking] = useState(false);

  // Dynamic context-aware dialog speech lines
  useEffect(() => {
    if (isLoading) {
      const loadingPhrases = [
        "Analyzing response vectors...",
        "Scanning brainwaves...",
        "Compiling profile matrix...",
        "Running trait projection...",
      ];
      setSpeechText(loadingPhrases[Math.floor(Math.random() * loadingPhrases.length)]);
      return;
    }

    if (currentQuestionIndex === 0) {
      setSpeechText("Ready to start the assessment? Let's check those traits!");
    } else if (currentQuestionIndex === 1) {
      setSpeechText("Good start! Analyzing your responses in real time...");
    } else if (currentQuestionIndex === 3) {
      setSpeechText("Fascinating choice. My telemetry nodes are lit!");
    } else if (currentQuestionIndex === 5) {
      setSpeechText("We are halfway! Excellent consistency in your replies.");
    } else if (currentQuestionIndex === 7) {
      setSpeechText("Computing career vectors... almost there!");
    } else {
      const generalPhrases = [
        "Calibrating...",
        "Processing cognitive signals...",
        "You're doing great!",
        "Every choice defines your profile...",
        "Integrating trait coordinates...",
        "Updating career recommendation graph...",
      ];
      setSpeechText(generalPhrases[currentQuestionIndex % generalPhrases.length]);
    }
  }, [currentQuestionIndex, isLoading]);

  // Periodic Blink Animation: closed eye state is toggled briefly
  useEffect(() => {
    const triggerBlink = () => {
      setIsBlinking(true);
      setTimeout(() => {
        setIsBlinking(false);
      }, 150);
    };

    const interval = setInterval(() => {
      triggerBlink();
    }, 3500 + Math.random() * 2500); // random interval between 3.5s and 6s

    return () => clearInterval(interval);
  }, []);

  // Cursor Eye-tracking math
  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      if (!containerRef.current || !leftPupilRef.current || !rightPupilRef.current) return;

      const container = containerRef.current;
      const mouseX = event.clientX;
      const mouseY = event.clientY;

      // Get container center as base reference to prevent pupil offset feedback jitter
      const rect = container.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const dx = mouseX - centerX;
      const dy = mouseY - centerY;
      const dist = Math.sqrt(dx * dx + dy * dy);

      // Max travel distance for the pupil within the socket
      const maxOffset = 5.5; 
      // Scale translation by distance, capped at maxOffset
      const offset = Math.min(dist * 0.05, maxOffset);
      const angle = Math.atan2(dy, dx);

      const translateX = offset * Math.cos(angle);
      const translateY = offset * Math.sin(angle);

      // Apply coordinates dynamically
      const transformValue = `translate(${translateX}px, ${translateY}px)`;
      leftPupilRef.current.style.transform = transformValue;
      rightPupilRef.current.style.transform = transformValue;
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div
      ref={containerRef}
      className="flex flex-col items-center gap-2 animate-float relative select-none w-full max-w-[320px] mx-auto py-2"
    >
      {/* Dynamic Speech Bubble */}
      <div className="relative bg-slate-900/90 border border-slate-700/80 text-[11px] text-cyan-300 font-semibold px-4 py-2 rounded-xl shadow-[0_4px_16px_rgba(0,0,0,0.5)] text-center w-full max-w-[250px] transition-all duration-300">
        <div className="absolute bottom-[-6px] left-[50%] -translate-x-[50%] w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[6px] border-t-slate-700" />
        <div className="absolute bottom-[-5px] left-[50%] -translate-x-[50%] w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-t-[5px] border-t-slate-900" />
        <span className="tracking-wide">{speechText}</span>
      </div>

      {/* Retro-Futuristic Companion Robot */}
      <div className="w-[88px] h-[88px]">
        <svg
          viewBox="0 0 100 100"
          className="w-full h-full filter drop-shadow-[0_0_8px_rgba(6,182,212,0.25)]"
        >
          {/* Antennas */}
          <path
            d="M 28,26 L 36,38 M 72,26 L 64,38"
            stroke="#475569"
            strokeWidth="3"
            strokeLinecap="round"
          />
          {/* Antenna glowing tips */}
          <circle cx="28" cy="26" r="3.5" className="fill-indigo-500 animate-pulse-glow" style={{ animationDuration: "2s" }} />
          <circle cx="72" cy="26" r="3.5" className="fill-cyan-400 animate-pulse-glow" style={{ animationDuration: "1.5s" }} />

          {/* Neck Link */}
          <rect x="45" y="74" width="10" height="8" rx="2" fill="#334155" stroke="#475569" strokeWidth="1.5" />

          {/* Robot Head Body */}
          <rect
            x="22"
            y="34"
            width="56"
            height="42"
            rx="12"
            fill="#1e293b"
            stroke="#475569"
            strokeWidth="2"
          />

          {/* Visor Screen */}
          <rect
            x="27"
            y="39"
            width="46"
            height="24"
            rx="8"
            fill="#0f172a"
            stroke="#06b6d4"
            strokeWidth="1.5"
          />

          {/* Left Eye Sockets */}
          <ellipse cx="39" cy="51" rx="7" ry="7" fill="#1b2537" />
          {/* Right Eye Sockets */}
          <ellipse cx="61" cy="51" rx="7" ry="7" fill="#1b2537" />

          {/* Interactive Pupils */}
          <circle
            ref={leftPupilRef}
            cx="39"
            cy="51"
            r={isBlinking ? "0" : "3.5"}
            fill="#06b6d4"
            className="transition-transform duration-75 ease-out shadow-[0_0_8px_rgba(6,182,212,0.8)]"
          />
          <circle
            ref={rightPupilRef}
            cx="61"
            cy="51"
            r={isBlinking ? "0" : "3.5"}
            fill="#06b6d4"
            className="transition-transform duration-75 ease-out shadow-[0_0_8px_rgba(6,182,212,0.8)]"
          />

          {/* Pulse Telemetry Wave (Mouth) */}
          <path
            d="M 43,58 Q 50,62 57,58"
            fill="none"
            stroke="#06b6d4"
            strokeWidth="1.5"
            strokeLinecap="round"
            className="opacity-80"
          />

          {/* Decorative Rivets */}
          <circle cx="16" cy="55" r="1" fill="#475569" />
          <circle cx="84" cy="55" r="1" fill="#475569" />
        </svg>
      </div>
    </div>
  );
}
