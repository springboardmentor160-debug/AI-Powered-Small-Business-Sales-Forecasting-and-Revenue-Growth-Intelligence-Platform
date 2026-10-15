import { useState } from "react";
import { cn, formatNumber, formatPercent } from "../../lib/format";

const RADIUS = 52;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

/**
 * segments: [{ key, label, value, color }]
 * Hovering a segment or legend row focuses it and swaps the centre label.
 */
export default function Donut({ segments, centerLabel = "Total", className }) {
  const [activeKey, setActiveKey] = useState(null);
  const total = segments.reduce((sum, s) => sum + s.value, 0);
  const visibleCount = segments.filter((s) => s.value > 0).length;
  const gap = visibleCount > 1 ? 3 : 0;
  const active = segments.find((s) => s.key === activeKey);

  let offset = 0;
  const arcs = segments.map((segment) => {
    const length = total > 0 ? (segment.value / total) * CIRCUMFERENCE : 0;
    const arc = { ...segment, length, offset };
    offset += length;
    return arc;
  });

  return (
    <div className={cn("flex flex-col items-center gap-5 sm:flex-row", className)}>
      <div className="relative size-40 shrink-0">
        <svg viewBox="0 0 140 140" className="size-full -rotate-90" role="img" aria-label={`${centerLabel}: ${formatNumber(total)}`}>
          <circle
            cx="70"
            cy="70"
            r={RADIUS}
            fill="none"
            strokeWidth="14"
            className="stroke-slate-100 dark:stroke-white/10"
          />
          {arcs.map(
            (arc) =>
              arc.length > 0 && (
                <circle
                  key={arc.key}
                  cx="70"
                  cy="70"
                  r={RADIUS}
                  fill="none"
                  stroke={arc.color}
                  strokeWidth={activeKey === arc.key ? 17 : 14}
                  strokeDasharray={`${Math.max(arc.length - gap, 0.5)} ${CIRCUMFERENCE}`}
                  strokeDashoffset={-arc.offset}
                  opacity={activeKey && activeKey !== arc.key ? 0.35 : 1}
                  className="cursor-pointer transition-all duration-150 motion-reduce:transition-none"
                  onMouseEnter={() => setActiveKey(arc.key)}
                  onMouseLeave={() => setActiveKey(null)}
                />
              ),
          )}
        </svg>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-2xl font-bold tabular-nums tracking-tight text-slate-900 dark:text-white">
            {formatNumber(active ? active.value : total)}
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400">
            {active ? active.label : centerLabel}
          </span>
        </div>
      </div>

      <ul className="w-full min-w-0 flex-1 space-y-1.5">
        {segments.map((segment) => (
          <li key={segment.key}>
            <button
              type="button"
              onMouseEnter={() => setActiveKey(segment.key)}
              onMouseLeave={() => setActiveKey(null)}
              onFocus={() => setActiveKey(segment.key)}
              onBlur={() => setActiveKey(null)}
              className="flex w-full items-center gap-3 rounded-lg px-2.5 py-2 text-left text-sm transition-colors hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 dark:hover:bg-white/5"
            >
              <span
                aria-hidden="true"
                className="size-2.5 shrink-0 rounded-full"
                style={{ backgroundColor: segment.color }}
              />
              <span className="flex-1 font-medium text-slate-700 dark:text-slate-200">
                {segment.label}
              </span>
              <span className="tabular-nums font-semibold text-slate-900 dark:text-white">
                {formatNumber(segment.value)}
              </span>
              <span className="w-12 text-right text-xs tabular-nums text-slate-500 dark:text-slate-400">
                {total > 0 ? formatPercent((segment.value / total) * 100, 0) : "—"}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
