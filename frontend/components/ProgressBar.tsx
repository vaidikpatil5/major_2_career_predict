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
  
  // Gamified Levels
  const currentLvl = Math.max(1, Math.min(3, Math.ceil((value + 1) / 3)));
  const levelNames = ["Initiate Scan", "Scenario Trial", "Final Tuning"];
  const currentLvlName = levelNames[currentLvl - 1];

  return (
    <div className={`w-full ${className}`}>
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="flex h-5 items-center justify-center rounded bg-indigo-500 px-1.5 text-[10px] font-bold uppercase tracking-wider text-white shadow-[0_0_10px_rgba(99,102,241,0.5)]">
            Lvl {currentLvl}
          </span>
          <span className="text-xs font-semibold text-slate-300">
            {currentLvlName}
          </span>
        </div>
        <span className="text-xs font-medium text-slate-400 tabular-nums">
          Quest {value} of {rangeLabel} ({Math.round(pct)}% XP)
        </span>
      </div>
      
      <div className="relative h-3 w-full rounded-full border border-slate-700 bg-slate-950 p-[2px] shadow-[inset_0_2px_4px_rgba(0,0,0,0.6)]">
        <div
          className="relative h-full rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400 transition-[width] duration-500 ease-out shadow-[0_0_12px_rgba(34,211,238,0.4)]"
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={Math.round(pct)}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          {pct > 0 && (
            <div className="absolute right-0 top-1/2 h-3 w-3 -translate-y-1/2 rounded-full bg-white shadow-[0_0_10px_#fff,0_0_20px_#22d3ee] animate-pulse-glow" />
          )}
        </div>
      </div>
    </div>
  );
}

