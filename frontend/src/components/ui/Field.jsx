import { forwardRef } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "../../lib/format";

export function Field({ label, htmlFor, hint, error, children, className }) {
  return (
    <div className={cn("space-y-1.5", className)}>
      {label && (
        <label
          htmlFor={htmlFor}
          className="block text-sm font-medium text-slate-700 dark:text-slate-200"
        >
          {label}
        </label>
      )}
      {children}
      {error ? (
        <p id={`${htmlFor}-error`} className="text-xs font-medium text-rose-600 dark:text-rose-300">
          {error}
        </p>
      ) : (
        hint && (
          <p id={`${htmlFor}-hint`} className="text-xs text-slate-500 dark:text-slate-400">
            {hint}
          </p>
        )
      )}
    </div>
  );
}

const CONTROL =
  "w-full rounded-lg border bg-white text-sm text-slate-900 shadow-sm transition placeholder:text-slate-400 focus:outline-none focus:ring-4 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-slate-950/60 dark:text-slate-100 dark:placeholder:text-slate-500";

function stateClasses(invalid) {
  return invalid
    ? "border-rose-400 focus:border-rose-500 focus:ring-rose-500/15 dark:border-rose-400/50"
    : "border-slate-300 focus:border-indigo-500 focus:ring-indigo-500/15 dark:border-white/10 dark:focus:border-indigo-400";
}

export const Input = forwardRef(function Input(
  { icon: Icon, trailing, invalid = false, className, ...props },
  ref,
) {
  return (
    <div className="relative">
      {Icon && (
        <Icon
          aria-hidden="true"
          className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400"
        />
      )}
      <input
        ref={ref}
        aria-invalid={invalid || undefined}
        className={cn(
          CONTROL,
          "h-10 py-2",
          Icon ? "pl-10" : "pl-3",
          trailing ? "pr-11" : "pr-3",
          stateClasses(invalid),
          className,
        )}
        {...props}
      />
      {trailing && <div className="absolute right-1.5 top-1/2 -translate-y-1/2">{trailing}</div>}
    </div>
  );
});

export function Select({ className, children, ...props }) {
  return (
    <div className="relative">
      <select
        className={cn(
          CONTROL,
          "h-9 cursor-pointer appearance-none py-1.5 pl-3 pr-8",
          stateClasses(false),
          className,
        )}
        {...props}
      >
        {children}
      </select>
      <ChevronDown
        aria-hidden="true"
        className="pointer-events-none absolute right-2.5 top-1/2 size-4 -translate-y-1/2 text-slate-400"
      />
    </div>
  );
}
