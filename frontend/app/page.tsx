"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/Button";
import { useAssessment } from "@/context/AssessmentContext";
import { startAssessment } from "@/lib/api";
import { ApiError } from "@/lib/types";

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
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-slate-100 to-slate-200/80 px-4 py-16">
      <div className="mx-auto max-w-lg text-center">
        <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          AI Career Navigator
        </h1>
        <p className="mt-4 text-lg text-slate-600 sm:text-xl">
          Discover the best career path based on your personality and strengths
        </p>
        <div className="mt-10">
          <Button
            onClick={handleStart}
            disabled={loading}
            className="min-w-[200px] px-8 py-3 text-base"
          >
            {loading ? "Starting…" : "Start Assessment"}
          </Button>
        </div>
        {error && (
          <p
            className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
            role="alert"
          >
            {error}
          </p>
        )}
      </div>
    </main>
  );
}
