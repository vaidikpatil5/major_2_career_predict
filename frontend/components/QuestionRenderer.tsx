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

  const scaleColors = {
    1: { bg: "bg-rose-950/20", border: "border-rose-800/40", text: "text-rose-400", active: "bg-rose-500 text-white border-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.6)]" },
    2: { bg: "bg-orange-950/20", border: "border-orange-900/40", text: "text-orange-400", active: "bg-orange-500 text-white border-orange-500 shadow-[0_0_15px_rgba(249,115,22,0.6)]" },
    3: { bg: "bg-slate-900/40", border: "border-slate-800", text: "text-slate-400", active: "bg-slate-500 text-white border-slate-500 shadow-[0_0_15px_rgba(100,116,139,0.6)]" },
    4: { bg: "bg-emerald-950/20", border: "border-emerald-900/40", text: "text-emerald-400", active: "bg-emerald-500 text-white border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.6)]" },
    5: { bg: "bg-cyan-950/20", border: "border-cyan-900/40", text: "text-cyan-400", active: "bg-cyan-500 text-white border-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.6)]" },
  };

  const scaleEmojis = ["😡", "🙁", "😐", "🙂", "😄"];

  return (
    <Card
      className={`w-full max-w-[500px] transition-all duration-300 relative overflow-hidden shadow-2xl ${
        fade ? "animate-fade-in opacity-100 translate-y-0" : "opacity-0 translate-y-4"
      }`}
    >
      <div className="absolute top-0 right-0 p-1 px-2.5 rounded-bl-xl bg-slate-800/80 border-l border-b border-slate-700 text-[10px] uppercase font-bold tracking-wider text-slate-400">
        {kind} Choice
      </div>

      <p className="text-xl font-bold leading-relaxed text-slate-100 pr-12">
        {question.text}
      </p>
      <p className="mt-2 text-xs font-medium text-slate-400">{hint}</p>

      {kind === "scale" ? (
        <>
          <div className="mt-6 grid grid-cols-5 gap-2">
            {([1, 2, 3, 4, 5] as const).map((n) => {
              const active = selectedAnswer === n;
              const col = scaleColors[n];
              return (
                <Button
                  key={n}
                  variant="secondary"
                  disabled={disabled}
                  onClick={() => onAnswer(n)}
                  className={`flex min-h-[72px] flex-col justify-between py-2.5 text-center text-xs transition-all duration-150 ${
                    active ? col.active : `${col.bg} ${col.border} ${col.text} hover:scale-105`
                  }`}
                  aria-label={`${n}, ${SCALE_LABELS[n]}`}
                  aria-pressed={active}
                >
                  <span className="text-xl">{scaleEmojis[n-1]}</span>
                  <span className={`text-base font-black ${active ? "text-white" : col.text}`}>{n}</span>
                  <span className="text-[9px] font-medium leading-none opacity-80">
                    {SCALE_LABELS[n]}
                  </span>
                </Button>
              );
            })}
          </div>
          <div className="mt-4 flex flex-wrap justify-between gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            <span>Strongly Disagree</span>
            <span>Strongly Agree</span>
          </div>
        </>
      ) : null}

      {kind === "binary" ? (
        <div className="mt-6 grid grid-cols-2 gap-4">
          {(
            [
              { value: "yes" as const, label: "Yes", activeClass: "border-emerald-500 bg-emerald-950/20 text-emerald-400 ring-2 ring-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)]" },
              { value: "no" as const, label: "No", activeClass: "border-rose-500 bg-rose-950/20 text-rose-400 ring-2 ring-rose-400 shadow-[0_0_20px_rgba(244,63,94,0.3)]" },
            ] as const
          ).map(({ value, label, activeClass }) => {
            const active = selectedAnswer === value;
            return (
              <Button
                key={value}
                variant="secondary"
                disabled={disabled}
                onClick={() => onAnswer(value)}
                className={`min-h-[64px] py-4 text-lg font-bold transition-all duration-150 ${
                  active ? activeClass : "hover:border-slate-500 hover:scale-102"
                }`}
                aria-pressed={active}
              >
                {label === "Yes" ? "👍 " : "👎 "} {label}
              </Button>
            );
          })}
        </div>
      ) : null}

      {kind === "mcq" ? (
        <div className="mt-6 flex flex-col gap-3">
          {question.options && question.options.length > 0 ? (
            question.options.map((label, index) => {
              const active = selectedAnswer === index;
              const optionLetter = String.fromCharCode(65 + index); // A, B, C, D...
              return (
                <Button
                  key={`${question.id}-opt-${index}`}
                  variant="secondary"
                  disabled={disabled}
                  onClick={() => onAnswer(index)}
                  className={`min-h-[56px] justify-start px-4 py-3 text-left text-sm transition-all duration-150 ${
                    active
                      ? "border-cyan-500 bg-cyan-950/20 ring-2 ring-cyan-400 text-cyan-100 shadow-[0_0_15px_rgba(6,182,212,0.25)]"
                      : "hover:border-indigo-500/50 hover:bg-slate-800/70 hover:scale-[1.01]"
                  }`}
                  aria-label={`Option ${optionLetter}: ${label}`}
                  aria-pressed={active}
                >
                  <span className={`mr-4 flex h-6 w-6 items-center justify-center rounded-lg text-xs font-bold transition-colors ${
                    active ? "bg-cyan-500 text-slate-950" : "bg-slate-700/80 text-slate-300"
                  }`}>
                    {optionLetter}
                  </span>
                  <span className={`flex-1 font-medium ${active ? "text-cyan-50" : "text-slate-200"}`}>{label}</span>
                </Button>
              );
            })
          ) : (
            <p className="rounded-lg bg-amber-950/30 border border-amber-900/50 px-3 py-2 text-sm text-amber-400">
              This question has no options. Please refresh or contact support.
            </p>
          )}
        </div>
      ) : null}
    </Card>
  );
}

