import { cn, riskTone } from "../../lib/format";

const TONES = {
  neutral:
    "bg-slate-100 text-slate-700 ring-slate-200 dark:bg-white/5 dark:text-slate-300 dark:ring-white/10",
  brand:
    "bg-indigo-50 text-indigo-700 ring-indigo-200 dark:bg-indigo-500/10 dark:text-indigo-300 dark:ring-indigo-400/20",
  success:
    "bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:ring-emerald-400/20",
  warning:
    "bg-amber-50 text-amber-800 ring-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-400/20",
  danger:
    "bg-rose-50 text-rose-700 ring-rose-200 dark:bg-rose-500/10 dark:text-rose-300 dark:ring-rose-400/20",
};

const DOTS = {
  neutral: "bg-slate-400",
  brand: "bg-indigo-500",
  success: "bg-emerald-500",
  warning: "bg-amber-500",
  danger: "bg-rose-500",
};

export default function Badge({
  tone = "neutral",
  dot = false,
  icon: Icon,
  className,
  children,
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 whitespace-nowrap rounded-md px-2 py-0.5 text-xs font-semibold capitalize ring-1 ring-inset",
        TONES[tone],
        className,
      )}
    >
      {dot && (
        <span aria-hidden="true" className={cn("size-1.5 rounded-full", DOTS[tone])} />
      )}
      {Icon && <Icon aria-hidden="true" className="size-3.5" />}
      {children}
    </span>
  );
}

const RISK_TO_TONE = {
  high: "danger",
  medium: "warning",
  low: "success",
  neutral: "neutral",
};

/** High / Medium / Low badge. Accepts "High Risk", "high", "Medium", etc. */
export function RiskBadge({ level, children }) {
  return (
    <Badge tone={RISK_TO_TONE[riskTone(level)]} dot>
      {children ?? level}
    </Badge>
  );
}
