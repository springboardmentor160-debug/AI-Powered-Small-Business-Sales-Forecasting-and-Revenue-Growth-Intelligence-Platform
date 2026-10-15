import { useMemo, useState } from "react";
import { Search, UserMinus, Wand2, BellRing, ShoppingBasket } from "lucide-react";
import Alert from "./components/ui/Alert";
import Badge, { RiskBadge } from "./components/ui/Badge";
import Button from "./components/ui/Button";
import { Card, CardBody, CardHeader } from "./components/ui/Card";
import DataTable from "./components/ui/DataTable";
import { Field, Input } from "./components/ui/Field";
import Skeleton from "./components/ui/Skeleton";
import { useInsights } from "./hooks/useInsights";
import { apiRequest } from "./lib/api";
import { cn, formatDate, formatNumber, formatPercent, riskTone } from "./lib/format";

/* ------------------------------------------------------------------ */
/* Product recommendations: printed as a till-roll basket slip         */
/* ------------------------------------------------------------------ */

function Barcode({ seed }) {
  // Deterministic bars from the customer id, so each slip looks like its own.
  const digits = String(seed).replace(/\D/g, "").padEnd(8, "7");
  const bars = Array.from({ length: 34 }, (_, i) => {
    const d = Number(digits[i % digits.length]);
    return { w: 1 + ((d + i * 3) % 3), gap: 1 + ((d * 2 + i) % 2) };
  });
  return (
    <div aria-hidden="true" className="flex h-8 items-stretch">
      {bars.map((bar, i) => (
        <span
          key={i}
          className="bg-stone-800"
          style={{ width: bar.w, marginRight: bar.gap }}
        />
      ))}
    </div>
  );
}

function SlipLines({ title, items, empty }) {
  return (
    <div>
      <p className="mb-2 font-semibold text-stone-900">{title}</p>
      {!items || items.length === 0 ? (
        <p className="text-stone-500">{empty}</p>
      ) : (
        <ul className="space-y-1.5">
          {items.map((item, index) => (
            <li key={`${item}-${index}`} className="flex items-end gap-2">
              <span className="min-w-0 break-words">{item}</span>
              <span
                aria-hidden="true"
                className="mb-1 min-w-3 flex-1 border-b border-dotted border-stone-400"
              />
              <span aria-hidden="true" className="shrink-0 font-semibold text-indigo-600">
                +
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Slip({ loading, result, searchedProduct }) {
  const count =
    (result?.recommended_for_you?.length ?? 0) +
    (searchedProduct ? (result?.frequently_bought_with?.length ?? 0) : 0);

  return (
    <div
      aria-live="polite"
      className="relative mx-auto w-full max-w-md rounded-md bg-stone-50 px-6 py-6 font-mono text-[13px] leading-relaxed text-stone-700 shadow-card ring-1 ring-stone-200 dark:bg-stone-100 dark:shadow-pop dark:ring-0"
    >
      <div className="text-center">
        <ShoppingBasket aria-hidden="true" className="mx-auto mb-1 size-5 text-stone-800" />
        <p className="font-bold text-stone-900">Basket</p>
        <p className="text-stone-500">
          {result ? `Customer ${result.customer_id}` : "No customer selected"}
        </p>
      </div>
      <div aria-hidden="true" className="my-4 border-t border-dashed border-stone-400" />

      {loading && (
        <div className="space-y-3" aria-busy="true">
          {[72, 58, 66, 44].map((w) => (
            <div
              key={w}
              className="h-3.5 animate-pulse rounded-sm bg-stone-200 motion-reduce:animate-none"
              style={{ width: `${w}%` }}
            />
          ))}
        </div>
      )}

      {!loading && !result && (
        <p className="py-4 text-center text-stone-500">
          Enter a customer ID to print their basket.
        </p>
      )}

      {!loading && result && (
        <div className="space-y-5">
          <SlipLines
            title="Recommended for them"
            items={result.recommended_for_you}
            empty="No personalized picks for this customer."
          />
          {searchedProduct && (
            <SlipLines
              title={`Bought with ${searchedProduct}`}
              items={result.frequently_bought_with || []}
              empty="No matching product associations."
            />
          )}
        </div>
      )}

      <div aria-hidden="true" className="my-4 border-t border-dashed border-stone-400" />
      <div className="flex items-end justify-between gap-4">
        <p className="text-stone-500">
          {result ? `${count} ${count === 1 ? "suggestion" : "suggestions"}` : "Ready"}
        </p>
        <Barcode seed={result?.customer_id ?? "0000"} />
      </div>
    </div>
  );
}

export function RecommendationsPanel({ token, onSessionExpired }) {
  const [customerId, setCustomerId] = useState("17850");
  const [currentProduct, setCurrentProduct] = useState("");
  const [result, setResult] = useState(null);
  const [searchedProduct, setSearchedProduct] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const idInvalid = !/^\d+$/.test(customerId.trim());

  async function handleSubmit(event) {
    event.preventDefault();
    if (idInvalid) {
      setError("Enter a numeric customer ID, e.g. 17850.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const params = new URLSearchParams({ customer_id: customerId.trim() });
      if (currentProduct.trim()) params.set("current_product", currentProduct.trim());
      const data = await apiRequest(`/recommendations?${params.toString()}`, token);
      setResult(data);
      setSearchedProduct(currentProduct.trim());
    } catch (err) {
      if (err.status === 401) onSessionExpired?.();
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader
        title="Product recommendations"
        description="Look up a customer and see what to put in front of them next"
      />
      <CardBody className="grid items-start gap-8 lg:grid-cols-[minmax(0,20rem)_1fr]">
        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <Field
            label="Customer ID"
            htmlFor="rec-customer-id"
            error={error && idInvalid ? error : undefined}
          >
            <Input
              id="rec-customer-id"
              inputMode="numeric"
              placeholder="e.g. 17850"
              value={customerId}
              invalid={Boolean(error) && idInvalid}
              onChange={(event) => setCustomerId(event.target.value)}
            />
          </Field>
          <Field
            label="Current product (optional)"
            htmlFor="rec-current-product"
            hint="Exact product name. Adds what other shoppers bought with it."
          >
            <Input
              id="rec-current-product"
              placeholder="Exact product name"
              value={currentProduct}
              onChange={(event) => setCurrentProduct(event.target.value)}
            />
          </Field>
          <Button type="submit" icon={Wand2} loading={loading} className="w-full sm:w-auto">
            {loading ? "Printing basket…" : "Get recommendations"}
          </Button>
          {error && !idInvalid && <Alert variant="error">{error}</Alert>}
        </form>

        <Slip loading={loading} result={result} searchedProduct={searchedProduct} />
      </CardBody>
    </Card>
  );
}

/* ------------------------------------------------------------------ */
/* Churn risk: a watchlist with signal-strength meters                 */
/* ------------------------------------------------------------------ */

const LIT = {
  high: "bg-rose-500",
  medium: "bg-amber-500",
  low: "bg-emerald-500",
  neutral: "bg-slate-400",
};

function RiskMeter({ probability, tone }) {
  const p = Math.min(Math.max(Number(probability) || 0, 0), 1);
  const lit = Math.round(p * 20);
  return (
    <div
      role="img"
      aria-label={`${formatPercent(p * 100)} churn probability`}
      className="flex items-end gap-[2px]"
    >
      {Array.from({ length: 20 }, (_, i) => (
        <span
          key={i}
          className={cn(
            "w-[3px] rounded-[1px]",
            i < lit ? LIT[tone] : "bg-slate-200 dark:bg-white/10",
          )}
          style={{ height: 6 + i * 0.6 }}
        />
      ))}
    </div>
  );
}

const SPLIT = [
  { key: "High Risk", label: "High", bar: "bg-rose-500", dot: "bg-rose-500" },
  { key: "Medium Risk", label: "Medium", bar: "bg-amber-500", dot: "bg-amber-500" },
  { key: "Low Risk", label: "Low", bar: "bg-emerald-500", dot: "bg-emerald-500" },
];

export function ChurnPanel({ churn, loading }) {
  const rows = useMemo(() => (Array.isArray(churn?.customers) ? churn.customers : []), [churn]);
  const ok = churn && !churn.error;

  const riskFilter = useMemo(() => {
    const levels = [...new Set(rows.map((r) => r.retention_risk).filter(Boolean))];
    return {
      id: "risk",
      label: "risk levels",
      options: levels.map((l) => ({ value: l, label: l })),
      predicate: (row, value) => row.retention_risk === value,
    };
  }, [rows]);

  const segmentFilter = useMemo(() => {
    const names = [...new Set(rows.map((r) => r.segment || "Unassigned"))].sort();
    return {
      id: "segment",
      label: "segments",
      options: names.map((n) => ({ value: n, label: n })),
      predicate: (row, value) => (row.segment || "Unassigned") === value,
    };
  }, [rows]);

  const summary = ok ? churn.risk_summary : null;
  const counts = summary ? SPLIT.map((s) => Number(summary[s.key] || 0)) : [];
  const total = counts.reduce((a, b) => a + b, 0);

  return (
    <Card>
      <CardHeader
        icon={UserMinus}
        title="Customer churn risk"
        description="Who is most likely to stop buying, highest first"
        actions={
          ok && (
            <>
              <Badge tone="neutral">{formatNumber(churn.total_customers)} customers</Badge>
              {churn.model_used && <Badge tone="brand">Model: {churn.model_used}</Badge>}
            </>
          )
        }
      />

      {!churn && loading && (
        <CardBody aria-busy="true" className="space-y-3">
          <Skeleton className="h-14 w-full rounded-xl" />
          {Array.from({ length: 5 }, (_, i) => (
            <Skeleton key={i} className="h-9 w-full" />
          ))}
        </CardBody>
      )}

      {churn?.error && (
        <CardBody>
          <Alert variant="error" title="Churn predictions didn't load">
            {churn.error}
          </Alert>
        </CardBody>
      )}

      {summary && (
        <CardBody className="pb-5">
          <div className="flex flex-wrap items-end gap-x-10 gap-y-5">
            <div>
              <p className="text-5xl font-bold tabular-nums tracking-tight text-slate-900 dark:text-white">
                {formatNumber(counts[0])}
              </p>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                customers at high risk of leaving
              </p>
            </div>
            <div className="min-w-[16rem] flex-1">
              <div
                role="img"
                aria-label={SPLIT.map((s, i) => `${s.label} ${counts[i]}`).join(", ")}
                className="flex h-3 gap-0.5 overflow-hidden rounded-full"
              >
                {SPLIT.map((s, i) =>
                  counts[i] > 0 ? (
                    <span
                      key={s.key}
                      className={cn("h-full", s.bar)}
                      style={{ width: `${(counts[i] / total) * 100}%` }}
                    />
                  ) : null,
                )}
              </div>
              <ul className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-sm">
                {SPLIT.map((s, i) => (
                  <li key={s.key} className="inline-flex items-center gap-2">
                    <span aria-hidden="true" className={cn("size-2 rounded-full", s.dot)} />
                    <span className="font-semibold tabular-nums text-slate-900 dark:text-white">
                      {formatNumber(counts[i])}
                    </span>
                    <span className="text-slate-500 dark:text-slate-400">
                      {s.label.toLowerCase()} risk
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </CardBody>
      )}

      {ok && (
        <>
          <DataTable
            rows={rows}
            rowKey={(row) => row.CustomerID}
            defaultSort={{ key: "churn_probability", dir: "desc" }}
            searchPlaceholder="Search customer ID"
            searchText={(row) => String(row.CustomerID)}
            filters={[riskFilter, segmentFilter]}
            emptyTitle="No churn predictions yet"
            emptyDescription="Predictions will appear here once the model has scored your customers."
            columns={[
              {
                key: "CustomerID",
                header: "Customer",
                cell: (row) => (
                  <span className="font-semibold text-slate-900 dark:text-white">
                    {row.CustomerID}
                  </span>
                ),
              },
              {
                key: "churn_probability",
                header: "Churn probability",
                sortValue: (row) => Number(row.churn_probability),
                cell: (row) => (
                  <div className="flex items-center gap-3">
                    <RiskMeter
                      probability={row.churn_probability}
                      tone={riskTone(row.retention_risk)}
                    />
                    <span className="w-14 font-medium tabular-nums">
                      {formatPercent(Number(row.churn_probability) * 100)}
                    </span>
                  </div>
                ),
              },
              {
                key: "retention_risk",
                header: "Risk",
                sortValue: (row) =>
                  ({ high: 0, medium: 1, low: 2, neutral: 3 })[riskTone(row.retention_risk)],
                cell: (row) => <RiskBadge level={row.retention_risk} />,
              },
              {
                key: "segment",
                header: "Segment",
                sortValue: (row) => row.segment || "Unassigned",
                cell: (row) => row.segment || "Unassigned",
              },
            ]}
          />
          {churn.total_customers > 100 && (
            <p className="border-t border-slate-200 px-5 py-3 text-xs text-slate-500 dark:border-white/10 dark:text-slate-400 sm:px-6">
              Showing the 100 customers with the highest predicted churn probability.
            </p>
          )}
        </>
      )}
    </Card>
  );
}

/* ------------------------------------------------------------------ */
/* Anomaly alerts: a severity-ruled log instead of a table             */
/* ------------------------------------------------------------------ */

const RULE = {
  high: "border-rose-500",
  medium: "border-amber-400",
  low: "border-emerald-500",
  neutral: "border-slate-300 dark:border-white/20",
};

const PAGE = 15;

export function AlertsPanel({ anomalies, loading }) {
  const [severity, setSeverity] = useState("all");
  const [query, setQuery] = useState("");
  const [shown, setShown] = useState(PAGE);

  const rows = useMemo(
    () => (Array.isArray(anomalies?.alerts) ? anomalies.alerts : []),
    [anomalies],
  );
  const ok = anomalies && !anomalies.error;

  const levels = useMemo(() => {
    const counts = new Map();
    rows.forEach((r) => counts.set(String(r.severity), (counts.get(String(r.severity)) ?? 0) + 1));
    return [...counts.entries()];
  }, [rows]);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows.filter((r) => {
      if (severity !== "all" && String(r.severity) !== severity) return false;
      return (
        !q ||
        `${r.store_id} ${r.product_id} ${r.detected_by} ${r.message}`.toLowerCase().includes(q)
      );
    });
  }, [rows, severity, query]);

  const high = Number(anomalies?.high_severity || 0);
  const medium = Number(anomalies?.medium_severity || 0);
  const totalAlerts = Number(anomalies?.total_alerts || 0);
  const other = Math.max(totalAlerts - high - medium, 0);

  return (
    <Card>
      <CardHeader
        icon={BellRing}
        title="Sales and inventory alerts"
        description="Unusual sales or stock patterns, most serious first"
      />

      {!anomalies && loading && (
        <CardBody aria-busy="true" className="space-y-3">
          <Skeleton className="h-14 w-full rounded-xl" />
          {Array.from({ length: 4 }, (_, i) => (
            <Skeleton key={i} className="h-14 w-full" />
          ))}
        </CardBody>
      )}

      {anomalies?.error && (
        <CardBody>
          <Alert variant="error" title="Alerts didn't load">
            {anomalies.error}
          </Alert>
        </CardBody>
      )}

      {ok && (
        <>
          <CardBody className="pb-4">
            <div className="flex flex-wrap items-end gap-x-10 gap-y-4">
              <div>
                <p className="text-5xl font-bold tabular-nums tracking-tight text-slate-900 dark:text-white">
                  {formatNumber(totalAlerts)}
                </p>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  alerts flagged, {formatNumber(high)} high severity
                </p>
              </div>
              {totalAlerts > 0 && (
                <div
                  role="img"
                  aria-label={`${high} high, ${medium} medium, ${other} other`}
                  className="flex h-3 min-w-[16rem] flex-1 gap-0.5 overflow-hidden rounded-full"
                >
                  {high > 0 && <span className="bg-rose-500" style={{ width: `${(high / totalAlerts) * 100}%` }} />}
                  {medium > 0 && <span className="bg-amber-400" style={{ width: `${(medium / totalAlerts) * 100}%` }} />}
                  {other > 0 && <span className="bg-slate-300 dark:bg-white/20" style={{ width: `${(other / totalAlerts) * 100}%` }} />}
                </div>
              )}
            </div>
          </CardBody>

          <div className="flex flex-wrap items-center gap-3 border-y border-slate-200 px-5 py-3 dark:border-white/10 sm:px-6">
            <div
              role="radiogroup"
              aria-label="Filter by severity"
              className="flex gap-1 rounded-lg bg-slate-100 p-0.5 dark:bg-white/5"
            >
              {[["all", rows.length], ...levels].map(([level, count]) => {
                const selected = severity === level;
                return (
                  <button
                    key={level}
                    type="button"
                    role="radio"
                    aria-checked={selected}
                    onClick={() => {
                      setSeverity(level);
                      setShown(PAGE);
                    }}
                    className={cn(
                      "rounded-md px-3 py-1 text-xs font-semibold capitalize transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500",
                      selected
                        ? "bg-white text-slate-900 shadow-sm dark:bg-slate-700 dark:text-white"
                        : "text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white",
                    )}
                  >
                    {level === "all" ? "All" : level}{" "}
                    <span className="tabular-nums opacity-60">{count}</span>
                  </button>
                );
              })}
            </div>
            <div className="min-w-[12rem] flex-1 sm:max-w-xs">
              <Input
                icon={Search}
                type="search"
                className="h-9"
                placeholder="Search store, product or details"
                aria-label="Search alerts"
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setShown(PAGE);
                }}
              />
            </div>
          </div>

          {visible.length === 0 ? (
            <p className="px-6 py-12 text-center text-sm text-slate-500 dark:text-slate-400">
              {rows.length === 0
                ? "No alerts right now. Anything unusual will show up here."
                : "No alerts match that search."}
            </p>
          ) : (
            <ul className="divide-y divide-slate-100 px-5 dark:divide-white/5 sm:px-6">
              {visible.slice(0, shown).map((row) => (
                <li
                  key={row.row_id}
                  className={cn(
                    "my-3 grid gap-x-4 gap-y-1 border-l-[3px] py-1 pl-4 sm:grid-cols-[1fr_auto]",
                    RULE[riskTone(row.severity)],
                  )}
                >
                  <div className="min-w-0">
                    <p className="flex flex-wrap items-center gap-x-2 text-sm">
                      <span className="font-semibold text-slate-900 dark:text-white">
                        {row.product_id}
                      </span>
                      <span className="text-slate-500 dark:text-slate-400">
                        in store {row.store_id}
                      </span>
                    </p>
                    <p className="mt-0.5 text-sm text-slate-600 dark:text-slate-300">
                      {row.message}
                    </p>
                    <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                      Detected by {row.detected_by}
                    </p>
                  </div>
                  <div className="flex items-center gap-3 sm:flex-col sm:items-end sm:gap-1.5">
                    <RiskBadge level={row.severity} />
                    <span className="text-xs tabular-nums text-slate-500 dark:text-slate-400">
                      {formatDate(row.date)}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}

          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 px-5 py-3 text-xs text-slate-500 dark:border-white/10 dark:text-slate-400 sm:px-6">
            <p aria-live="polite">
              Showing {formatNumber(Math.min(shown, visible.length))} of {formatNumber(visible.length)}
              {totalAlerts > 100 && " (top 100 by priority, high severity first)"}
            </p>
            {visible.length > shown && (
              <Button variant="secondary" size="sm" onClick={() => setShown((n) => n + PAGE)}>
                Show {Math.min(PAGE, visible.length - shown)} more
              </Button>
            )}
          </div>
        </>
      )}
    </Card>
  );
}

/* ------------------------------------------------------------------ */
/* Drop-in version: same props as before, loads its own data           */
/* ------------------------------------------------------------------ */

export default function M3Panels({ token, role, onSessionExpired }) {
  const { churn, anomalies, loading } = useInsights({
    token,
    role,
    onSessionExpired,
    reloadKey: 0,
  });

  if (!["owner", "admin", "store_manager"].includes(role)) return null;

  return (
    <div className="space-y-5">
      <RecommendationsPanel token={token} onSessionExpired={onSessionExpired} />
      {(role === "owner" || role === "admin") && <ChurnPanel churn={churn} loading={loading} />}
      <AlertsPanel anomalies={anomalies} loading={loading} />
    </div>
  );
}
