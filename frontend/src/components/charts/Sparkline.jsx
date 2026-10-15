import { useId } from "react";
import { cn } from "../../lib/format";

/** Tiny trend line for stat cards. `data` is a plain array of numbers. */
export default function Sparkline({ data, className, color = "#6366f1" }) {
  const gradientId = useId().replace(/:/g, "");
  if (!data || data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const span = max - min || 1;
  const points = data.map((v, i) => [
    (i / (data.length - 1)) * 100,
    36 - ((v - min) / span) * 32,
  ]);
  const line = points.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(2)},${y.toFixed(2)}`).join(" ");
  const area = `${line} L100,40 L0,40 Z`;

  return (
    <svg
      viewBox="0 0 100 40"
      preserveAspectRatio="none"
      aria-hidden="true"
      className={cn("h-10 w-24", className)}
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.28" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill={`url(#${gradientId})`} />
      <path
        d={line}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}
