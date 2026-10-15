import { useState } from "react";
import { api, money, rangeLabel, useFetch } from "./api";
import { BarChart } from "./Charts";

export function Panel({ title, state, children, right }) {
  return (
    <section className="card">
      <div className="card-head"><h2>{title}</h2>{right}</div>
      {state?.loading && <p className="muted">Loading…</p>}
      {state?.error && <p className="notice">{state.error}</p>}
      {(!state || (!state.loading && !state.error)) && children}
    </section>
  );
}

/** M3: "recommended for you" (collaborative filtering) + "frequently bought with" (association rules). */
export function Recommendations({ token }) {
  const sample = useFetch("/recommendations", token);
  const [customer, setCustomer] = useState("");
  const [product, setProduct] = useState("");
  const [res, setRes] = useState({ data: null, error: null, loading: false });

  async function lookup(e) {
    e.preventDefault();
    if (!customer.trim()) return;
    setRes({ data: null, error: null, loading: true });
    try {
      const q = product.trim() ? `?product=${encodeURIComponent(product.trim())}` : "";
      setRes({ data: await api(`/recommendations/${encodeURIComponent(customer.trim())}${q}`, { token }), error: null, loading: false });
    } catch (err) { setRes({ data: null, error: err.status === 404 ? `Customer ${customer.trim()} was not found.` : err.message, loading: false }); }
  }
  const s = sample.data;
  return (
    <Panel title="Product Recommendations" state={sample.error ? sample : null}>
      <form className="row" onSubmit={lookup}>
        <input placeholder="Customer ID" value={customer} onChange={(e) => setCustomer(e.target.value)} />
        <input placeholder="Current product code (optional)" value={product} onChange={(e) => setProduct(e.target.value)} />
        <button className="btn">Recommend</button>
      </form>
      {s && <p className="muted small">Try customers: {s.sample_customers.map((c) => <button type="button" key={c} className="chip" onClick={() => setCustomer(c)}>{c}</button>)}
        {" "}products: {s.sample_products.map((c) => <button type="button" key={c} className="chip" onClick={() => setProduct(c)}>{c}</button>)}</p>}
      {res.loading && <p className="muted">Finding recommendations…</p>}
      {res.error && <p className="notice">{res.error}</p>}
      {res.data && (
        <div className="two">
          <div><h3>Recommended for you</h3>{res.data.recommended_for_you.length ? <ol>{res.data.recommended_for_you.map((r) => <li key={r.code}>{r.name} <span className="muted small">({r.code})</span></li>)}</ol> : <p className="muted">No suggestions for this customer.</p>}</div>
          {res.data.product && <div><h3>Frequently bought with {res.data.product.name || res.data.product.code}</h3>
            {res.data.frequently_bought_with.length ? <ol>{res.data.frequently_bought_with.map((r) => <li key={r.code}>{r.name} <span className="muted small">lift {r.lift}</span></li>)}</ol> : <p className="muted">No strong pairings found.</p>}</div>}
        </div>
      )}
    </Panel>
  );
}

const RISK_CLASS = { "High Risk": "high", "Medium Risk": "med", "Low Risk": "low" };

export function ChurnRisk({ token }) {
  const [risk, setRisk] = useState("High Risk");
  const st = useFetch(`/churn/risk?risk=${encodeURIComponent(risk)}&limit=10`, token);
  const d = st.data;
  return (
    <Panel title="Churn Risk" state={st.error ? st : null}
           right={<select value={risk} onChange={(e) => setRisk(e.target.value)}>{["High Risk", "Medium Risk", "Low Risk"].map((r) => <option key={r}>{r}</option>)}</select>}>
      {st.loading && !d && <p className="muted">Loading…</p>}
      {d && <>
        <BarChart items={Object.entries(d.counts).map(([label, value]) => ({ label, value }))} />
        <p className="muted small">Model: {d.selected_model}. Showing the highest-probability customers in “{risk}”.</p>
        <div className="scroll"><table><thead><tr><th>Customer</th><th>Probability</th><th>Risk</th><th>Orders</th><th>Days inactive</th><th>Segment</th></tr></thead>
          <tbody>{d.customers.map((c) => <tr key={c.customer_id}><td>{c.customer_id}</td><td>{(c.churn_probability * 100).toFixed(0)}%</td>
            <td><span className={`pill ${RISK_CLASS[c.retention_risk]}`}>{c.retention_risk}</span></td><td>{c.order_frequency}</td><td>{c.inactivity_days}</td><td>{c.segment}</td></tr>)}</tbody></table></div>
      </>}
    </Panel>
  );
}

export function Anomalies({ token, range = "all" }) {
  const [sev, setSev] = useState("high");
  const st = useFetch(`/anomalies?severity=${sev}&limit=10&range=${range}`, token);
  const d = st.data;
  return (
    <Panel title={`Anomaly Alerts · ${rangeLabel(range)}`} state={st.error ? st : null}
           right={<select value={sev} onChange={(e) => setSev(e.target.value)}><option value="high">High severity</option><option value="medium">Medium severity</option></select>}>
      {d && <>
        <p className="muted small">{d.total.toLocaleString()} alerts: {d.high.toLocaleString()} high, {d.medium.toLocaleString()} medium.</p>
        {d.alerts.length === 0 && <p className="muted">No alerts in this period.</p>}
        <ul className="alerts">{d.alerts.map((a, i) => <li key={i}><span className={`pill ${a.severity === "high" ? "high" : "med"}`}>{a.severity}</span> {a.message}</li>)}</ul>
      </>}
    </Panel>
  );
}
