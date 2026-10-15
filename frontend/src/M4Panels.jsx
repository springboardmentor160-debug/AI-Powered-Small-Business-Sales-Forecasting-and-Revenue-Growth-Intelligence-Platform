import { useEffect, useState } from "react";
import { api, money, rangeLabel, useFetch } from "./api";
import { BarChart } from "./Charts";
import { Panel } from "./M3Panels";

const pct = (v, d = 1) => (v == null ? "-" : `${Number(v).toFixed(d)}%`);
const num = (v, d = 3) => (v == null ? "-" : Number(v).toFixed(d));

/** Sales analytics: revenue by category + top products (database aggregates). */
export function SalesBreakdown({ token, range = "all" }) {
  const cat = useFetch(`/sales/by-category?range=${range}`, token);
  const top = useFetch(`/sales/top-products?limit=5&range=${range}`, token);
  const st = cat.error ? cat : top.error ? top : null;
  return (
    <Panel title={`Sales analytics · ${rangeLabel(range)}`} state={st}>
      {(cat.loading || top.loading) && <p className="muted">Loading…</p>}
      {cat.data && (cat.data.length ? <>
        <h3>Revenue by category</h3>
        <BarChart items={cat.data.map((c) => ({ label: c.category, value: c.revenue }))} format={(v) => money(v)} />
      </> : <p className="muted">No sales data loaded yet - run <code>python load_data.py</code>.</p>)}
      {top.data && top.data.length > 0 && <>
        <h3>Top 5 products</h3>
        <div className="scroll"><table><thead><tr><th>Product</th><th>Category</th><th>Units</th><th>Revenue</th></tr></thead>
          <tbody>{top.data.map((p) => <tr key={p.product_id}><td>{p.product_id}</td><td>{p.category}</td><td>{p.units_sold.toLocaleString()}</td><td>{money(p.revenue)}</td></tr>)}</tbody></table></div>
      </>}
    </Panel>
  );
}

/** Inventory intelligence: stock status mix, days of cover and suggested reorder quantities. */
export function InventoryIntel({ token }) {
  const st = useFetch("/inventory/summary?limit=6", token);
  const d = st.data;
  return (
    <Panel title="Inventory intelligence" state={st.error ? st : null}>
      {st.loading && <p className="muted">Loading…</p>}
      {d && <>
        <BarChart items={Object.entries(d.status_counts).map(([label, value]) => ({ label, value }))} />
        <p className="muted small">{d.total_items} store-product lines on {d.date}. Critical = under 1 day of cover; low = below reorder point;
          overstock = above 2.5× reorder point. Suggested quantity tops stock up to {d.target_days} days of average sales.</p>
        {d.most_urgent.length ? <div className="scroll"><table><thead><tr><th>Store</th><th>Product</th><th>Stock</th><th>Days cover</th><th>Status</th><th>Order qty</th></tr></thead>
          <tbody>{d.most_urgent.map((i, k) => <tr key={k}><td>{i.store_id}</td><td>{i.product_id}</td><td>{i.stock_level}</td><td>{i.days_of_cover ?? "-"}</td>
            <td><span className={`pill ${i.status === "critical" ? "high" : "med"}`}>{i.status}</span></td><td>{i.suggested_reorder_qty}</td></tr>)}</tbody></table></div>
          : <p className="muted">Nothing is below its reorder point.</p>}
      </>}
    </Panel>
  );
}

function Dendrogram({ token }) {
  const [s, setS] = useState({ url: null, error: null });
  useEffect(() => {
    let url = null, off = false;
    api("/segments/dendrogram", { token, blob: true })
      .then((b) => { if (!off) { url = URL.createObjectURL(b); setS({ url, error: null }); } })
      .catch((e) => !off && setS({ url: null, error: e.message }));
    return () => { off = true; if (url) URL.revokeObjectURL(url); };
  }, [token]);
  if (s.error) return <p className="notice">Dendrogram unavailable: {s.error}</p>;
  return s.url ? <img className="dendro" src={s.url} alt="Hierarchical clustering dendrogram" /> : <p className="muted">Loading dendrogram…</p>;
}

/** Milestone 4: measured evaluation of every model, straight from the files the ML scripts wrote. */
export function ModelPerformance({ token }) {
  const st = useFetch("/models/performance", token);
  const d = st.data;
  const fc = d?.forecasting, seg = d?.segmentation, ch = d?.churn, rec = d?.recommendations, an = d?.anomalies?.evaluation;
  return (
    <Panel title="Model performance (Milestone 4 evaluation)" state={st.error ? st : null}>
      {st.loading && <p className="muted">Loading…</p>}
      {d && <>
        <h3>Sales forecasting</h3>
        {fc ? <>
          <div className="scroll"><table><thead><tr><th>Model</th><th>MAE</th><th>RMSE</th><th>MAPE</th><th>R²</th></tr></thead>
            <tbody>{fc.results.map((r) => <tr key={r.model}><td>{r.model}{r.model === fc.best_model && " ★"}</td><td>{money(r.mae)}</td><td>{money(r.rmse)}</td><td>{pct(r.mape)}</td><td>{num(r.r2)}</td></tr>)}</tbody></table></div>
          <p className="muted small">Test window {fc.evaluation.test_start} → {fc.evaluation.test_end} ({fc.evaluation.test_days} days, time-ordered, trained only on earlier days).
            ★ = best ML model by RMSE.</p>
          {fc.evaluation.beaten_by_baseline?.length > 0 && <p className="notice">No ML model beats “{fc.evaluation.beaten_by_baseline.join(", ")}”: this dataset has little learnable signal, so the forecast is close to the average level.</p>}
        </> : <p className="muted">Not generated yet - run <code>python ml/forecasting_models.py</code>.</p>}

        <h3>Customer segmentation</h3>
        {seg ? <>
          <p className="small">K-Means silhouette <b>{num(seg.kmeans_silhouette)}</b> · Hierarchical silhouette <b>{num(seg.hierarchical_silhouette)}</b> ·
            Adjusted Rand Index (K-Means vs Hierarchical) <b>{num(seg.adjusted_rand_index_kmeans_vs_hierarchical)}</b> ·
            K-Means seed stability (ARI) <b>{num(seg.kmeans_seed_stability_ari_mean)}</b></p>
          {seg.by_k && <div className="scroll"><table><thead><tr><th>K</th><th>Silhouette</th><th>Davies-Bouldin</th><th>Inertia</th></tr></thead>
            <tbody>{Object.entries(seg.by_k).map(([k, v]) => <tr key={k}><td>{k}{Number(k) === seg.chosen_k && " ✓"}</td><td>{num(v.silhouette)}</td><td>{num(v.davies_bouldin)}</td><td>{Math.round(v.inertia).toLocaleString()}</td></tr>)}</tbody></table></div>}
          {seg.k_justification && <p className="muted small">{seg.k_justification}</p>}
          <Dendrogram token={token} />
        </> : <p className="muted">Not generated yet - run <code>python ml/segmentation.py</code>.</p>}

        <h3>Churn prediction</h3>
        {ch ? <>
          <div className="scroll"><table><thead><tr><th>Model</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1</th><th>ROC-AUC</th></tr></thead>
            <tbody>{ch.results.map((r) => <tr key={r.model}><td>{r.model}{r.model === ch.selected_model && " ★"}</td><td>{num(r.accuracy)}</td><td>{num(r.precision)}</td><td>{num(r.recall)}</td><td>{num(r.f1)}</td><td>{num(r.roc_auc)}</td></tr>)}</tbody></table></div>
          <p className="muted small">Label: {ch.label}. Churn rate in training data {pct(ch.churn_rate * 100)}; test set {ch.test_size} customers.</p>
        </> : <p className="muted">Not generated yet - run <code>python ml/churn_models.py</code>.</p>}

        <h3>Recommendations & anomaly detection</h3>
        <div className="two">
          <div>{rec ? <ul className="plain">
            <li>Collaborative filtering Precision@3: <b>{pct(rec.cf_precision_at_3 * 100)}</b> (popularity baseline {pct(rec.popular_precision_at_3 * 100)})</li>
            <li>Recall@3: <b>{pct(rec.cf_recall_at_3 * 100)}</b> (baseline {pct(rec.popular_recall_at_3 * 100)})</li>
            <li className="muted small">{rec.customers_evaluated?.toLocaleString()} customers, {rec.holdout_days}-day time-based holdout.</li></ul>
            : <p className="muted">Not generated yet.</p>}</div>
          <div>{an ? <ul className="plain">
            <li>Recall on injected anomalies: <b>{pct(an.recall * 100)}</b>; precision {pct(an.precision * 100)}</li>
            <li>False-positive rate: <b>{pct(an.false_positive_rate * 100)}</b></li>
            <li className="muted small">Evaluated on {an.injected} synthetic anomalies injected into real rows (no fraud labels exist).</li></ul>
            : <p className="muted">Not generated yet.</p>}</div>
        </div>
      </>}
    </Panel>
  );
}
