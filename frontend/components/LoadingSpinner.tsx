type LoadingSpinnerProps = {
  label?: string;
  className?: string;
};

export function LoadingSpinner({
  label = "Analyzing your response...",
  className = "",
}: LoadingSpinnerProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center gap-4 py-8 ${className}`}
      role="status"
      aria-live="polite"
    >
      <div className="h-10 w-10 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
      <p className="text-sm font-medium text-slate-600">{label}</p>
    </div>
  );
}
