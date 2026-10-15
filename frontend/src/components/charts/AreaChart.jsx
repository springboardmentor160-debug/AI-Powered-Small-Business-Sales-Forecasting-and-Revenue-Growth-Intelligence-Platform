import { useId, useMemo, useState } from "react";
import { useElementWidth } from "../../hooks/useElementWidth";
import { cn, formatCompact } from "../../lib/format";

const PAD = { top: 16, right: 16, bottom: 28, left: 44 };

function niceMax(max) {
  if (max <= 0) return 1;
  const exp = 10 ** Math.floor(Math.log10(max));
  const f = max / exp;
  const nice = f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10;
  return nice * exp;
}

/**
 * data: [{ x: number (timestamp or index), label: string, value: number }]
 * Hover (or arrow keys when focused) shows the exact value for each point.
 */
export default function AreaChart({
  data,
  height = 260,
  formatValue = (v) => String(v),
  formatLabel = (l) => l,
  valueLabel = "Value",
  className,
}) {
  const [ref, measured] = useElementWidth();
  const width = measured || 640;
  const gradientId = useId().replace(/:/g, "");
  const [activeIndex, setActiveIndex] = useState(null);

  const innerW = Math.max(width - PAD.left - PAD.right, 1);
  const innerH = height - PAD.top - PAD.bottom;

  const geo = useMemo(() => {
    if (!data.length) return null;
    const maxV = niceMax(Math.max(...data.map((d) => d.value)));
    const xs = data.map((d) => d.x);
    const minX = Math.min(...xs);
    const spanX = Math.max(...xs) - minX || 1;
    const px = (x) => (data.length === 1 ? innerW / 2 : ((x - minX) / spanX) * innerW);
    const py = (v) => innerH - (v / maxV) * innerH;

    const pts = data.map((d) => ({ ...d, cx: PAD.left + px(d.x), cy: PAD.top + py(d.value) }));
    const line = pts.map((p, i) => `${i ? "L" : "M"}${p.cx.toFixed(1)},${p.cy.toFixed(1)}`).join(" ");
    const baseline = PAD.top + innerH;
    const area = `${line} L${pts[pts.length - 1].cx.toFixed(1)},${baseline} L${pts[0].cx.toFixed(1)},${baseline} Z`;
    const ticks = [0, 1, 2, 3, 4].map((i) => ({
      value: (maxV / 4) * i,
      y: PAD.top + py((maxV / 4) * i),
    }));

    const labelCount = Math.max(2, Math.min(6, Math.floor(innerW / 110)));
    const labelIdx = [
      ...new Set(
        Array.from({ length: labelCount }, (_, i) =>
          Math.round((i / (labelCount - 1)) * (pts.length - 1)),
        ),
      ),
    ];
    return { pts, line, area, ticks, labelIdx, baseline };
  }, [data, innerW, innerH]);

  if (!geo) return null;
  const active = activeIndex === null ? null : geo.pts[activeIndex];

  function onPointerMove(event) {
    const rect = ref.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    let best = 0;
    let bestDist = Infinity;
    geo.pts.forEach((p, i) => {
      const dist = Math.abs(p.cx - x);
      if (dist < bestDist) {
        best = i;
        bestDist = dist;
      }
    });
    setActiveIndex(best);
  }

  function onKeyDown(event) {
    const last = geo.pts.length - 1;
    if (event.key === "ArrowRight") {
      event.preventDefault();
      setActiveIndex((i) => (i === null ? 0 : Math.min(i + 1, last)));
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      setActiveIndex((i) => (i === null ? last : Math.max(i - 1, 0)));
    } else if (event.key === "Escape") {
      setActiveIndex(null);
    }
  }

  const first = geo.pts[0];
  const last = geo.pts[geo.pts.length - 1];

  return (
    <div
      ref={ref}
      tabIndex={0}
      role="img"
      aria-label={`${valueLabel} from ${formatLabel(first.label)} to ${formatLabel(last.label)}. Use left and right arrow keys to read individual values.`}
      onPointerMove={onPointerMove}
      onPointerLeave={() => setActiveIndex(null)}
      onKeyDown={onKeyDown}
      onBlur={() => setActiveIndex(null)}
      className={cn(
        "relative select-none rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500",
        className,
      )}
      style={{ height }}
    >
      <svg width={width} height={height} className="block overflow-visible">
        <defs>
          <linearGradient id={`${gradientId}-fill`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#6366f1" stopOpacity="0.28" />
            <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
          </linearGradient>
          <linearGradient id={`${gradientId}-line`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>

        {geo.ticks.map((tick) => (
          <g key={tick.value}>
            <line
              x1={PAD.left}
              x2={width - PAD.right}
              y1={tick.y}
              y2={tick.y}
              strokeDasharray="3 5"
              className="stroke-slate-200 dark:stroke-white/10"
            />
            <text
              x={PAD.left - 8}
              y={tick.y}
              textAnchor="end"
              dominantBaseline="middle"
              fontSize="11"
              className="fill-slate-400 dark:fill-slate-500"
            >
              {formatCompact(tick.value)}
            </text>
          </g>
        ))}

        <path d={geo.area} fill={`url(#${gradientId}-fill)`} />
        <path
          d={geo.line}
          fill="none"
          stroke={`url(#${gradientId}-line)`}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {geo.labelIdx.map((i, n) => (
          <text
            key={i}
            x={geo.pts[i].cx}
            y={geo.baseline + 18}
            fontSize="11"
            textAnchor={n === 0 ? "start" : n === geo.labelIdx.length - 1 ? "end" : "middle"}
            className="fill-slate-400 dark:fill-slate-500"
          >
            {formatLabel(geo.pts[i].label)}
          </text>
        ))}

        {active && (
          <g>
            <line
              x1={active.cx}
              x2={active.cx}
              y1={PAD.top}
              y2={geo.baseline}
              strokeDasharray="3 3"
              className="stroke-indigo-400/70"
            />
            <circle
              cx={active.cx}
              cy={active.cy}
              r="5"
              strokeWidth="2.5"
              stroke="#6366f1"
              className="fill-white dark:fill-slate-900"
            />
          </g>
        )}
      </svg>

      {active && (
        <div
          role="status"
          className="pointer-events-none absolute z-20 -translate-x-1/2 rounded-lg bg-slate-900 px-3 py-2 text-xs text-white shadow-pop ring-1 ring-white/10 dark:bg-slate-100 dark:text-slate-900 dark:ring-black/5"
          style={{
            left: Math.min(Math.max(active.cx, 72), width - 72),
            top: Math.max(active.cy - 62, 0),
          }}
        >
          <p className="font-medium opacity-70">{formatLabel(active.label, true)}</p>
          <p className="mt-0.5 text-sm font-semibold tabular-nums">
            {formatValue(active.value)} <span className="font-normal opacity-70">{valueLabel.toLowerCase()}</span>
          </p>
        </div>
      )}
    </div>
  );
}
