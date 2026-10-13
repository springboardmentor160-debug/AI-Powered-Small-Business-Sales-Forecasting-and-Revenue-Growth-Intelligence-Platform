import { useCallback, useEffect, useState } from "react";
import { AlertCircle, RefreshCw, UserMinus } from "lucide-react";
import {
  ApiRequestError,
  getChurnOverview,
  type ChurnOverview,
  type RetentionRisk,
} from "./lib/api";

interface ChurnPanelProps {
  token: string;
}

const RISK_LEVELS: RetentionRisk[] = ["High Risk", "Medium Risk", "Low Risk"];

function formatNumber(value: number | null | undefined, digits = 0): string {
  if (value == null || !Number.isFinite(Number(value))) return "N/A";
  return Number(value).toLocaleString(undefined, {
    maximumFractionDigits: digits,
  });
}

function riskClass(risk: RetentionRisk): string {
  return `risk-badge risk-${risk.split(" ")[0].toLowerCase()}`;
}

export default function ChurnPanel({ token }: ChurnPanelProps) {
  const [data, setData] = useState<ChurnOverview | null>(null);
  const [risk, setRisk] = useState<RetentionRisk | "">("High Risk");
  const [activeOnly, setActiveOnly] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      setData(await getChurnOverview(token, risk || undefined, activeOnly));
    } catch (cause: unknown) {
      setError(
        cause instanceof ApiRequestError
          ? cause.message
          : "Unable to load churn predictions.",
      );
    } finally {
      setLoading(false);
    }
  }, [token, risk, activeOnly]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => {
      if (active) void load();
    });
    return () => {
      active = false;
    };
  }, [load]);

  return (
    <section className="segmentation-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">CUSTOMER INTELLIGENCE</p>
          <h2>
            <UserMinus size={22} /> Churn risk
          </h2>
          <p>
            Probability that a customer makes no purchase in the next 90 days.
          </p>
        </div>

        <button
          type="button"
          className="button button-secondary"
          onClick={() => void load()}
          disabled={loading}
        >
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {loading && <p>Loading churn predictions...</p>}

      {error && (
        <p className="segmentation-error" role="alert">
          <AlertCircle size={17} /> {error}
        </p>
      )}

      {data && !loading && (
        <>
          <div className="inventory-metrics">
            {RISK_LEVELS.map((level) => (
              <article key={level}>
                <span>{level} (still ordering)</span>
                <strong>
                  {formatNumber(data.still_active_risk_counts[level])}
                </strong>
              </article>
            ))}
            <article>
              <span>Already silent 90+ days</span>
              <strong>
                {formatNumber(data.total_customers - data.still_active_customers)}
              </strong>
            </article>
          </div>

          <p className="segmentation-note">
            Model: {data.run_info.selected_model ?? "N/A"}. Trained on purchases
            before {data.run_info.snapshot_date ?? "N/A"} and tested on whether
            customers came back in the next 90 days.
            {data.run_info.xgboost_available === false &&
              " XGBoost was not installed when this run was produced."}
          </p>

          <div className="segmentation-section">
            <h3>Customers to contact first</h3>
            <div className="m3-form">
              <label>
                Risk level
                <select
                  value={risk}
                  onChange={(event) =>
                    setRisk(event.target.value as RetentionRisk | "")
                  }
                >
                  <option value="">All</option>
                  {RISK_LEVELS.map((level) => (
                    <option key={level} value={level}>
                      {level}
                    </option>
                  ))}
                </select>
              </label>
              <label className="m3-checkbox">
                <input
                  type="checkbox"
                  checked={activeOnly}
                  onChange={(event) => setActiveOnly(event.target.checked)}
                />
                Only customers who bought in the last 90 days
              </label>
            </div>

            <div className="forecast-table-wrap">
              <table className="forecast-table">
                <thead>
                  <tr>
                    <th>Customer ID</th>
                    <th>Risk</th>
                    <th>Churn probability</th>
                    <th>Days since last order</th>
                    <th>Orders</th>
                    <th>Avg. order value</th>
                    <th>Segment</th>
                  </tr>
                </thead>
                <tbody>
                  {data.customers.map((customer) => (
                    <tr key={customer["Customer ID"]}>
                      <td>{customer["Customer ID"]}</td>
                      <td>
                        <span className={riskClass(customer.retention_risk)}>
                          {customer.retention_risk}
                        </span>
                      </td>
                      <td>{(customer.churn_probability * 100).toFixed(1)}%</td>
                      <td>{formatNumber(customer.recency_days)}</td>
                      <td>{formatNumber(customer.frequency)}</td>
                      <td>{formatNumber(customer.avg_order_value, 2)}</td>
                      <td>{customer.segment_name}</td>
                    </tr>
                  ))}
                  {data.customers.length === 0 && (
                    <tr>
                      <td colSpan={7}>No customers match this filter.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="segmentation-section">
            <h3>Risk by customer segment</h3>
            <div className="forecast-table-wrap">
              <table className="forecast-table">
                <thead>
                  <tr>
                    <th>Segment</th>
                    <th>Customers</th>
                    <th>High</th>
                    <th>Medium</th>
                    <th>Low</th>
                    <th>% high risk</th>
                  </tr>
                </thead>
                <tbody>
                  {data.risk_by_segment.map((row) => (
                    <tr key={row.segment_name}>
                      <td>{row.segment_name}</td>
                      <td>{formatNumber(row.customers)}</td>
                      <td>{formatNumber(row["High Risk"])}</td>
                      <td>{formatNumber(row["Medium Risk"])}</td>
                      <td>{formatNumber(row["Low Risk"])}</td>
                      <td>{row.high_risk_pct}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="segmentation-section">
            <h3>Model comparison</h3>
            <p className="segmentation-note">
              A model that predicted &quot;nobody churns&quot; would be right{" "}
              {data.model_comparison[0]
                ? (data.model_comparison[0].lazy_model_accuracy * 100).toFixed(1)
                : "N/A"}
              % of the time, so precision and recall matter more than accuracy.
            </p>
            <div className="forecast-table-wrap">
              <table className="forecast-table">
                <thead>
                  <tr>
                    <th>Model</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1</th>
                    <th>ROC-AUC</th>
                  </tr>
                </thead>
                <tbody>
                  {data.model_comparison.map((row) => (
                    <tr key={row.model}>
                      <td>{row.model}</td>
                      <td>{row.precision.toFixed(2)}</td>
                      <td>{row.recall.toFixed(2)}</td>
                      <td>{row.f1.toFixed(2)}</td>
                      <td>{row.roc_auc.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
