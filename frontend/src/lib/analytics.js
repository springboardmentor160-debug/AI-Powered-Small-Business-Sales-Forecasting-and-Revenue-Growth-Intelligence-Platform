function sum(list) {
  return list.reduce((total, d) => total + d.value, 0);
}

/** Units sold per date, sorted oldest to newest. */
export function buildUnitsSeries(rows) {
  const byDate = new Map();
  for (const row of rows ?? []) {
    if (!row?.date) continue;
    const x = Date.parse(row.date);
    if (Number.isNaN(x)) continue;
    const current = byDate.get(row.date);
    byDate.set(row.date, {
      x,
      label: row.date,
      value: (current?.value ?? 0) + Number(row.units_sold || 0),
    });
  }
  return [...byDate.values()].sort((a, b) => a.x - b.x);
}

/** % change between the earlier and the latest half of the series. */
export function computeTrend(series) {
  if (!series || series.length < 4) return null;
  const half = Math.floor(series.length / 2);
  const earlier = sum(series.slice(0, half));
  const latest = sum(series.slice(series.length - half));
  if (earlier === 0) return null;
  return { value: ((latest - earlier) / earlier) * 100 };
}
