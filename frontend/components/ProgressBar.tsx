"use client";

type ProgressBarProps = {
  value: number;
  max?: number;
  min?: number;
  className?: string;
};

export function ProgressBar({
  value,
  max = 100,
  min,
  className = "",
}: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const rangeLabel = min !== undefined ? `${min}–${max}` : `${max}`;

  return (
    <div className={`w-full ${className}`}>
      <div className="mb-1 flex justify-between text-xs font-medium text-slate-500">
        <span>Question {value} of {rangeLabel}</span>
        <span>{Math.round(pct)}%</span>
      </div>
      <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-blue-500 transition-[width] duration-500 ease-out"
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={Math.round(pct)}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}
