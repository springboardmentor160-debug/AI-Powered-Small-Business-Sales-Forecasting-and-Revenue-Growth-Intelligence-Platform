import { cn } from "../../lib/format";
import Spinner from "./Spinner";

const VARIANTS = {
  primary:
    "bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-sm shadow-indigo-600/30 hover:from-indigo-400 hover:to-violet-500 active:scale-[0.98]",
  secondary:
    "border border-slate-200 bg-white text-slate-700 shadow-sm hover:bg-slate-50 dark:border-white/10 dark:bg-white/5 dark:text-slate-200 dark:hover:bg-white/10",
  ghost:
    "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/10",
};

const SIZES = {
  sm: "h-8 gap-1.5 px-3 text-xs",
  md: "h-10 gap-2 px-4 text-sm",
  icon: "size-9 justify-center",
};

export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  icon: Icon,
  className,
  children,
  disabled,
  type = "button",
  ...props
}) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={cn(
        "inline-flex items-center justify-center rounded-lg font-semibold transition duration-150 motion-reduce:transition-none",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-950",
        "disabled:cursor-not-allowed disabled:opacity-60 disabled:active:scale-100",
        VARIANTS[variant],
        SIZES[size],
        className,
      )}
      {...props}
    >
      {loading ? <Spinner /> : Icon && <Icon aria-hidden="true" className="size-4" />}
      {children}
    </button>
  );
}
