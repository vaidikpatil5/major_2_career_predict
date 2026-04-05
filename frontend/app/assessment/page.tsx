"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { ProgressBar } from "@/components/ProgressBar";
import { QuestionCard } from "@/components/QuestionCard";
import { useAssessment } from "@/context/AssessmentContext";
import { startAssessment, submitAnswer } from "@/lib/api";
import { ApiError } from "@/lib/types";

export default function AssessmentPage() {
  const router = useRouter();
  const {
    sessionId,
    currentQuestion,
    answers,
    maxQuestions,
    result,
    setSessionFromStart,
    setNextQuestion,
    appendAnswer,
    setResult,
  } = useAssessment();

  const [initLoading, setInitLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedValue, setSelectedValue] = useState<number | null>(null);

  useEffect(() => {
    if (result) {
      router.replace("/result");
      return;
    }
    if (sessionId && currentQuestion) return;

    let cancelled = false;
    setError(null);
    setInitLoading(true);
    startAssessment()
      .then((data) => {
        if (!cancelled) {
          setSessionFromStart(data.session_id, data.question);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          const msg =
            e instanceof ApiError
              ? e.message
              : e instanceof Error
                ? e.message
                : "Could not start assessment.";
          setError(msg);
        }
      })
      .finally(() => {
        if (!cancelled) setInitLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [result, sessionId, currentQuestion, router, setSessionFromStart]);

  async function handleSelect(answer: number) {
    if (!sessionId || !currentQuestion || submitLoading) return;
    setError(null);
    setSelectedValue(answer);
    setSubmitLoading(true);
    try {
      const res = await submitAnswer(sessionId, answer);
      appendAnswer(currentQuestion.id, answer);

      if (res.result) {
        setResult(res.result);
        router.push("/result");
        return;
      }

      if (res.question) {
        setNextQuestion(res.question);
        setSelectedValue(null);
      } else {
        setError("Unexpected response: no question or result.");
      }
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? e.message
          : e instanceof Error
            ? e.message
            : "Request failed.";
      setError(msg);
    } finally {
      setSubmitLoading(false);
    }
  }

  const answeredCount = answers.length;
  const progressDenominator = maxQuestions;

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-10 sm:py-16">
      <div className="mx-auto flex max-w-[500px] flex-col items-center gap-6">
        <ProgressBar value={answeredCount} max={progressDenominator} />

        {error && (
          <p
            className="w-full rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-center text-sm text-amber-900"
            role="alert"
          >
            {error}
          </p>
        )}

        {initLoading && !currentQuestion ? (
          <LoadingSpinner label="Preparing your first question…" />
        ) : currentQuestion && submitLoading ? (
          <LoadingSpinner label="Analyzing your response..." />
        ) : currentQuestion ? (
          <QuestionCard
            questionKey={currentQuestion.id}
            questionText={currentQuestion.text}
            loading={submitLoading}
            selectedValue={selectedValue}
            onSelect={handleSelect}
          />
        ) : null}
      </div>
    </main>
  );
}
