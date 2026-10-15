import { formatNumber, formatPercent } from "../../lib/format";
import Tooltip from "../ui/Tooltip";

/** Horizontal bars for ranked categories. items: [{ label, value }] */
export default function BarList({ items, unit = "customers" }) {
  const max = Math.max(1, ...items.map((i) => i.value));
  const total = items.reduce((sum, i) => sum + i.value, 0);

  return (
    <ul className="space-y-3.5">
      {items.map((item) => {
        const share = total > 0 ? (item.value / total) * 100 : 0;
        return (
          <li key={item.label}>
            <Tooltip
              side="top"
              align="start"
              className="flex w-full"
              content={`${formatNumber(item.value)} ${unit} · ${formatPercent(share)} of total`}
            >
              <div className="w-full">
                <div className="mb-1.5 flex items-baseline justify-between gap-3 text-sm">
                  <span className="truncate font-medium text-slate-700 dark:text-slate-200">
                    {item.label}
                  </span>
                  <span className="tabular-nums font-semibold text-slate-900 dark:text-white">
                    {formatNumber(item.value)}
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-white/10">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500"
                    style={{ width: `${Math.max((item.value / max) * 100, 2)}%` }}
                  />
                </div>
              </div>
            </Tooltip>
          </li>
        );
      })}
    </ul>
  );
}
