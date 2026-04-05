import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  variant?: "primary" | "secondary" | "ghost";
};

const base =
  "inline-flex items-center justify-center rounded-xl px-5 py-2.5 text-sm font-semibold transition-all duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:pointer-events-none disabled:opacity-50";

const variants = {
  primary:
    "bg-indigo-600 text-white shadow-md hover:bg-indigo-700 hover:shadow-lg active:scale-[0.98] focus-visible:outline-indigo-600",
  secondary:
    "border border-slate-200 bg-white text-slate-800 shadow-sm hover:border-indigo-200 hover:bg-indigo-50 focus-visible:outline-indigo-500",
  ghost:
    "text-indigo-700 hover:bg-indigo-50 focus-visible:outline-indigo-500",
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
