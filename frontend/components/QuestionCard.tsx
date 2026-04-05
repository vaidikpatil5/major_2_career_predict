"use client";

import { useEffect, useState } from "react";
import { Button } from "./Button";
import { Card } from "./Card";

const LABELS: Record<number, string> = {
  1: "Strongly Disagree",
  2: "Disagree",
  3: "Neutral",
  4: "Agree",
  5: "Strongly Agree",
};

type QuestionCardProps = {
  questionText: string;
  questionKey: string;
  loading: boolean;
  selectedValue?: number | null;
  onSelect: (value: number) => void;
};

export function QuestionCard({
  questionText,
  questionKey,
  loading,
  selectedValue,
  onSelect,
}: QuestionCardProps) {
  const [fade, setFade] = useState(true);

  useEffect(() => {
    setFade(false);
    const t = requestAnimationFrame(() => setFade(true));
    return () => cancelAnimationFrame(t);
  }, [questionKey]);

  return (
    <Card
      className={`max-w-[500px] w-full transition-opacity duration-300 ${
        fade ? "opacity-100 animate-fade-in" : "opacity-0"
      }`}
    >
      <p className="text-lg font-medium leading-relaxed text-slate-800">
        {questionText}
      </p>
      <p className="mt-2 text-xs text-slate-500">
        Rate how much you agree with this statement (1–5).
      </p>
      <div className="mt-6 grid grid-cols-1 gap-2 sm:grid-cols-5 sm:gap-2">
        {([1, 2, 3, 4, 5] as const).map((n) => (
          <Button
            key={n}
            variant="secondary"
            disabled={loading}
            onClick={() => onSelect(n)}
            className={`flex min-h-[44px] flex-col gap-0.5 py-3 text-center text-xs sm:min-h-[72px] ${
              selectedValue === n
                ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-400"
                : ""
            }`}
            aria-label={`${n}, ${LABELS[n]}`}
            aria-pressed={selectedValue === n}
          >
            <span className="text-base font-bold text-indigo-600">{n}</span>
            <span className="hidden font-normal text-slate-600 sm:inline">
              {LABELS[n]}
            </span>
          </Button>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap justify-between gap-2 text-[10px] text-slate-400 sm:text-xs">
        <span>1 — Strongly Disagree</span>
        <span>5 — Strongly Agree</span>
      </div>
    </Card>
  );
}
