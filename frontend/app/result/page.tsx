"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { ResultCard } from "@/components/ResultCard";
import { useAssessment } from "@/context/AssessmentContext";
import { fetchAssessmentResult, fetchCareerAdvice } from "@/lib/api";
import type { AdviceResponse, TraitState } from "@/lib/types";
import { ApiError } from "@/lib/types";

function explanationToBullets(text: string): string[] {
  const lines = text
    .split(/\n/)
    .map((l) => l.trim())
    .filter(Boolean);
  if (!lines.length) return [text];
  return lines.map((line) =>
    line.replace(/^[-•*]\s*/, "").trim()
  );
}

function weakTraits(state: TraitState, take = 3): { name: string; value: number }[] {
  const entries = Object.entries(state) as [keyof TraitState, number][];
  return [...entries]
    .sort((a, b) => a[1] - b[1])
    .slice(0, take)
    .map(([name, value]) => ({ name, value }));
}

export default function ResultPage() {
  const router = useRouter();
  const { result, sessionId, setResult, resetAssessment } = useAssessment();
  const [advice, setAdvice] = useState<AdviceResponse | null>(null);
  const [adviceError, setAdviceError] = useState<string | null>(null);
  const [adviceLoading, setAdviceLoading] = useState(false);
  const [restoreLoading, setRestoreLoading] = useState(false);
  const [showTelemetry, setShowTelemetry] = useState(false);


  useEffect(() => {
    if (result || !sessionId) return;
    let cancelled = false;
    setRestoreLoading(true);
    fetchAssessmentResult(sessionId)
      .then((serverResult) => {
        if (cancelled) return;
        setResult({
          best_match: serverResult.best_match,
          alternatives: serverResult.alternatives,
          confidence: serverResult.confidence,
          state: serverResult.state,
        });
      })
      .catch(() => {
        if (!cancelled) router.replace("/");
      })
      .finally(() => {
        if (!cancelled) setRestoreLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [result, sessionId, setResult, router]);

  useEffect(() => {
    if (!result) return;
    const { state, best_match } = result;
    setAdviceLoading(true);
    setAdviceError(null);
    fetchCareerAdvice({
      analytical: state.analytical,
      creativity: state.creativity,
      social: state.social,
      risk: state.risk,
      discipline: state.discipline,
      career: best_match.role,
    })
      .then(setAdvice)
      .catch((e) => {
        const msg =
          e instanceof ApiError
            ? e.message
            : e instanceof Error
              ? e.message
              : "Could not load personalized advice.";
        setAdviceError(msg);
      })
      .finally(() => setAdviceLoading(false));
  }, [result]);

  const bullets = useMemo(
    () => (advice ? explanationToBullets(advice.explanation) : []),
    [advice]
  );

  const weakest = useMemo(
    () => (result ? weakTraits(result.state) : []),
    [result]
  );

  if (restoreLoading || !result) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-100">
        <p className="text-slate-600">{restoreLoading ? "Restoring result…" : "Redirecting…"}</p>
      </main>
    );
  }

  const altTwo = result.alternatives.slice(0, 2);

  return (

    <main className="relative min-h-screen px-4 py-12 sm:py-20 flex flex-col justify-center items-center overflow-hidden">
      {/* Background ambient light */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-[10%] left-[5%] w-72 h-72 rounded-full bg-indigo-500/5 blur-[100px] animate-float" />
        <div className="absolute bottom-[15%] right-[5%] w-80 h-80 rounded-full bg-cyan-500/5 blur-[100px] animate-float" style={{ animationDelay: "-4s" }} />
      </div>

      <div className="mx-auto flex w-full max-w-2xl flex-col gap-8">
        <header className="text-center sm:text-left">
          <h1 className="text-3xl font-black tracking-tight text-white sm:text-4xl drop-shadow-[0_2px_10px_rgba(255,255,255,0.15)]">
            Alignment Compiled
          </h1>
          <p className="mt-1.5 text-slate-400 font-medium">
            Your adaptive profiling results and skill roadmaps are now unlocked.
          </p>
        </header>

        <ResultCard match={result.best_match} highlight />

        {/* Dynamic Personality Skill Profile Dashboard */}
        <section>
          <h2 className="mb-4 text-xs font-bold uppercase tracking-widest text-indigo-400">
            Skill Parameter Calibration
          </h2>
          <Card className="flex flex-col gap-5 border border-slate-800 bg-slate-900/40">
            <p className="text-xs text-slate-400">
              Below is your compiled skill vector. These scores represent your responses parsed through the Bayesian inference algorithm.
            </p>
            <div className="flex flex-col gap-4">
              {([
                { key: "analytical", label: "Analytical Logic", color: "from-blue-500 to-cyan-400", desc: "Data analysis, math, and logical debugging." },
                { key: "creativity", label: "Creative Innovation", color: "from-purple-500 to-pink-500", desc: "Design thinking, imagination, and prototyping." },
                { key: "social", label: "Social Influence", color: "from-amber-500 to-orange-400", desc: "Teamwork, leadership, and public persuasion." },
                { key: "risk", label: "Risk Initiative", color: "from-rose-500 to-red-500", desc: "Taking initiative under high uncertainty and venture spirit." },
                { key: "discipline", label: "Discipline & Execution", color: "from-emerald-500 to-teal-500", desc: "Routine execution, timelines, and goal focus." }
              ] as const).map((trait) => {
                const val = result.state[trait.key] ?? 0.0;
                const percent = Math.round(val * 100);
                return (
                  <div key={trait.key} className="flex flex-col gap-1.5">
                    <div className="flex justify-between items-baseline text-xs">
                      <span className="font-bold text-slate-200">{trait.label}</span>
                      <span className="font-black text-cyan-400 tabular-nums">{percent}% Fit</span>
                    </div>
                    <div className="relative h-2 w-full rounded-full bg-slate-950 border border-slate-800 p-[1px]">
                      <div
                        className={`h-full rounded-full bg-gradient-to-r ${trait.color} transition-[width] duration-700 ease-out`}
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-slate-400 leading-normal">{trait.desc}</span>
                  </div>
                );
              })}
            </div>
          </Card>
        </section>

        <section>
          <h2 className="mb-4 text-xs font-bold uppercase tracking-widest text-indigo-400">
            Alternative Roles
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {altTwo.length ? (
              altTwo.map((m) => (
                <ResultCard key={m.role} match={m} />
              ))
            ) : (
              <p className="text-sm text-slate-500">No alternatives returned.</p>
            )}
          </div>
        </section>

        <section>
          <h2 className="mb-4 text-xs font-bold uppercase tracking-widest text-indigo-400">
            Fit Explanation
          </h2>
          <Card>
            {adviceLoading ? (
              <LoadingSpinner label="Compiling advisor intelligence…" />
            ) : adviceError ? (
              <p className="text-sm text-red-400" role="alert">
                ⚠️ {adviceError}
              </p>
            ) : (
              <ul className="space-y-3.5 text-slate-200">
                {bullets.map((line, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm leading-relaxed">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-400 shadow-[0_0_8px_#22d3ee] content-['']" />
                    <span>{line}</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </section>

        <section>
          <h2 className="mb-4 text-xs font-bold uppercase tracking-widest text-indigo-400">
            Vector Discrepancy (Skill Gap)
          </h2>
          <Card>
            <p className="mb-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Under-calibrated Traits:
            </p>
            <ul className="mb-6 flex flex-wrap gap-2.5">
              {weakest.map(({ name, value }) => (
                <li
                  key={name}
                  className="rounded-lg bg-rose-500/10 border border-rose-500/20 px-3.5 py-1.5 text-xs font-bold capitalize text-rose-300 shadow-[0_0_10px_rgba(244,63,94,0.1)]"
                >
                  {name}{" "}
                  <span className="tabular-nums text-rose-400 ml-1">
                    {Math.round(value * 100)}%
                  </span>
                </li>
              ))}
            </ul>
            {advice?.skill_gap?.length ? (
              <ul className="space-y-3 border-t border-slate-800 pt-5">
                {advice.skill_gap.map((item, i) => (
                  <li
                    key={i}
                    className="flex gap-3 text-sm leading-relaxed text-slate-300 items-start"
                  >
                    <span className="mt-2 h-1 w-2 shrink-0 rounded bg-rose-400 shadow-[0_0_6px_#f43f5e] content-['']" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            ) : !adviceLoading && !adviceError ? (
              <p className="text-sm text-slate-500">No skill gap items.</p>
            ) : null}
          </Card>
        </section>

        <section>
          <h2 className="mb-4 text-xs font-bold uppercase tracking-widest text-indigo-400">
            Roadmap to Master Path
          </h2>
          <Card>
            {adviceLoading ? (
              <LoadingSpinner label="Synthesizing roadmap nodes…" />
            ) : adviceError ? null : advice?.roadmap?.length ? (
              <ol className="space-y-5">
                {advice.roadmap.map((step, i) => (
                  <li key={i} className="flex gap-4">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-slate-700 bg-slate-800/80 text-xs font-black text-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.1)]">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <p className="pt-1 text-sm leading-relaxed text-slate-300">
                      {step}
                    </p>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="text-sm text-slate-500">No roadmap steps.</p>
            )}
          </Card>
        </section>

        <div className="flex flex-col gap-3 pb-8 sm:flex-row sm:justify-center">
          <Button
            variant="secondary"
            className="w-full sm:w-auto uppercase tracking-wider text-xs font-bold px-8"
            onClick={() => {
              resetAssessment();
              router.push("/");
            }}
          >
            Start New Quest
          </Button>
        </div>

        {/* Professor Debug Panel */}
        <div className="mt-6 border-t border-slate-800 pt-6 flex flex-col items-center">
          <Button
            variant="ghost"
            onClick={() => setShowTelemetry(!showTelemetry)}
            className="text-xs uppercase font-bold tracking-wider text-slate-500 hover:text-cyan-400 transition-colors flex items-center gap-1.5"
          >
            🔧 {showTelemetry ? "Hide" : "Show"} Developer Telemetry (Professor Mode)
          </Button>
          {showTelemetry && (
            <div className="w-full mt-4 rounded-2xl bg-black border border-slate-800 p-5 font-mono text-[10px] text-green-400 shadow-inner max-h-[300px] overflow-auto flex flex-col gap-3">
              <div>
                <span className="text-slate-500">{"// Algorithm Session State"}</span>
                <p><span className="text-cyan-400">session_id:</span> &quot;{sessionId}&quot;</p>
                <p><span className="text-cyan-400">confidence:</span> {result.confidence}</p>
              </div>
              <div>
                <span className="text-slate-500">{"// Bayesian Posterior Probabilities (Clamped [0, 1])"}</span>
                <pre className="text-emerald-300 bg-slate-950 p-2 rounded border border-slate-900 mt-1">
                  {JSON.stringify(result.state, null, 2)}
                </pre>
              </div>
              <div>
                <span className="text-slate-500">{"// Scored Careers Cosine Blending"}</span>
                <pre className="text-cyan-300 bg-slate-950 p-2 rounded border border-slate-900 mt-1">
                  {JSON.stringify({
                    best_match: result.best_match,
                    alternatives: result.alternatives
                  }, null, 2)}
                </pre>
              </div>

            </div>
          )}
        </div>
      </div>
    </main>
  );
}

