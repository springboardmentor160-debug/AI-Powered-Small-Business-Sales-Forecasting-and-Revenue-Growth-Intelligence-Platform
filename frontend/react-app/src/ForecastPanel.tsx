import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  AlertCircle,
  BarChart3,
  CheckCircle2,
  LoaderCircle,
  TrendingUp,
} from "lucide-react";
import {
  ApiRequestError,
  getDemandForecast,
  getRevenueForecast,
  getForecastModelComparison,
  type DemandForecast,
  type RevenueForecast,
  type ForecastModelComparison,
  type ForecastModel,
} from "./lib/api";

interface ForecastPanelProps {
  token: string;
}

function formatNumber(value: unknown): string {
  const number = Number(value);

  return value !== null &&
    value !== undefined &&
    value !== "" &&
    Number.isFinite(number)
    ? number.toLocaleString(undefined, { maximumFractionDigits: 2 })
    : "N/A";
}

function bestModel(models: ForecastModel[]): ForecastModel | undefined {
  return models
    .filter((model) => Number.isFinite(Number(model.mae)))
    .reduce<ForecastModel | undefined>(
      (best, model) =>
        !best || Number(model.mae) < Number(best.mae) ? model : best,
      undefined,
    );
}

function ModelList({
  title,
  models,
}: {
  title: string;
  models: ForecastModel[];
}) {
  if (models.length === 0) {
    return (
      <div className="forecast-subsection">
        <h4>{title}</h4>
        <p>No model metrics are available.</p>
      </div>
    );
  }

  return (
    <div className="forecast-subsection">
      <h4>{title}</h4>
      <div className="forecast-table-wrap">
        <table className="forecast-table">
          <thead>
            <tr>
              <th>Model</th>
              <th>MAE</th>
              <th>RMSE</th>
            </tr>
          </thead>
          <tbody>
            {models.map((model, index) => (
              <tr key={`${model.model}-${index}`}>
                <td>{model.model}</td>
                <td>{formatNumber(model.mae)}</td>
                <td>{formatNumber(model.rmse)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}


function errorMessage(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 403) {
      return "Your account role does not have permission to view forecasts.";
    }

    if (error.status === 404) {
      return "Forecast artifacts are not available at the configured location.";
    }

    return error.message;
  }

  return "Unable to load this forecast. Check the backend and try again.";
}

type ChartPoint = {
  date: string;
  [key: string]: string | number;
};

function ModelMetricsChart({
  title,
  models,
  metric,
}: {
  title: string;
  models: ForecastModel[];
  metric: "mae" | "rmse";
}) {
  const data = models
    .filter((model) => Number.isFinite(Number(model[metric])))
    .map((model) => ({
      model: model.model,
      value: Number(model[metric]),
    }));

  if (data.length === 0) {
    return (
      <div className="forecast-subsection">
        <h4>{title}</h4>
        <p>No metric data is available.</p>
      </div>
    );
  }

  const best = Math.min(...data.map((entry) => entry.value));
  return (
    <div className="forecast-subsection">
      <h4>{title}</h4>
      <div style={{ width: "100%", height: 340 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 10, right: 20, left: 10, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1B3E46" />
            <XAxis dataKey="model" tick={{ fontSize: 11 }} />
            <YAxis
              tick={{ fontSize: 11 }}
              tickFormatter={(value: number) =>
                value.toLocaleString(undefined, {
                  notation: "compact",
                  maximumFractionDigits: 1,
                })
              }
            />
            <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "rgba(0,163,169,.08)" }}
              formatter={(value) => [
                Number(value).toLocaleString(undefined, {
                  maximumFractionDigits: 2,
                }),
                metric.toUpperCase(),
              ]}
            />
            <Bar dataKey="value" name={metric.toUpperCase()} radius={[8, 8, 0, 0]} animationDuration={900}>
              {data.map((entry) => (
                <Cell key={entry.model} fill={entry.value === best ? "#00A3A9" : "#2C5560"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function ForecastLineChart({
  title,
  data,
  lines,
  valueLabel,
}: {
  title: string;
  data: ChartPoint[];
  lines: { key: string; label: string }[];
  valueLabel: string;
}) {
  if (data.length === 0) {
    return (
      <div className="forecast-subsection">
        <h4>{title}</h4>
        <p>No prediction data is available for this chart.</p>
      </div>
    );
  }

  return (
    <div className="forecast-subsection">
      <h4>{title}</h4>
      <div style={{ width: "100%", height: 320 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 10, right: 20, left: 10, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1B3E46" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={30} />
            <YAxis
              tick={{ fontSize: 11 }}
              tickFormatter={(value: number) =>
                value.toLocaleString(undefined, {
                  notation: "compact",
                  maximumFractionDigits: 1,
                })
              }
            />
            <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "rgba(0,163,169,.08)" }}
              formatter={(value) => [
                Number(value).toLocaleString(undefined, {
                  maximumFractionDigits: 2,
                }),
                valueLabel,
              ]}
            />
            <Legend />
            {lines.map((line, lineIndex) => (
              <Line
                key={line.key}
                type="monotone"
                dataKey={line.key}
                name={line.label}
                stroke={LINE_COLORS[lineIndex % LINE_COLORS.length]}
                animationDuration={1100}
                strokeWidth={2}
                dot={false}
                connectNulls={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

const LINE_COLORS = ["#F2FBFC", "#00A3A9", "#FFC857", "#FF8E8E"];
const TOOLTIP_STYLE = {
  background: "#0D1F25",
  border: "1px solid #1B3E46",
  borderRadius: 10,
  color: "#EAF6F7",
  boxShadow: "0 12px 30px rgba(0,0,0,.5)",
};

export default function ForecastPanel({ token }: ForecastPanelProps) {
  const [demand, setDemand] = useState<DemandForecast | null>(null);
  const [revenue, setRevenue] = useState<RevenueForecast | null>(null);
  const [comparison, setComparison] =
    useState<ForecastModelComparison | null>(null);

  const [demandError, setDemandError] = useState("");
  const [revenueError, setRevenueError] = useState("");
  const [comparisonError, setComparisonError] = useState("");

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadForecasts() {
      setLoading(true);
      setDemandError("");
      setRevenueError("");
      setComparisonError("");
      setDemand(null);
      setRevenue(null);
      setComparison(null);

      const results = await Promise.allSettled([
        getDemandForecast(token),
        getRevenueForecast(token),
        getForecastModelComparison(token),
      ]);

      if (cancelled) return;

      const [demandResult, revenueResult, comparisonResult] = results;

      if (demandResult.status === "fulfilled") {
        setDemand(demandResult.value);
      } else {
        setDemandError(errorMessage(demandResult.reason));
      }

      if (revenueResult.status === "fulfilled") {
        setRevenue(revenueResult.value);
      } else {
        setRevenueError(errorMessage(revenueResult.reason));
      }

      if (comparisonResult.status === "fulfilled") {
        setComparison(comparisonResult.value);
      } else {
        setComparisonError(errorMessage(comparisonResult.reason));
      }

      setLoading(false);
    }

    void loadForecasts();

    return () => {
      cancelled = true;
    };
  }, [token]);

  const demandBest = demand ? bestModel(demand.models) : undefined;
  const revenueBest = revenue ? bestModel(revenue.models) : undefined;

  return (
    <article className="feature-card forecast-card">
      <span className="feature-icon blue">
        <BarChart3 size={22} />
      </span>

      <h3>Forecast intelligence</h3>
      <p>
        Model evaluation and prediction outputs from the connected forecasting
        APIs.
      </p>

      {loading ? (
        <p className="forecast-state">
          <LoaderCircle size={17} className="forecast-spinner" />
          Loading forecast results...
        </p>
      ) : (
        <>
          <section className="forecast-section">
            <h4>
              <TrendingUp size={16} /> Demand forecasting
            </h4>

            {demandError ? (
              <p className="forecast-error" role="alert">
                <AlertCircle size={16} />
                {demandError}
              </p>
            ) : demand ? (
              <>
                <p className="forecast-feature-name">{demand.feature}</p>
                <div className="forecast-stats">
                  <div>
                    <span>Validation horizon</span>
                    <strong>{demand.validation_horizon_days} days</strong>
                  </div>
                  <div>
                    <span>Prediction records</span>
                    <strong>{demand.predictions?.length ?? 0}</strong>
                  </div>
                  <div>
                    <span>Validation period</span>
                    <strong>
                      {demand.validation_start || "N/A"} –{" "}
                      {demand.validation_end || "N/A"}
                    </strong>
                  </div>
                </div>

                {demandBest && (
                  <p className="forecast-best">
                    <CheckCircle2 size={16} />
                    Lowest reported MAE: <b>{demandBest.model}</b>
                    {" · "}MAE {formatNumber(demandBest.mae)}
                  </p>
                )}

                <ModelList title="Demand model metrics" models={demand.models} />

<ForecastLineChart
  title="Actual vs. predicted demand"
  data={(demand.predictions ?? [])
    .filter(
      (point) =>
        point.date &&
        Number.isFinite(Number(point.actual_units)) &&
        Number.isFinite(Number(point.predicted_units)),
    )
    .map((point) => ({
      date: point.date!,
      actual_units: Number(point.actual_units),
      predicted_units: Number(point.predicted_units),
    }))}
  lines={[
    { key: "actual_units", label: "Actual units" },
    { key: "predicted_units", label: "Predicted units" },
  ]}
  valueLabel="Units"
/>

              </>
            ) : null}
          </section>

          <section className="forecast-section">
            <h4>
              <TrendingUp size={16} /> Revenue forecasting
            </h4>

            {revenueError ? (
              <p className="forecast-error" role="alert">
                <AlertCircle size={16} />
                {revenueError}
              </p>
            ) : revenue ? (
              <>
                <p className="forecast-feature-name">{revenue.feature}</p>
                <div className="forecast-stats">
                  <div>
                    <span>Prediction records</span>
                    <strong>{revenue.predictions?.length ?? 0}</strong>
                  </div>
                  <div>
                    <span>Test rows</span>
                    <strong>{revenue.validation?.test_rows ?? "N/A"}</strong>
                  </div>
                  <div>
                    <span>Validation period</span>
                    <strong>
                      {revenue.validation?.test_start || "N/A"} –{" "}
                      {revenue.validation?.test_end || "N/A"}
                    </strong>
                  </div>
                </div>

                {revenueBest && (
                  <p className="forecast-best">
                    <CheckCircle2 size={16} />
                    Lowest reported MAE: <b>{revenueBest.model}</b>
                    {" · "}MAE {formatNumber(revenueBest.mae)}
                  </p>
                )}

                <ModelList
                  title="Revenue model metrics"
                  models={revenue.models}
                />
                <ForecastLineChart
                  title="Actual vs. predicted revenue"
                  data={(revenue.predictions ?? [])
                    .filter(
                      (point) =>
                        point.date &&
                        Number.isFinite(Number(point.actual_revenue)) &&
                        (
                          Number.isFinite(Number(point.prophet_prediction)) ||
                          Number.isFinite(Number(point.random_forest_prediction)) ||
                          Number.isFinite(Number(point.xgboost_prediction))
                        ),
                    )
                    .map((point) => ({
                      date: point.date!,
                      actual_revenue: Number(point.actual_revenue),
                      prophet_prediction: Number(point.prophet_prediction),
                      random_forest_prediction: Number(point.random_forest_prediction),
                      xgboost_prediction: Number(point.xgboost_prediction),
                    }))}
                  lines={[
                    { key: "actual_revenue", label: "Actual revenue" },
                    { key: "prophet_prediction", label: "Prophet" },
                    { key: "random_forest_prediction", label: "Random Forest" },
                    { key: "xgboost_prediction", label: "XGBoost" },
                  ]}
                  valueLabel="Revenue"
                />
              </>
            ) : null}
          </section>

          <section className="forecast-section">
            <h4>Cross-task model comparison</h4>

            {comparisonError ? (
              <p className="forecast-error" role="alert">
                <AlertCircle size={16} />
                {comparisonError}
              </p>
            ) : comparison ? (
              <>
                <ModelList
                  title="UCI revenue models"
                  models={comparison.uci_revenue_models}
                />
                <ModelList
                  title="M5 demand models"
                  models={comparison.m5_demand_models}
                />
                <ModelMetricsChart
                  title="Revenue model MAE comparison"
                  models={comparison.uci_revenue_models}
                  metric="mae"
                />
                <ModelMetricsChart
                  title="Revenue model RMSE comparison"
                  models={comparison.uci_revenue_models}
                  metric="rmse"
                />
                <ModelMetricsChart
                  title="Demand model MAE comparison"
                  models={comparison.m5_demand_models}
                  metric="mae"
                />
                <ModelMetricsChart
                  title="Demand model RMSE comparison"
                  models={comparison.m5_demand_models}
                  metric="rmse"
                />

              </>
            ) : null}
          </section>
        </>
      )}

      <p className="forecast-footnote">
        MAE and RMSE are evaluation metrics, not guaranteed future performance.
        The lowest MAE alone does not establish that a model is best for every
        business objective.
      </p>
    </article>
  );
}