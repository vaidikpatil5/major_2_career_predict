"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/Button";
import { useAssessment } from "@/context/AssessmentContext";
import { startAssessment } from "@/lib/api";
import { ApiError } from "@/lib/types";
import { Sparkles, ArrowRight, Cpu, Briefcase, SearchCheck, LineChart, Zap } from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const { setSessionFromStart } = useAssessment();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleStart() {
    setError(null);
    setLoading(true);
    try {
      const data = await startAssessment();
      setSessionFromStart(data.session_id, data.question);
      router.push("/assessment");
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? e.message
          : e instanceof Error
            ? e.message
            : "Something went wrong.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden px-4 py-16 sm:px-6 lg:py-24">
      {/* Floating game ambient particles */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-[10%] left-[5%] w-72 h-72 rounded-full bg-indigo-500/10 blur-[100px] animate-float" />
        <div className="absolute bottom-[10%] right-[5%] w-80 h-80 rounded-full bg-cyan-500/10 blur-[100px] animate-float" style={{ animationDelay: "-2s" }} />
      </div>

      <div className="mx-auto max-w-5xl">
        <div className="flex flex-col items-center text-center">
          {/* Smart Badge */}
          <div className="mb-8 flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-950/40 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-indigo-300 shadow-[0_0_15px_rgba(99,102,241,0.15)] backdrop-blur-md">
            <Sparkles size={14} className="text-cyan-400" />
            <span>Interactive Assessment Arena</span>
          </div>

          {/* Gamified Title */}
          <h1 className="max-w-3xl text-5xl font-black tracking-tight text-white sm:text-7xl">
            Uncover Your AI{" "}
            <span className="bg-gradient-to-r from-cyan-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent drop-shadow-[0_2px_10px_rgba(99,102,241,0.3)]">
              Career Path
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mt-6 max-w-xl text-base leading-relaxed text-slate-400 sm:text-lg">
            An adaptive skill-matching quest designed for <span className="font-semibold text-cyan-400">Engineering</span> and <span className="font-semibold text-indigo-400">Commerce</span> students. Identify skill gaps and unlock your learning roadmap.
          </p>

          {/* Start CTA Button */}
          <div className="mt-10">
            <Button
              onClick={handleStart}
              disabled={loading}
              className="group relative flex h-14 items-center gap-3 overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500 px-10 text-lg font-black uppercase tracking-wider text-white transition-all shadow-[0_0_30px_rgba(99,102,241,0.4)] hover:shadow-[0_0_40px_rgba(99,102,241,0.7)] hover:scale-105 active:scale-95 disabled:opacity-50"
            >
              {loading ? "Booting Engine..." : (
                <>
                  Start Assessment Quest
                  <ArrowRight className="transition-transform group-hover:translate-x-1" size={20} />
                </>
              )}
            </Button>
          </div>

          {error && (
            <div className="mt-6 rounded-xl border border-red-900/50 bg-red-950/20 px-4 py-3 text-sm text-red-400">
              {error}
            </div>
          )}
        </div>

        {/* Track Selector Cards */}
        <div className="mt-20 grid gap-6 sm:grid-cols-2">
          <div className="group relative overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/40 p-8 transition-all hover:border-cyan-500/40 hover:shadow-[0_0_20px_rgba(6,182,212,0.1)]">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-950/50 text-cyan-400 group-hover:bg-cyan-500 group-hover:text-slate-950 transition-colors shadow-[0_0_15px_rgba(6,182,212,0.2)]">
                <Cpu size={24} />
              </div>
              <h3 className="text-xl font-bold text-white">Engineering Track</h3>
            </div>
            <p className="mt-4 text-slate-400">
              Scans technical stacks for Software Developers, Data Scientists, and AI Engineers. Discover modern frameworks and cloud tools you need to master.
            </p>
          </div>

          <div className="group relative overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/40 p-8 transition-all hover:border-indigo-500/40 hover:shadow-[0_0_20px_rgba(99,102,241,0.1)]">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-950/50 text-indigo-400 group-hover:bg-indigo-500 group-hover:text-slate-950 transition-colors shadow-[0_0_15px_rgba(99,102,241,0.2)]">
                <Briefcase size={24} />
              </div>
              <h3 className="text-xl font-bold text-white">Commerce Track</h3>
            </div>
            <p className="mt-4 text-slate-400">
              Gap analysis for Business Analytics, Product Management, and Finance. Learn high-demand corporate credentials and analysis tools.
            </p>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="mt-20 border-t border-slate-800 pt-20">
          <div className="grid gap-8 sm:grid-cols-3">
            <div className="text-center sm:text-left">
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-slate-800/80 text-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.1)]">
                <SearchCheck size={20} />
              </div>
              <h4 className="font-bold text-white">Adaptive Scan Engine</h4>
              <p className="mt-2 text-sm text-slate-400">Dynamically picks queries based on your answers to map trait points.</p>
            </div>
            <div className="text-center sm:text-left">
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-slate-800/80 text-indigo-400 shadow-[0_0_10px_rgba(99,102,241,0.1)]">
                <LineChart size={20} />
              </div>
              <h4 className="font-bold text-white">Industry Calibration</h4>
              <p className="mt-2 text-sm text-slate-400">Compares your scores to real-world engineering and business hiring profiles.</p>
            </div>
            <div className="text-center sm:text-left">
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-slate-800/80 text-purple-400 shadow-[0_0_10px_rgba(168,85,247,0.1)]">
                <Zap size={20} />
              </div>
              <h4 className="font-bold text-white">AI Advice Roadmap</h4>
              <p className="mt-2 text-sm text-slate-400">Returns actionable instructions generated specifically for your profile.</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}