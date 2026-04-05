import type { CareerMatch } from "@/lib/types";
import { Card } from "./Card";

type ResultCardProps = {
  match: CareerMatch;
  highlight?: boolean;
  className?: string;
};

function scorePercent(score: number): string {
  return `${Math.round(score * 100)}%`;
}

export function ResultCard({
  match,
  highlight = false,
  className = "",
}: ResultCardProps) {
  if (highlight) {
    return (
      <Card
        className={`relative overflow-hidden border-2 border-indigo-200 bg-gradient-to-br from-white via-indigo-50/40 to-blue-50/60 shadow-lg ring-1 ring-indigo-100 ${className}`}
      >
        <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-indigo-500 via-blue-500 to-cyan-400" />
        <p className="text-sm font-semibold uppercase tracking-wide text-indigo-600">
          Best career match
        </p>
        <h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          {match.role}
        </h2>
        <p className="mt-4 text-3xl font-semibold text-indigo-700 tabular-nums">
          {scorePercent(match.score)}
        </p>
        <p className="mt-1 text-sm text-slate-500">Confidence score</p>
      </Card>
    );
  }

  return (
    <Card className={`p-4 shadow-sm ${className}`}>
      <h3 className="font-semibold text-slate-800">{match.role}</h3>
      <p className="mt-1 text-sm font-medium text-indigo-600 tabular-nums">
        {scorePercent(match.score)}
      </p>
    </Card>
  );
}
