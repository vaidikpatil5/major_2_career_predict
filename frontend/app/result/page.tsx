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
    <main className="min-h-screen bg-slate-100 px-4 py-10 sm:py-14">
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <header className="text-center sm:text-left">
          <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">
            Your results
          </h1>
          <p className="mt-1 text-slate-600">
            Personalized career alignment from your assessment.
          </p>
        </header>

        <ResultCard match={result.best_match} highlight />

        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Alternatives
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
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Explanation
          </h2>
          <Card>
            {adviceLoading ? (
              <LoadingSpinner label="Generating your explanation…" />
            ) : adviceError ? (
              <p className="text-sm text-red-700" role="alert">
                {adviceError}
              </p>
            ) : (
              <ul className="list-inside list-disc space-y-3 text-slate-700">
                {bullets.map((line, i) => (
                  <li key={i} className="pl-1 leading-relaxed">
                    {line}
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </section>

        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Skill gap
          </h2>
          <Card>
            <p className="mb-4 text-sm text-slate-600">
              Traits with the lowest relative scores in your profile — worth
              strengthening over time:
            </p>
            <ul className="mb-6 flex flex-wrap gap-2">
              {weakest.map(({ name, value }) => (
                <li
                  key={name}
                  className="rounded-lg bg-amber-50 px-3 py-1 text-xs font-medium capitalize text-amber-900 ring-1 ring-amber-200"
                >
                  {name}{" "}
                  <span className="tabular-nums text-amber-700">
                    ({Math.round(value * 100)}%)
                  </span>
                </li>
              ))}
            </ul>
            {advice?.skill_gap?.length ? (
              <ul className="space-y-2 border-t border-slate-100 pt-4">
                {advice.skill_gap.map((item, i) => (
                  <li
                    key={i}
                    className="flex gap-2 text-sm text-slate-700 before:mt-2 before:h-1.5 before:w-1.5 before:shrink-0 before:rounded-full before:bg-indigo-400 before:content-['']"
                  >
                    {item}
                  </li>
                ))}
              </ul>
            ) : !adviceLoading && !adviceError ? (
              <p className="text-sm text-slate-500">No skill gap items.</p>
            ) : null}
          </Card>
        </section>

        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Roadmap
          </h2>
          <Card>
            {adviceLoading ? (
              <p className="text-sm text-slate-500">Loading roadmap…</p>
            ) : adviceError ? null : advice?.roadmap?.length ? (
              <ol className="space-y-4">
                {advice.roadmap.map((step, i) => (
                  <li key={i} className="flex gap-4">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-sm font-bold text-indigo-700">
                      {i + 1}
                    </span>
                    <p className="pt-1 text-sm leading-relaxed text-slate-700">
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
            className="w-full sm:w-auto"
            onClick={() => {
              resetAssessment();
              router.push("/");
            }}
          >
            Start over
          </Button>
        </div>
      </div>
    </main>
  );
}
