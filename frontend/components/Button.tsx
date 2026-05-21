import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  variant?: "primary" | "secondary" | "ghost";
};

const base =
  "inline-flex items-center justify-center rounded-xl px-5 py-2.5 text-sm font-semibold transition-all duration-150 ease-out focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:pointer-events-none disabled:opacity-40";

const variants = {
  primary:
    "bg-gradient-to-r from-indigo-500 to-blue-500 text-white shadow-[0_0_15px_rgba(99,102,241,0.25)] hover:shadow-[0_0_20px_rgba(99,102,241,0.45)] hover:scale-[1.03] active:scale-[0.97] focus-visible:outline-indigo-500",
  secondary:
    "border border-slate-700 bg-slate-800/40 text-slate-200 backdrop-blur-md hover:border-indigo-400/80 hover:bg-indigo-950/20 hover:scale-[1.02] active:scale-[0.98] focus-visible:outline-indigo-500",
  ghost:
    "text-indigo-400 hover:bg-indigo-950/30 focus-visible:outline-indigo-500",
};

export function Button({
  children,
  variant = "primary",
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      type="button"
      className={`${base} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
