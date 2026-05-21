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
    <main className="relative min-h-screen overflow-hidden bg-slate-50">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-400/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-400/10 blur-[120px]" />
      </div>

      <div className="mx-auto max-w-6xl px-6 py-16 lg:py-24">
        <div className="flex flex-col items-center text-center">
          <div className="mb-6 flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50/50 px-4 py-1.5 text-sm font-medium text-blue-700 shadow-sm">
            <Sparkles size={16} />
            <span>Smart Career Benchmarking</span>
          </div>

          <h1 className="max-w-4xl text-5xl font-extrabold tracking-tight text-slate-900 sm:text-7xl">
            AI Skill Gap{" "}
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Analyzer
            </span>
          </h1>

          <p className="mt-8 max-w-2xl text-lg leading-relaxed text-slate-600 sm:text-xl">
            Identify the bridge between your current academic knowledge and industry 
            requirements. Exclusively designed for <span className="font-semibold text-slate-900 text-blue-600">Engineering</span> and <span className="font-semibold text-slate-900 text-indigo-600">Commerce</span> students.
          </p>

          <div className="mt-10">
            <Button
              onClick={handleStart}
              disabled={loading}
              className="group relative flex h-14 items-center gap-2 overflow-hidden rounded-2xl bg-blue-600 px-10 text-lg font-semibold text-white transition-all hover:bg-blue-700 hover:shadow-xl hover:shadow-blue-200 disabled:opacity-70"
            >
              {loading ? "Initializing..." : (
                <>
                  Analyze My Skills
                  <ArrowRight className="transition-transform group-hover:translate-x-1" size={20} />
                </>
              )}
            </Button>
          </div>

          {error && (
            <div className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
              {error}
            </div>
          )}
        </div>

        <div className="mt-20 grid gap-6 sm:grid-cols-2">
          <div className="group relative overflow-hidden rounded-3xl border border-blue-100 bg-white p-8 transition-all hover:shadow-md">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                <Cpu size={24} />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Engineering Track</h3>
            </div>
            <p className="mt-4 text-slate-600">
              Analyzing technical stacks for SDE, Data Science, Core Engineering, and AI roles. 
              Find out which frameworks and tools you need to master.
            </p>
          </div>

          <div className="group relative overflow-hidden rounded-3xl border border-indigo-100 bg-white p-8 transition-all hover:shadow-md">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                <Briefcase size={24} />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Commerce Track</h3>
            </div>
            <p className="mt-4 text-slate-600">
              Gap analysis for Fintech, Business Analytics, Marketing, and Finance. 
              Discover high-demand certifications and modern corporate skills.
            </p>
          </div>
        </div>

        <div className="mt-20 border-t border-slate-200 pt-20">
          <div className="grid gap-8 sm:grid-cols-3">
            <div className="text-center sm:text-left">
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-900">
                <SearchCheck size={20} />
              </div>
              <h4 className="font-bold text-slate-900">Deep Skill Audit</h4>
              <p className="mt-2 text-sm text-slate-500">Scanning 50+ industry parameters to find exactly what you're missing.</p>
            </div>
            <div className="text-center sm:text-left">
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-900">
                <LineChart size={20} />
              </div>
              <h4 className="font-bold text-slate-900">Placement Readiness</h4>
              <p className="mt-2 text-sm text-slate-500">Know your score compared to current market hiring standards.</p>
            </div>
            <div className="text-center sm:text-left">
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-900">
                <Zap size={20} />
              </div>
              <h4 className="font-bold text-slate-900">Instant Roadmap</h4>
              <p className="mt-2 text-sm text-slate-500">Get a personalized learning path to fill the gaps in record time.</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}