import { useCallback, useEffect, useState } from "react";
import { AlertCircle, RefreshCw, ShieldAlert } from "lucide-react";
import {
  ApiRequestError,
  getAnomalyAlerts,
  type AlertSeverity,
  type AlertType,
  type AnomalyOverview,
} from "./lib/api";

interface AnomalyPanelProps {
  token: string;
}

const TYPE_LABELS: Record<AlertType, string> = {
  unusual_sales_activity: "Unusual sales activity",
  stock_write_off: "Stock write-off",
  demand_spike: "Demand spike",
};

function formatNumber(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(Number(value))) return "N/A";
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export default function AnomalyPanel({ token }: AnomalyPanelProps) {
  const [data, setData] = useState<AnomalyOverview | null>(null);
  const [alertType, setAlertType] = useState<AlertType | "">("");
  const [severity, setSeverity] = useState<AlertSeverity | "">("high");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      setData(
        await getAnomalyAlerts(
          token,
          alertType || undefined,
          severity || undefined,
        ),
      );
    } catch (cause: unknown) {
      setError(
        cause instanceof ApiRequestError
          ? cause.message
          : "Unable to load anomaly alerts.",
      );
    } finally {
      setLoading(false);
    }
  }, [token, alertType, severity]);

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
          <p className="eyebrow">RISK MONITORING</p>
          <h2>
            <ShieldAlert size={22} /> Fraud and inventory alerts
          </h2>
          <p>
            Unusual orders, stock write-offs and demand spikes worth a second
            look. An alert is a prompt to check, not proof of fraud.
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

      {loading && <p>Loading alerts...</p>}

      {error && (
        <p className="segmentation-error" role="alert">
          <AlertCircle size={17} /> {error}
        </p>
      )}

      {data && !loading && (
        <>
          <div className="inventory-metrics">
            <article>
              <span>Total alerts</span>
              <strong>{formatNumber(data.total_alerts)}</strong>
            </article>
            <article>
              <span>High severity</span>
              <strong>{formatNumber(data.by_severity.high ?? 0)}</strong>
            </article>
            <article>
              <span>Unusual sales</span>
              <strong>
                {formatNumber(data.by_type.unusual_sales_activity ?? 0)}
              </strong>
            </article>
            <article>
              <span>Stock write-offs</span>
              <strong>{formatNumber(data.by_type.stock_write_off ?? 0)}</strong>
            </article>
            <article>
              <span>Demand spikes</span>
              <strong>{formatNumber(data.by_type.demand_spike ?? 0)}</strong>
            </article>
          </div>

          <div className="segmentation-section">
            <div className="m3-form">
              <label>
                Alert type
                <select
                  value={alertType}
                  onChange={(event) =>
                    setAlertType(event.target.value as AlertType | "")
                  }
                >
                  <option value="">All types</option>
                  {(Object.keys(TYPE_LABELS) as AlertType[]).map((type) => (
                    <option key={type} value={type}>
                      {TYPE_LABELS[type]}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Severity
                <select
                  value={severity}
                  onChange={(event) =>
                    setSeverity(event.target.value as AlertSeverity | "")
                  }
                >
                  <option value="">All</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                </select>
              </label>
            </div>

            <p className="segmentation-note">
              Showing {data.alerts.length} of {data.matching_alerts} matching
              alerts.
            </p>

            <div className="forecast-table-wrap">
              <table className="forecast-table">
                <thead>
                  <tr>
                    <th>Alert</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Date</th>
                    <th>Details</th>
                    <th>Detected by</th>
                  </tr>
                </thead>
                <tbody>
                  {data.alerts.map((alert) => (
                    <tr key={alert.alert_id}>
                      <td>{alert.alert_id}</td>
                      <td>{TYPE_LABELS[alert.alert_type]}</td>
                      <td>
                        <span
                          className={`risk-badge ${
                            alert.severity === "high"
                              ? "risk-high"
                              : "risk-medium"
                          }`}
                        >
                          {alert.severity}
                        </span>
                      </td>
                      <td>{alert.event_date}</td>
                      <td>{alert.message}</td>
                      <td>{alert.detected_by.replace(/_/g, " ")}</td>
                    </tr>
                  ))}
                  {data.alerts.length === 0 && (
                    <tr>
                      <td colSpan={6}>No alerts match this filter.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
