import { useMemo } from "react";
import {
  AlertTriangle,
  BarChart3,
  BellRing,
  Boxes,
  CheckCircle2,
  Gauge,
  LayoutDashboard,
  Receipt,
  ShieldAlert,
  ShoppingBag,
  UserMinus,
  Users,
  Wallet,
} from "lucide-react";
import AreaChart from "../components/charts/AreaChart";
import BarList from "../components/charts/BarList";
import Donut from "../components/charts/Donut";
import StatCard from "../components/StatCard";
import Badge from "../components/ui/Badge";
import Button from "../components/ui/Button";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import { buildUnitsSeries, computeTrend } from "../lib/analytics";
import { formatCurrency, formatDate, formatNumber } from "../lib/format";

const LOW_STOCK_LEVEL = 100;
const KPI_ROLES = ["owner", "admin", "store_manager"];

export default function OverviewView({
  role,
  summary,
  salesData,
  myTransactions,
  segments,
  forecast,
  churn,
  anomalies,
  loading,
  insightsLoading,
  onNavigate,
}) {
  const series = useMemo(() => buildUnitsSeries(salesData), [salesData]);
  const trend = useMemo(() => computeTrend(series), [series]);
  const sparkValues = useMemo(() => series.map((d) => d.value), [series]);

  const showKpis = KPI_ROLES.includes(role);
  const isExec = role === "sales_exec";
  const hasChart = series.length >= 2;
  const churnOk = churn && !churn.error && churn.risk_summary;

  const stores = new Set(salesData.map((r) => r.store_id)).size;
  const products = new Set(salesData.map((r) => r.product_id)).size;
  const lowStock =
    summary?.low_stock_count ?? salesData.filter((r) => r.inventory_level < LOW_STOCK_LEVEL).length;

  const execStats = useMemo(
    () => ({
      revenue: myTransactions.reduce((sum, r) => sum + Number(r.total_amount || 0), 0),
      count: myTransactions.length,
      customers: new Set(myTransactions.map((r) => r.customer_id)).size,
    }),
    [myTransactions],
  );

  const attention = [];
  if (showKpis && Number(lowStock) > 0) {
    attention.push({
      id: "stock",
      icon: Boxes,
      tone: "warning",
      title: `${formatNumber(lowStock)} items running low`,
      text: `Below the ${LOW_STOCK_LEVEL}-unit reorder level.`,
      to: "data",
      cta: "Review stock",
    });
  }
  const highAlerts = anomalies && !anomalies.error ? Number(anomalies.high_severity || 0) : 0;
  if (highAlerts > 0) {
    attention.push({
      id: "alerts",
      icon: ShieldAlert,
      tone: "danger",
      title: `${formatNumber(highAlerts)} high-severity ${highAlerts === 1 ? "alert" : "alerts"}`,
      text: "Unusual sales or inventory patterns were detected.",
      to: "alerts",
      cta: "View alerts",
    });
  }
  const highRisk = churnOk ? Number(churn.risk_summary["High Risk"] || 0) : 0;
  if (highRisk > 0) {
    attention.push({
      id: "churn",
      icon: UserMinus,
      tone: "danger",
      title: `${formatNumber(highRisk)} customers likely to leave`,
      text: "Flagged as high churn risk.",
      to: "customers",
      cta: "See customers",
    });
  }

  const showAttention = showKpis;
  const attentionLoading = (loading || insightsLoading) && attention.length === 0;
  const hasAnything =
    showKpis || isExec || hasChart || forecast || segments.length > 0 || churnOk;

  if (!hasAnything && !loading) {
    return (
      <Card>
        <EmptyState
          icon={LayoutDashboard}
          title="No overview data yet"
          description="Once sales data is available for your account, trends and forecasts will appear here."
        />
      </Card>
    );
  }

  return (
    <div className="space-y-5">
      {showKpis && (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <StatCard
            label="Total units sold"
            icon={ShoppingBag}
            tone="indigo"
            loading={loading && !summary}
            value={summary ? formatNumber(summary.total_units_sold) : "—"}
            trend={trend}
            trendLabel="vs earlier period"
            hint="Across all stores"
            series={sparkValues}
            info="Trend compares units sold in the latest half of the dates in your data with the earlier half."
          />
          <StatCard
            label="Total inventory"
            icon={Boxes}
            tone="sky"
            loading={loading && !summary}
            value={summary ? formatNumber(summary.total_inventory) : "—"}
            hint={
              stores > 0
                ? `Across ${formatNumber(stores)} ${stores === 1 ? "store" : "stores"} and ${formatNumber(products)} ${products === 1 ? "product" : "products"}`
                : "Units currently in stock"
            }
          />
          <StatCard
            label="Low stock items"
            icon={AlertTriangle}
            tone="amber"
            loading={loading && !summary}
            value={summary ? formatNumber(summary.low_stock_count) : "—"}
            hint={`Below ${LOW_STOCK_LEVEL} units in stock`}
            info="Items under the reorder level. These are the next to sell out."
          />
        </div>
      )}

      {isExec && (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <StatCard
            label="Revenue from your customers"
            icon={Wallet}
            tone="emerald"
            loading={loading && myTransactions.length === 0}
            value={formatCurrency(execStats.revenue)}
            hint="Total of the transactions listed"
          />
          <StatCard
            label="Transactions"
            icon={Receipt}
            tone="indigo"
            loading={loading && myTransactions.length === 0}
            value={formatNumber(execStats.count)}
            hint="Assigned to you"
          />
          <StatCard
            label="Customers"
            icon={Users}
            tone="sky"
            loading={loading && myTransactions.length === 0}
            value={formatNumber(execStats.customers)}
            hint="Unique customers served"
          />
        </div>
      )}

      {(hasChart || forecast || (loading && series.length === 0)) && (
        <div className="grid gap-5 lg:grid-cols-3">
          {(hasChart || (loading && series.length === 0)) && (
            <Card className={forecast || (loading && !hasChart) ? "lg:col-span-2" : "lg:col-span-3"}>
              <CardHeader
                icon={BarChart3}
                title="Units sold over time"
                description={
                  hasChart
                    ? `${formatDate(series[0].label)} to ${formatDate(series[series.length - 1].label)}`
                    : "Daily units sold across all stores"
                }
                actions={
                  trend && (
                    <Badge tone={trend.value >= 0 ? "success" : "danger"} dot>
                      {trend.value >= 0 ? "Trending up" : "Trending down"}
                    </Badge>
                  )
                }
              />
              <CardBody>
                {hasChart ? (
                  <AreaChart
                    data={series}
                    valueLabel="Units sold"
                    formatValue={formatNumber}
                    formatLabel={(label, full) =>
                      full
                        ? formatDate(label)
                        : formatDate(label, { year: undefined })
                    }
                  />
                ) : (
                  <Skeleton className="h-[260px] w-full rounded-xl" />
                )}
              </CardBody>
            </Card>
          )}

          {forecast && (
            <section
              aria-label="Sales forecast"
              className="relative flex flex-col justify-between overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 via-indigo-600 to-violet-700 p-6 text-white shadow-lg shadow-indigo-600/20"
            >
              <div
                aria-hidden="true"
                className="pointer-events-none absolute -right-16 -top-16 size-56 rounded-full bg-white/10 blur-2xl"
              />
              <div className="relative">
                <div className="flex items-center justify-between gap-3">
                  <h2 className="text-sm font-semibold text-indigo-100">Sales forecast</h2>
                  {forecast.period && (
                    <span className="rounded-md bg-white/15 px-2 py-0.5 text-xs font-semibold ring-1 ring-inset ring-white/20">
                      {forecast.period}
                    </span>
                  )}
                </div>
                <p className="mt-6 text-sm text-indigo-100">Predicted revenue</p>
                <p className="mt-1 text-4xl font-bold tabular-nums tracking-tight sm:text-5xl">
                  {formatCurrency(forecast.predicted_revenue)}
                </p>
              </div>
              <div className="relative mt-8 flex items-center gap-2 text-sm text-indigo-100">
                <Gauge aria-hidden="true" className="size-4" />
                <span>
                  Model: <span className="font-semibold text-white">{forecast.model_used ?? "—"}</span>
                </span>
              </div>
            </section>
          )}
        </div>
      )}

      {(segments.length > 0 || churnOk || showAttention) && (
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {segments.length > 0 && (
            <Card>
              <CardHeader icon={Users} title="Customer segments" description="Customers per segment" />
              <CardBody>
                <BarList
                  items={segments.map((s) => ({ label: s.segment, value: Number(s.customer_count) || 0 }))}
                />
              </CardBody>
            </Card>
          )}

          {churnOk && (
            <Card>
              <CardHeader
                icon={UserMinus}
                title="Churn risk"
                description="Customers by likelihood of leaving"
                actions={
                  <Button variant="ghost" size="sm" onClick={() => onNavigate("customers")}>
                    Details
                  </Button>
                }
              />
              <CardBody>
                <Donut
                  centerLabel="Customers"
                  className="sm:flex-col sm:items-stretch xl:flex-row"
                  segments={[
                    { key: "high", label: "High risk", value: Number(churn.risk_summary["High Risk"] || 0), color: "#f43f5e" },
                    { key: "medium", label: "Medium risk", value: Number(churn.risk_summary["Medium Risk"] || 0), color: "#f59e0b" },
                    { key: "low", label: "Low risk", value: Number(churn.risk_summary["Low Risk"] || 0), color: "#10b981" },
                  ]}
                />
              </CardBody>
            </Card>
          )}

          {showAttention && (
            <Card className="md:col-span-2 xl:col-span-1">
              <CardHeader icon={BellRing} title="Needs attention" description="What to look at first" />
              <CardBody>
                {attentionLoading ? (
                  <div className="space-y-3">
                    <Skeleton className="h-16 w-full rounded-xl" />
                    <Skeleton className="h-16 w-full rounded-xl" />
                  </div>
                ) : attention.length === 0 ? (
                  <div className="flex items-center gap-3 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-200">
                    <CheckCircle2 aria-hidden="true" className="size-5 shrink-0" />
                    <p>All clear. No low stock, high-severity alerts or high churn risk right now.</p>
                  </div>
                ) : (
                  <ul className="space-y-3">
                    {attention.map((item) => {
                      const Icon = item.icon;
                      return (
                        <li
                          key={item.id}
                          className="flex items-center gap-3 rounded-xl border border-slate-200 p-3 dark:border-white/10"
                        >
                          <span
                            className={
                              item.tone === "danger"
                                ? "flex size-9 shrink-0 items-center justify-center rounded-lg bg-rose-50 text-rose-600 dark:bg-rose-500/10 dark:text-rose-300"
                                : "flex size-9 shrink-0 items-center justify-center rounded-lg bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-300"
                            }
                          >
                            <Icon aria-hidden="true" className="size-[18px]" />
                          </span>
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-semibold text-slate-900 dark:text-white">{item.title}</p>
                            <p className="text-xs text-slate-500 dark:text-slate-400">{item.text}</p>
                          </div>
                          <Button variant="secondary" size="sm" onClick={() => onNavigate(item.to)}>
                            {item.cta}
                          </Button>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </CardBody>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
