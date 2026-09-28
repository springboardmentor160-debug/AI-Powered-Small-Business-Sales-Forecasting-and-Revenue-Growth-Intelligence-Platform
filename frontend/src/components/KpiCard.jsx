export default function KpiCard({ label, value, detail, accent }) {
  return (
    <article className={`kpi-card ${accent ? `kpi-card--${accent}` : ""}`}>
      <div className="kpi-card__label">{label}</div>
      <div className="kpi-card__value">{value}</div>
      <div className="kpi-card__detail">{detail}</div>
    </article>
  );
}
