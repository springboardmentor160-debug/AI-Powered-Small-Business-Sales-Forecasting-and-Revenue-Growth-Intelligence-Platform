import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  Area, AreaChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import {
  AlertCircle, ArrowRight, BarChart3, Boxes, ChevronDown, Command, DollarSign, Download, FileText, LogOut,
  Network, Pause, Play, Plus, ReceiptText, RefreshCw, ShieldAlert, ShieldCheck, ShoppingBag, UserMinus, Users,
} from "lucide-react";
import CountUp from "./CountUp";
import LiveStatus from "./LiveStatus";
import { SkeletonRows } from "./Skeleton";
import {
  ApiRequestError, getAdminUsers, getAnomalyAlerts, getChurnOverview, getCustomerSegments, getForecastModelComparison,
  getInventoryPreview, getInvoices, getRecommendationOverview, getRevenueForecast, getSalesSummary,
  type AdminUsersResponse, type AnomalyOverview, type ChurnOverview, type CustomerSegments, type ForecastModelComparison,
  type InventoryPreview, type InvoiceListResponse, type RecommendationOverview, type RevenueForecast, type SalesSummary, type UserRole,
} from "./lib/api";

interface Props {
  token: string;
  role: UserRole;
  name: string;
  email: string;
  pages: string[];
  onNavigate: (id: string) => void;
  onSignOut: () => void;
}

type Slot = { state: "loading" | "ok" | "error"; data?: unknown; error?: string };
type Slots = Record<string, Slot>;

const REFRESH_SECONDS = 30;
const RISK_COLORS = { "High Risk": "#FF6B6B", "Medium Risk": "#FFC857", "Low Risk": "#3DDC97" } as const;
const fmt = (n: number, d = 0) => n.toLocaleString(undefined, { minimumFractionDigits: d, maximumFractionDigits: d });
const initials = (n: string) => n.split(/\s+/).filter(Boolean).map((p) => p[0]).slice(0, 2).join("").toUpperCase() || "U";
const esc = (v: unknown) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);

export default function DashboardOverview({ token, role, name, email, pages, onNavigate, onSignOut }: Props) {
  const pageKey = pages.join(",");
  const has = useCallback((id: string) => pageKey.split(",").includes(id), [pageKey]);
  const [slots, setSlots] = useState<Slots>({});
  const [refreshing, setRefreshing] = useState(false);
  const [live, setLive] = useState(true);
  const [remaining, setRemaining] = useState(REFRESH_SECONDS);
  const [updated, setUpdated] = useState<Date | null>(null);
  const [range, setRange] = useState<30 | 60 | 0>(60);
  const [scope, setScope] = useState<"active" | "all">("active");
  const [hoverRisk, setHoverRisk] = useState<string | null>(null);
  const [hoverSeg, setHoverSeg] = useState<string | null>(null);
  const [menu, setMenu] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const get = useCallback(<T,>(k: string): { state: Slot["state"]; data?: T; error?: string } => (slots[k] as { state: Slot["state"]; data?: T; error?: string } | undefined) ?? { state: "loading" }, [slots]);

  const load = useCallback(async () => {
    setRefreshing(true);
    const jobs: [string, boolean, () => Promise<unknown>][] = [
      ["sales", true, () => getSalesSummary(token)],
      ["segments", has("segmentation"), () => getCustomerSegments(token)],
      ["recs", has("recommendations"), () => getRecommendationOverview(token)],
      ["churn", has("churn"), () => getChurnOverview(token)],
      ["alerts", has("alerts"), () => getAnomalyAlerts(token)],
      ["models", has("forecasts") || has("executive"), () => getForecastModelComparison(token)],
      ["revenue", has("forecasts"), () => getRevenueForecast(token)],
      ["invoices", has("invoices"), () => getInvoices(token)],
      ["inventory", has("inventory"), () => getInventoryPreview(token)],
      ["users", has("admin"), () => getAdminUsers(token)],
    ];
    await Promise.all(jobs.filter(([, on]) => on).map(([key, , fn]) =>
      fn().then(
        (data) => setSlots((s) => ({ ...s, [key]: { state: "ok", data } })),
        (e: unknown) => setSlots((s) => ({
          ...s,
          [key]: s[key]?.data ? s[key] : { state: "error", error: e instanceof ApiRequestError ? e.message : "Unable to load this section." },
        })),
      )));
    setUpdated(new Date());
    setRemaining(REFRESH_SECONDS);
    setRefreshing(false);
  }, [token, has]);

  useEffect(() => { void Promise.resolve().then(() => void load()); }, [load]);
  useEffect(() => {
    if (!live) return;
    const t = window.setInterval(() => setRemaining((r) => Math.max(0, r - 1)), 1000);
    return () => window.clearInterval(t);
  }, [live]);
  useEffect(() => { if (live && remaining === 0 && !refreshing) void load(); }, [remaining, live, refreshing, load]);
  useEffect(() => {
    const close = (e: MouseEvent) => { if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenu(false); };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  const sales = get<SalesSummary>("sales"), segs = get<CustomerSegments>("segments"), recs = get<RecommendationOverview>("recs");
  const churn = get<ChurnOverview>("churn"), alerts = get<AnomalyOverview>("alerts"), models = get<ForecastModelComparison>("models");
  const revenue = get<RevenueForecast>("revenue"), inv = get<InvoiceListResponse>("invoices"), stock = get<InventoryPreview>("inventory");
  const users = get<AdminUsersResponse>("users");

  const bestOf = (list?: { model: string; mae: number; rmse: number }[]) =>
    list?.length ? [...list].sort((a, b) => a.mae - b.mae)[0] : undefined;
  const bestRevenue = bestOf(models.data?.uci_revenue_models);
  const bestDemand = bestOf(models.data?.m5_demand_models);

  const invoiceStats = useMemo(() => {
    const list = inv.data?.invoices ?? [];
    const sum = (s?: string) => list.filter((i) => !s || i.payment_status === s).reduce((a, i) => a + Number(i.total_amount), 0);
    return { list, total: sum(), paid: sum("Paid"), pending: sum("Pending"), cancelled: sum("Cancelled") };
  }, [inv.data]);

  const trend = useMemo(() => {
    const preds = revenue.data?.predictions ?? [];
    const key = ({ Prophet: "prophet_prediction", "Random Forest": "random_forest_prediction", XGBoost: "xgboost_prediction" } as Record<string, string>)[
      bestOf(revenue.data?.models)?.model ?? ""] ?? "random_forest_prediction";
    const rows = preds.map((p) => ({ date: String(p.date ?? "").slice(5, 10), actual: Number(p.actual_revenue ?? 0), predicted: Number(p[key] ?? 0) }));
    return range ? rows.slice(-range) : rows;
  }, [revenue.data, range]);

  const risk = churn.data ? (scope === "active" ? churn.data.still_active_risk_counts : churn.data.risk_counts) : undefined;
  const riskTotal = risk ? Object.values(risk).reduce((a, b) => a + b, 0) : 0;
  const donut = risk ? (Object.keys(RISK_COLORS) as (keyof typeof RISK_COLORS)[]).map((k) => ({ name: k, value: risk[k] ?? 0 })) : [];

  /* ---------- KPI tiles ---------- */
  type Kpi = { id: string; label: string; icon: typeof Users; slot: { state: string }; value: number | null; dec?: number; prefix?: string; sub: string; page: string; bar?: number };
  const kpis: Kpi[] = [
    { id: "rev", label: "Total revenue", icon: DollarSign, slot: sales, value: sales.data ? Number(sales.data.total_revenue) : null, dec: 2, sub: sales.data ? `${fmt(Number(sales.data.total_orders))} orders` : "", page: "dashboard" },
    ...(has("segmentation") ? [{ id: "cust", label: "Customers", icon: Users, slot: segs, value: segs.data?.total_customers ?? null, sub: segs.data ? `${segs.data.segment_count} segments` : "", page: "segmentation" }] : []),
    ...(has("churn") ? [{ id: "churn", label: "High churn risk", icon: UserMinus, slot: churn, value: churn.data ? (churn.data.still_active_risk_counts["High Risk"] ?? 0) : null, sub: churn.data ? `of ${fmt(churn.data.still_active_customers)} active customers` : "", page: "churn",
      bar: churn.data && churn.data.still_active_customers ? ((churn.data.still_active_risk_counts["High Risk"] ?? 0) / churn.data.still_active_customers) * 100 : undefined }] : []),
    ...(has("alerts") ? [{ id: "alerts", label: "Open alerts", icon: ShieldAlert, slot: alerts, value: alerts.data?.total_alerts ?? null, sub: alerts.data ? `${alerts.data.by_severity?.high ?? 0} high severity` : "", page: "alerts" }] : []),
    ...(has("invoices") ? [{ id: "inv", label: "Invoices", icon: ReceiptText, slot: inv, value: inv.data?.total_invoices ?? null, sub: inv.data ? `${fmt(invoiceStats.pending, 2)} outstanding` : "", page: "invoices",
      bar: invoiceStats.total ? (invoiceStats.paid / invoiceStats.total) * 100 : undefined }] : []),
    ...(has("inventory") ? [{ id: "stock", label: "Est. stock units", icon: Boxes, slot: stock, value: stock.data?.total_estimated_remaining_stock ?? null, sub: stock.data ? `${fmt(stock.data.total_products)} products` : "", page: "inventory",
      bar: stock.data && stock.data.total_estimated_initial_stock ? (stock.data.total_estimated_remaining_stock / stock.data.total_estimated_initial_stock) * 100 : undefined }] : []),
    ...(has("admin") ? [{ id: "users", label: "Platform users", icon: ShieldCheck, slot: users, value: users.data?.users?.length ?? null, sub: users.data ? `${users.data.users.filter((u) => u.is_active).length} active` : "", page: "admin" }] : []),
  ];

  /* ---------- export report ---------- */
  function exportReport() {
    const rows = (h: string[], r: (string | number)[][]) => `<table><thead><tr>${h.map((x) => `<th>${esc(x)}</th>`).join("")}</tr></thead><tbody>${r.map((x) => `<tr>${x.map((c) => `<td>${esc(c)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
    const sec = (t: string, body: string) => `<h2>${esc(t)}</h2>${body}`;
    const parts: string[] = [];
    if (sales.data) parts.push(sec("Sales", rows(["Metric", "Value"], [["Total revenue", fmt(Number(sales.data.total_revenue), 2)], ["Total orders", fmt(Number(sales.data.total_orders))], ["Top product", sales.data.top_product]])));
    if (segs.data) parts.push(sec("Customer segments", rows(["Segment", "Customers", "Avg purchase value"], segs.data.segment_summary.map((s) => [s.segment, s.customer_count, fmt(s.average_purchase_value, 2)]))));
    if (churn.data) parts.push(sec("Churn risk (active customers)", rows(["Risk", "Customers"], Object.entries(churn.data.still_active_risk_counts))));
    if (alerts.data) parts.push(sec("Alerts", rows(["Severity", "Count"], Object.entries(alerts.data.by_severity ?? {}))));
    if (bestRevenue || bestDemand) parts.push(sec("Best forecasting models (lowest MAE)", rows(["Task", "Model", "MAE", "RMSE"], [
      ...(bestRevenue ? [["UCI revenue", bestRevenue.model, fmt(bestRevenue.mae, 2), fmt(bestRevenue.rmse, 2)]] : []),
      ...(bestDemand ? [["M5 demand", bestDemand.model, fmt(bestDemand.mae, 2), fmt(bestDemand.rmse, 2)]] : [])])));
    if (inv.data) parts.push(sec("Invoices", rows(["Invoice", "Customer", "Total", "Status"], invoiceStats.list.slice(0, 20).map((i) => [i.invoice_id, i.customer_name, fmt(Number(i.total_amount), 2), i.payment_status]))));
    if (stock.data) parts.push(sec("Inventory (estimates)", rows(["Metric", "Value"], [["Products", fmt(stock.data.total_products)], ["Units sold", fmt(stock.data.total_units_sold)], ["Estimated remaining", fmt(stock.data.total_estimated_remaining_stock)]])));
    const html = `<!doctype html><html><head><meta charset="utf-8"><title>MarketMind AI report</title><style>
body{font-family:Inter,Arial,sans-serif;color:#133336;max-width:860px;margin:40px auto;padding:0 24px}h1{font-family:Georgia,serif;color:#003B46;margin-bottom:0}
.sub{color:#006770;font-size:13px;letter-spacing:.12em;text-transform:uppercase}h2{color:#006770;border-bottom:2px solid #00A3A9;padding-bottom:6px;margin-top:32px}
table{width:100%;border-collapse:collapse;margin-top:8px}th{background:#003B46;color:#BFF2F4;text-align:left;padding:8px 10px;font-size:11px;letter-spacing:.1em;text-transform:uppercase}
td{padding:8px 10px;border-bottom:1px solid #D5E8EA}.foot{margin-top:36px;font-size:11px;color:#5E8087}</style></head><body>
<p class="sub">MarketMind AI · Business report</p><h1>Business overview</h1><p>Prepared for ${esc(name)} (${esc(role.replaceAll("_", " "))}) · ${esc(new Date().toLocaleString())}</p>
${parts.join("") || "<p>No data was available when this report was generated.</p>"}
<p class="foot">Inventory values are estimates. MAE and RMSE are evaluation metrics, not guaranteed future performance. Use Print → Save as PDF for a PDF copy.</p></body></html>`;
    const url = URL.createObjectURL(new Blob([html], { type: "text/html;charset=utf-8" }));
    const a = document.createElement("a"); a.href = url; a.download = `marketmind-report-${new Date().toISOString().slice(0, 10)}.html`; a.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  const first = (name.split(/\s+/)[0] || "there").toUpperCase();
  const ringPct = ((REFRESH_SECONDS - remaining) / REFRESH_SECONDS) * 100;
  const revSpan = has("churn") ? "ov-8" : "ov-12";

  return (
    <div className="ov">
      {/* ---------- Welcome bar ---------- */}
      <div className="ov-welcome">
        <h2>Welcome, {first}</h2>
        <div className="ov-welcome-right">
          <button type="button" className="ov-export" onClick={exportReport}><Download size={15} /> Export report</button>
          <div className="ov-profile" ref={menuRef}>
            <button type="button" className="ov-profile-btn" onClick={() => setMenu((m) => !m)} aria-haspopup="menu" aria-expanded={menu}>
              <span className="ov-avatar">{initials(name)}</span>
              <span className="ov-profile-name">{name.toUpperCase()}</span>
              <ChevronDown size={15} className={menu ? "lx-flip" : ""} />
            </button>
            {menu && (
              <div className="ov-menu" role="menu">
                <div className="ov-menu-head"><b>{name}</b><small>{email}</small><span className="role-chip">{role.replaceAll("_", " ")}</span></div>
                <button type="button" role="menuitem" onClick={onSignOut}><LogOut size={15} /> Sign out</button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ---------- Hero ---------- */}
      <div className="ov-hero">
        <div>
          <p className="eyebrow">YOUR BUSINESS OVERVIEW</p>
          <h1>Your business, in focus.</h1>
          <p className="welcome-copy">Sales, customers, risk, forecasts and stock, live in one place.</p>
        </div>
        <div className="ov-live">
          <button type="button" className={`ov-ring ${live ? "on" : ""}`} onClick={() => setLive((l) => !l)} aria-label={live ? "Pause live refresh" : "Resume live refresh"}
            style={{ background: `conic-gradient(var(--teal-4) ${live ? ringPct : 100}%, var(--line) 0)` }}>
            <span>{live ? <Pause size={14} /> : <Play size={14} />}</span>
          </button>
          <div className="ov-live-text">
            <b>{live ? `Live · next refresh in ${remaining}s` : "Live refresh paused"}</b>
            <small>{updated ? `Updated ${updated.toLocaleTimeString()}` : "Loading…"}</small>
          </div>
          <button type="button" className="button button-secondary ov-refresh" onClick={() => void load()} disabled={refreshing}>
            <RefreshCw size={15} className={refreshing ? "lx-spin" : ""} /> Refresh all
          </button>
          <LiveStatus />
        </div>
      </div>

      {/* ---------- Quick actions ---------- */}
      <div className="ov-actions">
        {has("invoices") && <button type="button" onClick={() => onNavigate("invoices")}><Plus size={16} /> New invoice</button>}
        {has("forecasts") && <button type="button" onClick={() => onNavigate("forecasts")}><Network size={16} /> View forecasts</button>}
        {has("executive") && <button type="button" onClick={() => onNavigate("executive")}><BarChart3 size={16} /> Executive summary</button>}
        <button type="button" onClick={() => window.dispatchEvent(new KeyboardEvent("keydown", { key: "k", ctrlKey: true }))}><Command size={16} /> Jump to… <kbd>Ctrl</kbd><kbd>K</kbd></button>
      </div>

      {/* ---------- KPI tiles ---------- */}
      <div className="ov-kpis" data-n={kpis.length}>
        {kpis.map(({ id, label, icon: Icon, slot, value, dec, sub, page, bar }, i) => (
          <button key={id} type="button" className="ov-kpi" style={{ animationDelay: `${i * 70}ms` }} onClick={() => onNavigate(page)}>
            <span className="ov-kpi-top"><span className="ov-kpi-icon"><Icon size={18} /></span><ArrowRight size={15} className="ov-arrow" /></span>
            <span className="ov-kpi-label">{label}</span>
            <strong className="ov-kpi-value">
              {slot.state === "loading" ? <span className="lx-skeleton" style={{ width: 90 }} /> : value === null ? "—" : <CountUp value={value} decimals={dec ?? 0} />}
            </strong>
            <small>{slot.state === "error" ? "Unavailable" : sub}</small>
            {bar !== undefined && <span className="ov-bar"><i style={{ width: `${Math.min(100, Math.max(0, bar))}%` }} /></span>}
          </button>
        ))}
      </div>

      {/* ---------- Module cards ---------- */}
      <div className="ov-grid">
        {has("forecasts") && (
          <ModuleCard span={revSpan} title="Revenue forecast" icon={Network} slot={revenue} onOpen={() => onNavigate("forecasts")} onRetry={load}
            extra={<div className="ov-chips">{([[30, "30d"], [60, "60d"], [0, "All"]] as const).map(([v, l]) => (
              <button key={l} type="button" className={range === v ? "on" : ""} onClick={() => setRange(v)}>{l}</button>))}</div>}>
            <div className="ov-chart">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trend} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="ovA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#00A3A9" stopOpacity=".55" /><stop offset="1" stopColor="#00A3A9" stopOpacity="0" /></linearGradient>
                  </defs>
                  <CartesianGrid stroke="#1B3E46" strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} minTickGap={24} />
                  <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} width={44} tickFormatter={(v: number) => v.toLocaleString(undefined, { notation: "compact" })} />
                  <Tooltip contentStyle={{ background: "#0D1F25", border: "1px solid #1B3E46", borderRadius: 10, color: "#EAF6F7" }} formatter={(v) => fmt(Number(v), 0)} />
                  <Area type="monotone" dataKey="predicted" name={`Predicted (${bestOf(revenue.data?.models)?.model ?? "best model"})`} stroke="#00A3A9" strokeWidth={2.5} fill="url(#ovA)" animationDuration={900} />
                  <Area type="monotone" dataKey="actual" name="Actual" stroke="#F2FBFC" strokeWidth={2} fill="none" animationDuration={900} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <p className="ov-note">Best model on the test window: <b>{bestOf(revenue.data?.models)?.model ?? "n/a"}</b> (lowest MAE).</p>
          </ModuleCard>
        )}

        {has("churn") && (
          <ModuleCard span="ov-4" title="Churn risk" icon={UserMinus} slot={churn} onOpen={() => onNavigate("churn")} onRetry={load}
            extra={<div className="ov-chips">{(["active", "all"] as const).map((s) => (
              <button key={s} type="button" className={scope === s ? "on" : ""} onClick={() => setScope(s)}>{s === "active" ? "Active" : "All"}</button>))}</div>}>
            <div className="ov-donut">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={donut} dataKey="value" innerRadius="64%" outerRadius="92%" paddingAngle={3} stroke="none" animationDuration={900}
                    onMouseEnter={(_, i) => setHoverRisk(donut[i]?.name ?? null)} onMouseLeave={() => setHoverRisk(null)}>
                    {donut.map((d) => <Cell key={d.name} fill={RISK_COLORS[d.name as keyof typeof RISK_COLORS]} opacity={hoverRisk && hoverRisk !== d.name ? 0.35 : 1} />)}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="ov-donut-center">
                <strong>{fmt(hoverRisk ? (risk?.[hoverRisk as keyof typeof RISK_COLORS] ?? 0) : riskTotal)}</strong>
                <small>{hoverRisk ?? "customers"}</small>
              </div>
            </div>
            <ul className="ov-legend">{donut.map((d) => (
              <li key={d.name} onMouseEnter={() => setHoverRisk(d.name)} onMouseLeave={() => setHoverRisk(null)}>
                <i style={{ background: RISK_COLORS[d.name as keyof typeof RISK_COLORS] }} />{d.name}<b>{fmt(d.value)}</b>
                <span>{riskTotal ? Math.round((d.value / riskTotal) * 100) : 0}%</span></li>))}</ul>
          </ModuleCard>
        )}

        {has("segmentation") && (
          <ModuleCard span="ov-4" title="Customer segments" icon={Users} slot={segs} onOpen={() => onNavigate("segmentation")} onRetry={load}>
            {(() => {
              const list = segs.data?.segment_summary ?? [];
              const max = Math.max(1, ...list.map((s) => s.customer_count));
              const h = list.find((s) => s.segment === hoverSeg);
              return (<>
                <ul className="ov-bars">{list.map((s) => (
                  <li key={s.segment} onMouseEnter={() => setHoverSeg(s.segment)} onMouseLeave={() => setHoverSeg(null)} className={hoverSeg && hoverSeg !== s.segment ? "dim" : ""}>
                    <span>{s.segment}</span><span className="ov-track"><i style={{ width: `${(s.customer_count / max) * 100}%` }} /></span><b>{fmt(s.customer_count)}</b></li>))}</ul>
                <p className="ov-note">{h ? <>Avg purchase value <b>{fmt(h.average_purchase_value, 2)}</b> · {fmt(h.average_purchase_frequency, 1)} orders · last seen {fmt(h.average_customer_activity_days)} days ago</> : "Hover a segment for its average behaviour."}</p>
              </>);
            })()}
          </ModuleCard>
        )}

        {has("invoices") && (
          <ModuleCard span="ov-4" title="Invoices" icon={FileText} slot={inv} onOpen={() => onNavigate("invoices")} onRetry={load}>
            <div className="ov-split">
              <span style={{ width: `${invoiceStats.total ? (invoiceStats.paid / invoiceStats.total) * 100 : 0}%`, background: "#3DDC97" }} />
              <span style={{ width: `${invoiceStats.total ? (invoiceStats.pending / invoiceStats.total) * 100 : 0}%`, background: "#FFC857" }} />
              <span style={{ width: `${invoiceStats.total ? (invoiceStats.cancelled / invoiceStats.total) * 100 : 0}%`, background: "#FF6B6B" }} />
            </div>
            <div className="ov-trio"><div><small>Paid</small><b>{fmt(invoiceStats.paid, 2)}</b></div><div><small>Pending</small><b>{fmt(invoiceStats.pending, 2)}</b></div><div><small>Cancelled</small><b>{fmt(invoiceStats.cancelled, 2)}</b></div></div>
            <ul className="ov-list">{[...invoiceStats.list].sort((a, b) => b.created_at.localeCompare(a.created_at)).slice(0, 4).map((i) => (
              <li key={i.invoice_id}><span><b>{i.invoice_id}</b><small>{i.customer_name}</small></span><span className={`lx-badge ${i.payment_status.toLowerCase()}`}>{i.payment_status}</span><b>{fmt(Number(i.total_amount), 2)}</b></li>))}
              {invoiceStats.list.length === 0 && <li className="ov-empty">No invoices yet.</li>}</ul>
          </ModuleCard>
        )}

        {has("alerts") && (
          <ModuleCard span="ov-4" title="Alerts" icon={ShieldAlert} slot={alerts} onOpen={() => onNavigate("alerts")} onRetry={load}>
            <div className="ov-trio"><div><small>Total</small><b>{fmt(alerts.data?.total_alerts ?? 0)}</b></div>
              <div><small>High</small><b style={{ color: "#FF8E8E" }}>{fmt(alerts.data?.by_severity?.high ?? 0)}</b></div>
              <div><small>Medium</small><b style={{ color: "#FFD27A" }}>{fmt(alerts.data?.by_severity?.medium ?? 0)}</b></div></div>
            <ul className="ov-list">{(alerts.data?.alerts ?? []).slice(0, 4).map((a) => (
              <li key={a.alert_id}><span><b>{a.alert_type.replaceAll("_", " ")}</b><small>{a.message}</small></span>
                <span className={`lx-badge ${a.severity === "high" ? "cancelled" : "pending"}`}>{a.severity}</span></li>))}
              {(alerts.data?.alerts ?? []).length === 0 && <li className="ov-empty">No alerts right now.</li>}</ul>
          </ModuleCard>
        )}

        {has("recommendations") && (
          <ModuleCard span="ov-4" title="Recommendations" icon={ShoppingBag} slot={recs} onOpen={() => onNavigate("recommendations")} onRetry={load}>
            <div className="ov-trio"><div><small>Rules</small><b>{fmt(recs.data?.rule_count ?? 0)}</b></div><div><small>Upsell pairs</small><b>{fmt(recs.data?.upsell_pair_count ?? 0)}</b></div></div>
            <ul className="ov-bars">{(recs.data?.evaluation ?? []).slice(0, 2).map((e) => (
              <li key={e.model}><span>{e.model}</span><span className="ov-track"><i style={{ width: `${Math.min(100, e.hit_rate_at_10 * 100)}%` }} /></span><b>{(e.hit_rate_at_10 * 100).toFixed(1)}%</b></li>))}</ul>
            <p className="ov-note">Hit rate in the top 10 recommendations.</p>
            <ul className="ov-list">{(recs.data?.top_rules ?? []).slice(0, 2).map((r) => (
              <li key={r.antecedent_name + r.consequent_name}><span><b>{r.antecedent_name}</b><small>→ {r.consequent_name}</small></span><b>×{r.lift.toFixed(1)}</b></li>))}</ul>
          </ModuleCard>
        )}

        {has("inventory") && (
          <ModuleCard span="ov-4" title="Inventory" icon={Boxes} slot={stock} onOpen={() => onNavigate("inventory")} onRetry={load}>
            <div className="ov-trio"><div><small>Products</small><b>{fmt(stock.data?.total_products ?? 0)}</b></div><div><small>Units sold</small><b>{fmt(stock.data?.total_units_sold ?? 0)}</b></div><div><small>Est. left</small><b>{fmt(stock.data?.total_estimated_remaining_stock ?? 0)}</b></div></div>
            <ul className="ov-bars">{[...(stock.data?.products ?? [])].filter((p) => p.InitialStock > 0).sort((a, b) => a.EstimatedRemainingStock / a.InitialStock - b.EstimatedRemainingStock / b.InitialStock).slice(0, 4).map((p) => (
              <li key={p.ProductID}><span title={p.ProductDescription}>{p.ProductDescription}</span><span className="ov-track warn"><i style={{ width: `${Math.max(2, (p.EstimatedRemainingStock / p.InitialStock) * 100)}%` }} /></span><b>{fmt(p.EstimatedRemainingStock)}</b></li>))}</ul>
            <p className="ov-note">Lowest estimated stock. Values are estimates, not a physical count.</p>
          </ModuleCard>
        )}

        {has("executive") && (
          <ModuleCard span="ov-4" title="Executive summary" icon={BarChart3} slot={models} onOpen={() => onNavigate("executive")} onRetry={load}>
            <ul className="ov-facts">
              <li><small>Top product</small><b>{sales.data?.top_product ?? "—"}</b></li>
              <li><small>Best revenue model</small><b>{bestRevenue ? `${bestRevenue.model} · MAE ${fmt(bestRevenue.mae, 0)}` : "—"}</b></li>
              <li><small>Best demand model</small><b>{bestDemand ? `${bestDemand.model} · MAE ${fmt(bestDemand.mae, 2)}` : "—"}</b></li>
              {segs.data && <li><small>Largest segment</small><b>{[...segs.data.segment_summary].sort((a, b) => b.customer_count - a.customer_count)[0]?.segment ?? "—"}</b></li>}
            </ul>
          </ModuleCard>
        )}

        {has("admin") && (
          <ModuleCard span="ov-4" title="Team" icon={ShieldCheck} slot={users} onOpen={() => onNavigate("admin")} onRetry={load}>
            <ul className="ov-list">{(users.data?.users ?? []).slice(0, 4).map((u) => (
              <li key={u.id}><span className="ov-user"><span className="ov-avatar sm">{initials(u.name)}</span><span><b>{u.name}</b><small>{u.role.replaceAll("_", " ")}</small></span></span>
                <span className={`lx-badge ${u.is_active ? "paid" : "cancelled"}`}>{u.is_active ? "active" : "inactive"}</span></li>))}</ul>
          </ModuleCard>
        )}
      </div>

      <p className="disclaimer">Sales metrics come from the authenticated backend API. Inventory values are estimates and must not be interpreted as a verified physical stock count. MAE and RMSE are evaluation metrics, not guaranteed future performance.</p>
    </div>
  );
}

function ModuleCard({ title, icon: Icon, slot, span, onOpen, onRetry, extra, children }: {
  title: string; icon: typeof Users; slot: Slot; span: string; onOpen: () => void; onRetry: () => void; extra?: ReactNode; children: ReactNode;
}) {
  return (
    <article className={`ov-card ${span}`}>
      <header>
        <span className="ov-card-icon"><Icon size={18} /></span>
        <h3>{title}</h3>
        {extra}
        <button type="button" className="ov-open" onClick={onOpen}>Open <ArrowRight size={14} /></button>
      </header>
      {slot.state === "loading" ? (
        <table className="ov-skel"><tbody><SkeletonRows cols={3} rows={4} /></tbody></table>
      ) : slot.state === "error" ? (
        <p className="invoice-error" role="alert"><AlertCircle size={16} /> {slot.error}<button type="button" className="lx-retry" onClick={() => void onRetry()}>Retry</button></p>
      ) : children}
    </article>
  );
}
