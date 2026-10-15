import { Info, TrendingDown, TrendingUp } from "lucide-react";
import { cn, formatPercent } from "../lib/format";
import Sparkline from "./charts/Sparkline";
import { Card } from "./ui/Card";
import Skeleton from "./ui/Skeleton";
import Tooltip from "./ui/Tooltip";

const TONES = {
  indigo: { tile: "bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-300", line: "#6366f1" },
  sky: { tile: "bg-sky-50 text-sky-600 dark:bg-sky-500/10 dark:text-sky-300", line: "#0ea5e9" },
  amber: { tile: "bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-300", line: "#f59e0b" },
  emerald: { tile: "bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-300", line: "#10b981" },
};

/**
 * trend: { value: number } (percent change); `trendLabel` explains the comparison.
 * `invertTrend` flips the colour for metrics where "up" is bad.
 */
export default function StatCard({
  label,
  value,
  icon: Icon,
  tone = "indigo",
  trend,
  trendLabel,
  invertTrend = false,
  hint,
  info,
  series,
  loading = false,
  className,
}) {
  const t = TONES[tone];

  if (loading) {
    return (
      <Card className={cn("p-5", className)} aria-busy="true">
        <div className="flex items-center gap-3">
          <Skeleton className="size-10 rounded-xl" />
          <Skeleton className="h-4 w-28" />
        </div>
        <Skeleton className="mt-5 h-8 w-32" />
        <Skeleton className="mt-3 h-4 w-40" />
      </Card>
    );
  }

  const up = trend && trend.value >= 0;
  const good = invertTrend ? !up : up;

  return (
    <Card className={cn("p-5", className)}>
      <div className="flex items-center gap-3">
        <span className={cn("flex size-10 shrink-0 items-center justify-center rounded-xl", t.tile)}>
          <Icon aria-hidden="true" className="size-5" />
        </span>
        <p className="flex-1 text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
        {info && (
          <Tooltip content={info} align="end">
            <button
              type="button"
              aria-label={`About ${label}`}
              className="rounded-full p-1 text-slate-400 transition-colors hover:text-slate-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 dark:hover:text-slate-200"
            >
              <Info aria-hidden="true" className="size-4" />
            </button>
          </Tooltip>
        )}
      </div>

      <div className="mt-4 flex items-end justify-between gap-3">
        <p className="text-3xl font-bold tabular-nums tracking-tight text-slate-900 dark:text-white">
          {value}
        </p>
        <Sparkline data={series} color={t.line} />
      </div>

      {(trend || hint) && (
        <div className="mt-3 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs">
          {trend && (
            <span
              className={cn(
                "inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 font-semibold",
                good
                  ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300"
                  : "bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300",
              )}
            >
              {up ? (
                <TrendingUp aria-hidden="true" className="size-3.5" />
              ) : (
                <TrendingDown aria-hidden="true" className="size-3.5" />
              )}
              {up ? "+" : ""}
              {formatPercent(trend.value)}
            </span>
          )}
          {(trendLabel || hint) && (
            <span className="text-slate-500 dark:text-slate-400">{trend ? trendLabel : hint}</span>
          )}
        </div>
      )}
    </Card>
  );
}
