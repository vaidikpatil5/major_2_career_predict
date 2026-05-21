"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { ProgressBar } from "@/components/ProgressBar";
import { QuestionRenderer } from "@/components/QuestionRenderer";
import { useAssessment } from "@/context/AssessmentContext";
import { startAssessment, submitAnswer } from "@/lib/api";
import { ApiError, type AnswerPayload } from "@/lib/types";

export default function AssessmentPage() {
  const router = useRouter();
  const {
    sessionId,
    currentQuestion,
    answers,
    maxQuestions,
    minQuestions,
    result,
    setSessionFromStart,
    setNextQuestion,
    appendAnswer,
    setResult,
  } = useAssessment();

  const [initLoading, setInitLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<AnswerPayload | null>(
    null
  );

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

  async function handleAnswer(answer: AnswerPayload) {
    if (!sessionId || !currentQuestion || submitLoading) return;
    setError(null);
    setSelectedAnswer(answer);
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
        setSelectedAnswer(null);
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
    <main className="relative min-h-screen px-4 py-12 sm:py-20 flex flex-col justify-center items-center overflow-hidden">
      {/* Background ambient light */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-[20%] left-[10%] w-72 h-72 rounded-full bg-indigo-500/5 blur-[100px] animate-float" />
        <div className="absolute bottom-[20%] right-[10%] w-80 h-80 rounded-full bg-cyan-500/5 blur-[100px] animate-float" style={{ animationDelay: "-3s" }} />
      </div>

      <div className="mx-auto flex w-full max-w-[500px] flex-col items-center gap-8">
        <ProgressBar value={answeredCount} max={maxQuestions} min={minQuestions} />

        {error && (
          <p
            className="w-full rounded-xl border border-red-900/50 bg-red-950/30 px-4 py-3 text-center text-sm font-semibold text-red-400 shadow-[0_0_15px_rgba(239,68,68,0.1)]"
            role="alert"
          >
            ⚠️ {error}
          </p>
        )}

        {initLoading && !currentQuestion ? (
          <div className="flex flex-col items-center gap-4 py-12">
            <LoadingSpinner label="Booting adaptive scan engine…" />
          </div>
        ) : currentQuestion && submitLoading ? (
          <div className="flex flex-col items-center gap-4 py-12">
            <LoadingSpinner label="Analyzing response vectors..." />
          </div>
        ) : currentQuestion ? (
          <QuestionRenderer
            question={currentQuestion}
            loading={submitLoading}
            selectedAnswer={selectedAnswer}
            onAnswer={handleAnswer}
          />
        ) : null}
      </div>
    </main>
  );
}
