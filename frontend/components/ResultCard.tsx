import type { CareerMatch } from "@/lib/types";
import { Card } from "./Card";
import { Sparkles, Trophy } from "lucide-react";

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
        className={`relative overflow-hidden border border-indigo-500/50 bg-gradient-to-br from-slate-900 via-indigo-950/70 to-slate-950 p-8 shadow-[0_0_40px_rgba(99,102,241,0.25)] ring-1 ring-indigo-500/30 group ${className}`}
      >
        {/* Animated foil/shine overlay */}
        <div className="absolute inset-0 shine-effect pointer-events-none opacity-40 mix-blend-overlay" />
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 rounded-full bg-amber-500/10 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-amber-400 border border-amber-500/20">
            <Trophy size={12} className="text-amber-400" />
            <span>Legendary Fit</span>
          </div>
          <Sparkles size={16} className="text-indigo-400 animate-pulse" />
        </div>

        <h2 className="mt-4 text-3xl font-black tracking-tight text-white sm:text-4xl drop-shadow-[0_2px_10px_rgba(255,255,255,0.1)]">
          {match.role}
        </h2>
        
        <div className="mt-6 flex items-baseline gap-2">
          <span className="text-5xl font-black tracking-tight bg-gradient-to-r from-cyan-400 via-indigo-400 to-indigo-500 bg-clip-text text-transparent drop-shadow-[0_0_20px_rgba(6,182,212,0.3)] tabular-nums">
            {scorePercent(match.score)}
          </span>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Match Score</span>
        </div>
        <p className="mt-2 text-xs text-slate-400">Calculated via multi-trait adaptive vector alignment.</p>
      </Card>
    );
  }

  return (
    <Card className={`relative overflow-hidden border border-slate-800 bg-slate-900/60 p-5 hover:border-indigo-500/40 hover:shadow-[0_0_20px_rgba(99,102,241,0.1)] transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] ${className}`}>
      <div className="flex items-center justify-between gap-3">
        <div>
          <span className="text-[9px] font-bold uppercase tracking-widest text-indigo-400">Alternative Match</span>
          <h3 className="text-lg font-bold text-white mt-0.5">{match.role}</h3>
        </div>
        <span className="text-2xl font-black text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.2)] tabular-nums">
          {scorePercent(match.score)}
        </span>
      </div>
    </Card>
  );
}

