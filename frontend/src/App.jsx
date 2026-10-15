import { useCallback, useEffect, useState } from "react";
import { api, money, RANGES, rangeLabel, useFetch } from "./api";
import { BarChart, TrendChart } from "./Charts";
import { Anomalies, ChurnRisk, Panel, Recommendations } from "./M3Panels";
import { InventoryIntel, ModelPerformance, SalesBreakdown } from "./M4Panels";
import "./App.css";

const ROLE_LABEL = { business_owner: "Business Owner", store_manager: "Store Manager", sales_executive: "Sales Executive", admin: "Administrator" };

const Icon = ({ name, size = 20 }) => {
  const P = {
    dashboard: "M4 20V10M10 20V4M16 20v-7M22 20H2",
    customers: "M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.9M16 3.1a4 4 0 010 7.8",
    inventory: "M21 8l-9-5-9 5v8l9 5 9-5V8zM3 8l9 5 9-5M12 13v8",
    alert: "M12 3l10 18H2L12 3zM12 10v5M12 18h.01",
    invoice: "M6 2h9l5 5v15H6V2zM14 2v6h6M9 13h8M9 17h8",
    models: "M3 3v18h18M7 15l4-4 3 3 5-6",
    users: "M12 15a3 3 0 100-6 3 3 0 000 6zM19.4 15a1.7 1.7 0 00.3 1.8l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.8-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 11-4 0v-.1a1.7 1.7 0 00-1.1-1.5 1.7 1.7 0 00-1.8.3l-.1.1a2 2 0 11-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.8 1.7 1.7 0 00-1.5-1H3a2 2 0 110-4h.1a1.7 1.7 0 001.5-1.1 1.7 1.7 0 00-.3-1.8l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.8.3H9a1.7 1.7 0 001-1.5V3a2 2 0 114 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.8-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.8V9a1.7 1.7 0 001.5 1H21a2 2 0 110 4h-.1a1.7 1.7 0 00-1.5 1z",
    user: "M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z",
    mail: "M3 5h18v14H3zM3 7l9 6 9-6",
    lock: "M5 11h14v10H5zM8 11V7a4 4 0 118 0v4",
    logout: "M9 21H5V3h4M16 17l5-5-5-5M21 12H9",
    download: "M12 3v12M7 10l5 5 5-5M4 21h16",
    trend: "M3 17l6-6 4 4 8-8M15 7h6v6",
    dollar: "M12 2v20M17 6H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6",
    calendar: "M3 5h18v16H3zM3 10h18M8 3v4M16 3v4",
    chevron: "M6 9l6 6 6-6",
    star: "M12 2l3 7 7 .6-5.3 4.7 1.6 7.2-6.3-3.7-6.3 3.7 1.6-7.2L2 9.6 9 9z",
  };
  return <svg className="ico" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={P[name]} /></svg>;
};

const resetTokenFromUrl = () => new URLSearchParams(window.location.search).get("reset_token");
const TITLES = {
  login: ["Welcome Back!", "Enter your email and password to continue"],
  register: ["Create your account", "Fill in your details to get started"],
  forgot: ["Forgot your password?", "Enter your e-mail and we will send you a reset link"],
  reset: ["Choose a new password", "Use at least 8 characters"],
};

function Login({ onLogin }) {
  const [mode, setMode] = useState(() => (resetTokenFromUrl() ? "reset" : "login"));   // login | register | forgot | reset
  const [f, setF] = useState({ name: "", email: "", password: "", confirm: "", role: "store_manager", admin_code: "" });
  const [err, setErr] = useState(""); const [ok, setOk] = useState(""); const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const go = (m) => { setMode(m); setErr(""); setOk(""); };

  async function submit(e) {
    e.preventDefault(); setErr(""); setOk(""); setBusy(true);
    try {
      if (mode === "forgot") {
        const r = await api("/auth/forgot-password", { method: "POST", body: { email: f.email } });
        setOk(r.message);
      } else if (mode === "reset") {
        if (f.password !== f.confirm) throw new Error("The two passwords do not match.");
        await api("/auth/reset-password", { method: "POST", body: { token: resetTokenFromUrl(), new_password: f.password } });
        window.history.replaceState({}, "", window.location.pathname);              // remove the token from the address bar
        setF({ ...f, password: "", confirm: "" }); setMode("login"); setOk("Password updated. Please log in with your new password.");
      } else {
        if (mode === "register") {
          await api("/register", { method: "POST", body: { name: f.name, email: f.email, password: f.password, role: f.role, ...(f.role === "admin" ? { admin_code: f.admin_code } : {}) } });
        }
        const t = await api("/login", { method: "POST", body: { email: f.email, password: f.password } });
        onLogin(t.access_token);
      }
    } catch (e2) { setErr(e2.message); } finally { setBusy(false); }
  }
  const [title, sub] = TITLES[mode];
  return (
    <div className="login-page">
      <svg className="login-curve" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        <path d="M0 0 H31.7 L14.3 43.5 C18 52 18 66 18.5 76 C19 88 20.5 96 22 100 H0 Z" fill="url(#lg)" />
        <defs><linearGradient id="lg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#ffffff" /><stop offset="1" stopColor="#e4e6ec" /></linearGradient></defs>
      </svg>
      <div className="login-brand"><span className="logo-mark">M</span><b>MarketMind AI</b></div>
      <div className="login-credit"><span>Retail analytics</span><b>MarketMind AI</b></div>

      <form className="login-form" onSubmit={submit}>
        <p className="login-kicker">MARKETMIND AI</p>
        <h1 className="login-title">RETAIL INTELLIGENCE</h1>
        <div className="avatar-ring"><div className="avatar"><Icon name="user" size={44} /></div></div>
        <p className="login-welcome">{title}</p>
        <p className="login-sub">{sub}</p>

        {mode === "register" && <label className="field"><Icon name="user" /><input placeholder="Full name" value={f.name} onChange={set("name")} required minLength={2} autoComplete="name" /></label>}
        {mode !== "reset" && <label className="field"><Icon name="mail" /><input type="email" placeholder="Email" value={f.email} onChange={set("email")} required autoComplete="username" /></label>}
        {mode !== "forgot" && <label className="field"><Icon name="lock" /><input type="password" placeholder={mode === "reset" ? "New password" : "Password"} value={f.password} onChange={set("password")} required minLength={8} autoComplete={mode === "login" ? "current-password" : "new-password"} /></label>}
        {mode === "reset" && <label className="field"><Icon name="lock" /><input type="password" placeholder="Confirm new password" value={f.confirm} onChange={set("confirm")} required minLength={8} autoComplete="new-password" /></label>}
        {mode === "login" && <button type="button" className="login-link" onClick={() => go("forgot")}>Forgot password?</button>}
        {mode === "register" && <label className="field"><Icon name="customers" /><select value={f.role} onChange={set("role")} aria-label="Role">{["business_owner", "store_manager", "sales_executive", "admin"].map((r) => <option key={r} value={r}>{ROLE_LABEL[r]}</option>)}</select></label>}
        {mode === "register" && f.role === "admin" && <>
          <label className="field"><Icon name="lock" /><input type="password" placeholder="Administrator access code" value={f.admin_code} onChange={set("admin_code")} required autoComplete="off" /></label>
          <p className="login-hint">Administrator accounts need the access code from the server’s ADMIN_REGISTRATION_CODE setting.</p>
        </>}
        {err && <p className="login-err" role="alert">{err}</p>}
        {ok && <p className="login-ok" role="status">{ok}</p>}
        <button className="login-btn" disabled={busy}>{busy ? "Please wait…" : { login: "Login", register: "Register & login", forgot: "Send reset link", reset: "Save new password" }[mode]}</button>
        {mode === "login" && <button type="button" className="login-switch" onClick={() => go("register")}>New here? Create an account</button>}
        {mode === "register" && <button type="button" className="login-switch" onClick={() => go("login")}>Already registered? Login</button>}
        {(mode === "forgot" || mode === "reset") && <button type="button" className="login-switch" onClick={() => { if (mode === "reset") window.history.replaceState({}, "", window.location.pathname); go("login"); }}>Back to login</button>}
      </form>
    </div>
  );
}

function Kpis({ token, range }) {
  const st = useFetch(`/sales/summary?range=${range}`, token);
  const d = st.data;
  if (st.error) return <Panel title="Today at a glance" state={st} />;
  if (st.loading && !d) return <div className="stat-row"><p className="muted">Loading…</p></div>;
  if (!d) return null;
  const ch = d.change_pct;
  const cards = [
    { icon: "trend", tone: "blue", label: `Revenue · ${rangeLabel(range)}`, value: money(d.total_revenue),
      sub: ch == null ? null : { up: ch >= 0, text: `${ch >= 0 ? "▲" : "▼"} ${Math.abs(ch)}% vs previous ${d.range_days} days` } },
    { icon: "dollar", tone: "violet", label: `Sales on ${d.latest_date}`, value: money(d.sales_latest_day) },
    { icon: "star", tone: "green", label: `Top product · ${rangeLabel(range)}`, value: d.top_product },
    { icon: "alert", tone: "amber", label: "Low stock alerts", value: d.low_stock_count },
  ];
  return (
    <>
      <div className="stat-row">
        {cards.map((c) => (
          <div className="stat-card" key={c.label}>
            <span className={`stat-icon ${c.tone}`}><Icon name={c.icon} size={26} /></span>
            <div><span className="stat-label">{c.label}</span><b className="stat-value" title={String(c.value)}>{c.value}</b>
              {c.sub && <small className={`stat-sub ${c.sub.up ? "up" : "down"}`}>{c.sub.text}</small>}</div>
          </div>
        ))}
      </div>
      {d.date_shift_days > 0 && <p className="muted small demo-note">Showing {d.range_start} to {d.range_end}. Demo data: the sample dataset ({d.source_start} to {d.source_end}) is displayed
        with its dates moved forward by {d.date_shift_days.toLocaleString()} days so the newest record is today. Set REBASE_DATES_TO_TODAY=0 in backend/.env to see the original dates.</p>}
    </>
  );
}

function Trend({ token, canForecast, range }) {
  const trend = useFetch(`/sales/trend?range=${range}`, token);
  const fc = useFetch(canForecast ? "/forecast/revenue" : null, token);
  return (
    <Panel title={`${canForecast ? "Sales trend & 30-day forecast" : "Sales trend"} · ${rangeLabel(range)}`} state={trend.error ? trend : null}>
      {trend.loading && !trend.data && <p className="muted">Loading…</p>}
      {trend.data && <TrendChart data={trend.data} forecast={fc.data?.daily || []} />}
      {canForecast && fc.error && <p className="notice">Forecast unavailable: {fc.error}</p>}
      {fc.data && <p className="muted small">Predicted revenue, {fc.data.period}: <b>{money(fc.data.predicted_revenue)}</b> · model: {fc.data.model_used}
        {" "}(test MAE {money(fc.data.metrics.mae)}, MAPE {fc.data.metrics.mape}%, R² {fc.data.metrics.r2}). Dashed line = forecast.</p>}
    </Panel>
  );
}

function Segments({ token }) {
  const st = useFetch("/segments", token);
  return (
    <Panel title="Customer Segments" state={st.error ? st : null}>
      {st.loading && <p className="muted">Loading…</p>}
      {st.data && <>
        <BarChart items={st.data.map((s) => ({ label: s.segment, value: s.customer_count }))} format={(v) => v.toLocaleString()} />
        <div className="scroll"><table><thead><tr><th>Segment</th><th>Customers</th><th>Avg order</th><th>Orders/cust.</th><th>Days inactive</th></tr></thead>
          <tbody>{st.data.map((s) => <tr key={s.segment}><td>{s.segment}</td><td>{s.customer_count.toLocaleString()} ({s.share_pct}%)</td><td>{money(s.avg_purchase_value, "£")}</td><td>{s.avg_purchase_frequency}</td><td>{Math.round(s.avg_inactivity_days)}</td></tr>)}</tbody></table></div>
        <ul className="plain">{st.data.map((s) => s.recommended_action && <li key={s.segment} className="small"><b>{s.segment}:</b> {s.recommended_action}</li>)}</ul>
      </>}
    </Panel>
  );
}

function InventoryAlerts({ token }) {
  const st = useFetch("/inventory/alerts?limit=8", token);
  return (
    <Panel title="Low Stock Alerts" state={st.error ? st : null}>
      {st.data && (st.data.alerts.length ? <div className="scroll"><table><thead><tr><th>Store</th><th>Product</th><th>Category</th><th>Stock</th><th>Reorder at</th></tr></thead>
        <tbody>{st.data.alerts.map((a, i) => <tr key={i}><td>{a.store_id}</td><td>{a.product_id}</td><td>{a.category}</td><td>{a.stock_level}</td><td>{a.reorder_point}</td></tr>)}</tbody></table></div>
        : <p className="muted">No items below their reorder point on {st.data.date}.</p>)}
    </Panel>
  );
}

function Invoices({ token, canCreate }) {
  const [tick, setTick] = useState(0);
  const st = useFetch(`/invoices?t=${tick}`, token);
  const [f, setF] = useState({ customer_id: "", description: "", amount: "", payment_status: "pending" });
  const [msg, setMsg] = useState("");
  async function create(e) {
    e.preventDefault(); setMsg("");
    try { await api("/invoices", { token, method: "POST", body: { ...f, amount: Number(f.amount) } }); setF({ ...f, customer_id: "", description: "", amount: "" }); setTick(tick + 1); }
    catch (err) { setMsg(err.message); }
  }
  return (
    <Panel title="Invoices" state={st.error ? st : null}>
      {canCreate && <form className="row" onSubmit={create}>
        <input placeholder="Customer ID" value={f.customer_id} onChange={(e) => setF({ ...f, customer_id: e.target.value })} required />
        <input placeholder="Description" value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })} />
        <input type="number" min="0.01" step="0.01" placeholder="Amount" value={f.amount} onChange={(e) => setF({ ...f, amount: e.target.value })} required />
        <select value={f.payment_status} onChange={(e) => setF({ ...f, payment_status: e.target.value })}><option>pending</option><option>paid</option><option>overdue</option></select>
        <button className="btn">Create</button></form>}
      {msg && <p className="notice">{msg}</p>}
      {st.data && (st.data.length ? <div className="scroll"><table><thead><tr><th>#</th><th>Customer</th><th>Description</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody>{st.data.slice(0, 8).map((i) => <tr key={i.id}><td>{i.id}</td><td>{i.customer_id}</td><td>{i.description}</td><td>{money(i.amount)}</td><td>{i.payment_status}</td></tr>)}</tbody></table></div>
        : <p className="muted">No invoices yet.</p>)}
    </Panel>
  );
}

function AdminUsers({ token, me }) {
  const [tick, setTick] = useState(0);
  const st = useFetch(`/admin/users?t=${tick}`, token);
  const [msg, setMsg] = useState("");
  const [f, setF] = useState({ name: "", email: "", password: "", role: "store_manager" });
  async function add(e) { e.preventDefault(); setMsg(""); try { await api("/admin/users", { token, method: "POST", body: f }); setF({ name: "", email: "", password: "", role: f.role }); setTick(tick + 1); } catch (err) { setMsg(err.message); } }
  async function del(id) { if (!window.confirm("Delete this user?")) return; try { await api(`/admin/users/${id}`, { token, method: "DELETE" }); setTick(tick + 1); } catch (err) { setMsg(err.message); } }
  return (
    <Panel title="User Management" state={st.error ? st : null}>
      <form className="row" onSubmit={add}>
        <input placeholder="Name" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} required />
        <input type="email" placeholder="Email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} required />
        <input type="password" placeholder="Password" minLength={8} value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} required />
        <select value={f.role} onChange={(e) => setF({ ...f, role: e.target.value })}>{Object.entries(ROLE_LABEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select>
        <button className="btn">Add user</button></form>
      {msg && <p className="notice">{msg}</p>}
      {st.data && <div className="scroll"><table><thead><tr><th>Name</th><th>Email</th><th>Role</th><th /></tr></thead>
        <tbody>{st.data.map((u) => <tr key={u.id}><td>{u.name}</td><td>{u.email}</td><td>{ROLE_LABEL[u.role]}</td><td>{u.email !== me.email && <button className="link" onClick={() => del(u.id)}>Delete</button>}</td></tr>)}</tbody></table></div>}
    </Panel>
  );
}

/** Ring showing how many store-product lines are healthy, plus a "needs reorder" callout. */
function StockHealth({ token }) {
  const st = useFetch("/inventory/summary?limit=1", token);
  const d = st.data;
  if (st.error) return <Panel title="Stock health" state={st} />;
  const c = d?.status_counts || {};
  const total = d?.total_items || 0;
  const pct = total ? Math.round(((c.healthy || 0) / total) * 100) : 0;
  const need = (c.critical || 0) + (c.low || 0);
  const R = 52, C = 2 * Math.PI * R;
  return (
    <section className="card health">
      <h2>Stock health</h2>
      {!d ? <p className="muted">Loading…</p> : <>
        <div className="ring">
          <svg viewBox="0 0 140 140" role="img" aria-label={`${pct}% of stock lines are healthy`}>
            <circle cx="70" cy="70" r={R} className="ring-bg" />
            <circle cx="70" cy="70" r={R} className="ring-fg" strokeDasharray={`${(pct / 100) * C} ${C}`} transform="rotate(-90 70 70)" />
          </svg>
          <div className="ring-label"><b>{pct}%</b><span>healthy</span></div>
        </div>
        <div className="callout"><b>{need.toLocaleString()} lines</b><span>need reordering</span></div>
        <p className="muted small">{total.toLocaleString()} store-product lines on {d.date}</p>
      </>}
    </section>
  );
}

const TABS = [
  { id: "overview", label: "Dashboard", icon: "dashboard", show: (can) => can("sales_summary") || can("inventory_alerts") },
  { id: "customers", label: "Customers", icon: "customers", show: (can) => can("segments") || can("recommendations") || can("churn") },
  { id: "inventory", label: "Inventory", icon: "inventory", show: (can) => can("inventory_alerts") },
  { id: "alerts", label: "Anomalies", icon: "alert", show: (can) => can("anomalies") },
  { id: "invoices", label: "Invoices", icon: "invoice", show: (can) => can("invoice_view") },
  { id: "models", label: "Model reports", icon: "models", show: (can) => can("model_performance") },
  { id: "users", label: "Users", icon: "users", show: (can) => can("user_management") },
];

function Dashboard({ token, me, onLogout }) {
  const can = (f) => me.features.includes(f);
  const tabs = TABS.filter((t) => t.show(can));
  const [tab, setTab] = useState(tabs[0]?.id);
  const [dl, setDl] = useState({ busy: false, err: "" });
  const [profile, setProfile] = useState(false);
  const [range, setRange] = useState(() => { const r = localStorage.getItem("mm_range"); return RANGES.some(([k]) => k === r) ? r : "30d"; });
  const pickRange = (r) => { setRange(r); localStorage.setItem("mm_range", r); };
  useEffect(() => {
    if (!profile) return;
    const onKey = (e) => e.key === "Escape" && setProfile(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [profile]);
  const initials = me.name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase();
  const current = tabs.find((t) => t.id === tab) || tabs[0];

  async function download() {
    setDl({ busy: true, err: "" });
    try {
      const blob = await api("/reports/business", { token, blob: true });
      const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "business_report.xlsx"; a.click(); URL.revokeObjectURL(a.href);
      setDl({ busy: false, err: "" });
    } catch (e) { setDl({ busy: false, err: e.message }); }
  }
  return (
    <div className="shell">
      <aside className="side">
        <div className="side-logo"><span className="logo-mark">M</span><b>MarketMind <i>AI</i></b></div>
        <nav className="side-nav" aria-label="Main">
          {tabs.map((t) => (
            <button key={t.id} className={`nav-pill${t.id === current?.id ? " active" : ""}`} onClick={() => setTab(t.id)} aria-current={t.id === current?.id ? "page" : undefined}>
              <Icon name={t.icon} size={19} /><span>{t.label}</span>
            </button>
          ))}
          {can("report_download") && (
            <button className="nav-pill export" onClick={download} disabled={dl.busy}>
              <Icon name="download" size={19} /><span>{dl.busy ? "Preparing…" : "Export report"}</span>
            </button>
          )}
        </nav>
        <div className="side-user">
          <button className="side-profile" onClick={() => setProfile(true)} aria-label="Open profile">
            <span className="side-avatar">{initials}</span>
            <b>{me.name}</b><span>{ROLE_LABEL[me.role]}</span>
          </button>
          <button className="side-logout" onClick={onLogout}>Log out <Icon name="logout" size={18} /></button>
        </div>
      </aside>

      <div className="main-col">
        <header className="topbar">
          <h1>{current?.label}</h1>
          {(current?.id === "overview" || current?.id === "alerts") && (
            <label className="range-pick" title="Show sales, trend, categories and alerts for this period">
              <Icon name="calendar" size={17} />
              <select value={range} onChange={(e) => pickRange(e.target.value)} aria-label="Date range">
                {RANGES.map(([k, l]) => <option key={k} value={k}>{l}</option>)}
              </select>
              <Icon name="chevron" size={16} />
            </label>
          )}
        </header>

        <main className="content">
          {dl.err && <p className="notice wide">{dl.err}</p>}
          {current?.id === "overview" && <div className="stack">
            {can("sales_summary") && <Kpis token={token} range={range} />}
            <div className="grid">
              {can("sales_summary") && <div className="span2"><Trend token={token} canForecast={can("forecast")} range={range} /></div>}
              {can("inventory_alerts") && <StockHealth token={token} />}
              {can("sales_summary") && <SalesBreakdown token={token} range={range} />}
              {can("segments") && <div className="span2"><Segments token={token} /></div>}
            </div>
          </div>}
          {current?.id === "customers" && <div className="grid">
            {can("segments") && <div className="span2"><Segments token={token} /></div>}
            {can("recommendations") && <Recommendations token={token} />}
            {can("churn") && <ChurnRisk token={token} />}
          </div>}
          {current?.id === "inventory" && <div className="grid">
            <InventoryAlerts token={token} />
            <InventoryIntel token={token} />
          </div>}
          {current?.id === "alerts" && <div className="grid"><div className="span2"><Anomalies token={token} range={range} /></div></div>}
          {current?.id === "invoices" && <div className="grid"><div className="span2"><Invoices token={token} canCreate={can("invoice_create")} /></div></div>}
          {current?.id === "models" && <div className="grid"><div className="span2"><ModelPerformance token={token} /></div></div>}
          {current?.id === "users" && <div className="grid"><div className="span2"><AdminUsers token={token} me={me} /></div></div>}
        </main>
      </div>

      {profile && (
        <div className="modal-back" onClick={() => setProfile(false)}>
          <div className="profile-card" role="dialog" aria-modal="true" aria-label="Your profile" onClick={(e) => e.stopPropagation()}>
            <div className="profile-avatar">{initials}</div>
            <h2>{me.name}</h2>
            <p className="muted">{me.email}</p>
            <p className="profile-role">{ROLE_LABEL[me.role]}</p>
            <div className="profile-actions">
              <button className="btn ghost" onClick={() => setProfile(false)}>Close</button>
              <button className="btn" onClick={onLogout}>Log out</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("mm_token"));
  const [me, setMe] = useState(null);
  const [err, setErr] = useState("");
  const logout = useCallback(() => { localStorage.removeItem("mm_token"); setToken(null); setMe(null); }, []);
  const login = (t) => { localStorage.setItem("mm_token", t); setToken(t); };

  useEffect(() => { window.addEventListener("mm-unauthorized", logout); return () => window.removeEventListener("mm-unauthorized", logout); }, [logout]);
  useEffect(() => {
    if (!token) return;
    setErr("");
    api("/me", { token }).then(setMe).catch((e) => { if (e.status !== 401) setErr(e.message); });
  }, [token]);

  if (!token) return <Login onLogin={login} />;
  if (err) return <div className="login-wrap"><div className="card login"><p className="notice">{err}</p><button className="btn" onClick={() => setToken(localStorage.getItem("mm_token"))}>Retry</button><button className="link" onClick={logout}>Log out</button></div></div>;
  if (!me) return <div className="login-wrap"><p className="muted">Loading your dashboard…</p></div>;
  return <Dashboard token={token} me={me} onLogout={logout} />;
}
