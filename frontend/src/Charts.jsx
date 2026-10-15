const W = 640, H = 220, P = { l: 56, r: 12, t: 12, b: 28 };
const fmt = (n) => (Math.abs(n) >= 1e6 ? (n / 1e6).toFixed(1) + "M" : Math.abs(n) >= 1e3 ? (n / 1e3).toFixed(0) + "k" : Math.round(n));

/** Revenue history line with an optional dashed forecast continuation. data/forecast: [{date, revenue}] */
export function TrendChart({ data = [], forecast = [] }) {
  const all = [...data, ...forecast];
  if (all.length < 2) return <p className="muted">Not enough data to draw a chart.</p>;
  const ys = all.map((d) => d.revenue), min = Math.min(...ys) * 0.95, max = Math.max(...ys) * 1.05;
  const x = (i) => P.l + (i / (all.length - 1)) * (W - P.l - P.r);
  const y = (v) => P.t + (1 - (v - min) / (max - min || 1)) * (H - P.t - P.b);
  const path = (arr, off) => arr.map((d, i) => `${i ? "L" : "M"}${x(i + off).toFixed(1)},${y(d.revenue).toFixed(1)}`).join(" ");
  const ticks = [min, (min + max) / 2, max];
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="chart" role="img" aria-label="Revenue trend">
      {ticks.map((t, i) => (<g key={i}><line x1={P.l} x2={W - P.r} y1={y(t)} y2={y(t)} className="grid" /><text x={P.l - 6} y={y(t) + 4} textAnchor="end" className="axis">{fmt(t)}</text></g>))}
      <path d={path(data, 0)} className="line" />
      {forecast.length > 0 && <path d={`M${x(data.length - 1)},${y(data[data.length - 1].revenue)} ` + path(forecast, data.length).replace(/^M/, "L")} className="line forecast" />}
      <text x={P.l} y={H - 8} className="axis">{all[0].date}</text>
      <text x={W - P.r} y={H - 8} textAnchor="end" className="axis">{all[all.length - 1].date}</text>
    </svg>
  );
}

/** Horizontal bars. items: [{label, value}] */
export function BarChart({ items = [], format = (v) => v }) {
  const max = Math.max(...items.map((i) => i.value), 1);
  return (
    <div className="bars">
      {items.map((i) => (
        <div className="bar-row" key={i.label}>
          <span className="bar-label">{i.label}</span>
          <div className="bar-track"><div className="bar-fill" style={{ width: `${(i.value / max) * 100}%` }} /></div>
          <span className="bar-value">{format(i.value)}</span>
        </div>
      ))}
    </div>
  );
}
