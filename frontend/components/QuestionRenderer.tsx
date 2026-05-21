"use client";

import { useEffect, useMemo, useState } from "react";
import type { AnswerPayload, Question, QuestionType } from "@/lib/types";
import { Button } from "./Button";
import { Card } from "./Card";

const SCALE_LABELS: Record<number, string> = {
  1: "Strongly Disagree",
  2: "Disagree",
  3: "Neutral",
  4: "Agree",
  5: "Strongly Agree",
};

function resolveQuestionType(question: Question): QuestionType {
  return question.type ?? "scale";
}

type QuestionRendererProps = {
  question: Question;
  loading: boolean;
  selectedAnswer: AnswerPayload | null;
  onAnswer: (answer: AnswerPayload) => void;
};

export function QuestionRenderer({
  question,
  loading,
  selectedAnswer,
  onAnswer,
}: QuestionRendererProps) {
  const kind = resolveQuestionType(question);
  const [fade, setFade] = useState(true);
  const disabled = loading;

  useEffect(() => {
    setFade(false);
    const id = requestAnimationFrame(() => setFade(true));
    return () => cancelAnimationFrame(id);
  }, [question.id]);

  const hint = useMemo(() => {
    switch (kind) {
      case "scale":
        return "Rate how much you agree with this statement (1–5).";
      case "binary":
        return "Choose the response that fits you best.";
      case "mcq":
        return "Select one option.";
    }
  }, [kind]);

  return (
    <Card
      className={`w-full max-w-[500px] transition-opacity duration-300 ${
        fade ? "animate-fade-in opacity-100" : "opacity-0"
      }`}
    >
      <p className="text-lg font-medium leading-relaxed text-slate-800">
        {question.text}
      </p>
      <p className="mt-2 text-xs text-slate-500">{hint}</p>

      {kind === "scale" ? (
        <>
          <div className="mt-6 grid grid-cols-1 gap-2 sm:grid-cols-5 sm:gap-2">
            {([1, 2, 3, 4, 5] as const).map((n) => (
              <Button
                key={n}
                variant="secondary"
                disabled={disabled}
                onClick={() => onAnswer(n)}
                className={`flex min-h-[44px] flex-col gap-0.5 py-3 text-center text-xs sm:min-h-[72px] ${
                  selectedAnswer === n
                    ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-400"
                    : ""
                }`}
                aria-label={`${n}, ${SCALE_LABELS[n]}`}
                aria-pressed={selectedAnswer === n}
              >
                <span className="text-base font-bold text-indigo-600">{n}</span>
                <span className="hidden font-normal text-slate-600 sm:inline">
                  {SCALE_LABELS[n]}
                </span>
              </Button>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap justify-between gap-2 text-[10px] text-slate-400 sm:text-xs">
            <span>1 — Strongly Disagree</span>
            <span>5 — Strongly Agree</span>
          </div>
        </>
      ) : null}

      {kind === "binary" ? (
        <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
          {(
            [
              { value: "yes" as const, label: "Yes" },
              { value: "no" as const, label: "No" },
            ] as const
          ).map(({ value, label }) => (
            <Button
              key={value}
              variant="secondary"
              disabled={disabled}
              onClick={() => onAnswer(value)}
              className={`min-h-[52px] py-3 text-base transition-transform duration-150 hover:scale-[1.02] active:scale-[0.98] ${
                selectedAnswer === value
                  ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-400"
                  : ""
              }`}
              aria-pressed={selectedAnswer === value}
            >
              {label}
            </Button>
          ))}
        </div>
      ) : null}

      {kind === "mcq" ? (
        <div className="mt-6 flex flex-col gap-2">
          {question.options && question.options.length > 0 ? (
            question.options.map((label, index) => (
              <Button
                key={`${question.id}-opt-${index}`}
                variant="secondary"
                disabled={disabled}
                onClick={() => onAnswer(index)}
                className={`min-h-[48px] justify-start px-4 py-3 text-left text-sm transition-transform duration-150 hover:scale-[1.01] active:scale-[0.99] ${
                  selectedAnswer === index
                    ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-400"
                    : ""
                }`}
                aria-label={`Option ${index + 1}: ${label}`}
                aria-pressed={selectedAnswer === index}
              >
                <span className="mr-3 font-semibold tabular-nums text-indigo-600">
                  {index + 1}.
                </span>
                <span className="text-slate-800">{label}</span>
              </Button>
            ))
          ) : (
            <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900">
              This question has no options. Please refresh or contact support.
            </p>
          )}
        </div>
      ) : null}
    </Card>
  );
}
