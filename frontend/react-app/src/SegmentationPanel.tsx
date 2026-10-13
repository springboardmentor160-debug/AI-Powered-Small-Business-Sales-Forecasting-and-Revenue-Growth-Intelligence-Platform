import { useCallback, useEffect, useState } from "react";
import { AlertCircle, RefreshCw, Users } from "lucide-react";
import {
  ApiRequestError,
  getCustomerSegments,
  type CustomerSegments,
} from "./lib/api";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface SegmentationPanelProps {
  token: string;
}

function formatNumber(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(Number(value))) return "N/A";

  return Number(value).toLocaleString(undefined, {
    maximumFractionDigits: 2,
  });
}

export default function SegmentationPanel({
  token,
}: SegmentationPanelProps) {
  const [data, setData] = useState<CustomerSegments | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadSegments = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      setData(await getCustomerSegments(token));
    } catch (cause: unknown) {
      setError(
        cause instanceof ApiRequestError
          ? cause.message
          : "Unable to load customer segmentation.",
      );
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => {
      if (active) void loadSegments();
    });
    return () => {
      active = false;
    };
  }, [loadSegments]);

  return (
    <section className="segmentation-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">CUSTOMER INTELLIGENCE</p>
          <h2>
            <Users size={22} /> Customer segmentation
          </h2>
        </div>

        <button
          type="button"
          className="button button-secondary"
          onClick={() => void loadSegments()}
          disabled={loading}
        >
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {loading && <p>Loading customer segments...</p>}

      {error && (
        <p className="segmentation-error" role="alert">
          <AlertCircle size={17} /> {error}
        </p>
      )}

      {data && !loading && (
        <>
          <div className="inventory-metrics">
            <article>
              <span>Total customers</span>
              <strong>{formatNumber(data.total_customers)}</strong>
            </article>
            <article>
              <span>Customer segments</span>
              <strong>{formatNumber(data.segment_count)}</strong>
            </article>
          </div>

          <div className="segmentation-section">
            <h3>Segment summary</h3>
            <div className="forecast-table-wrap">
              <table className="forecast-table">
                <thead>
                  <tr>
                    <th>Segment</th>
                    <th>Customers</th>
                    <th>Avg. purchase frequency</th>
                    <th>Avg. purchase value</th>
                    <th>Avg. activity days</th>
                  </tr>
                </thead>
                <tbody>
                  {data.segment_summary.map((segment, index) => (
                    <tr key={`${segment.segment}-${index}`}>
                      <td>{segment.segment || "Unassigned"}</td>
                      <td>{formatNumber(segment.customer_count)}</td>
                      <td>
                        {formatNumber(segment.average_purchase_frequency)}
                      </td>
                      <td>{formatNumber(segment.average_purchase_value)}</td>
                      <td>
                        {formatNumber(segment.average_customer_activity_days)}
                      </td>
                    </tr>
                  ))}
                  {data.segment_summary.length === 0 && (
                    <tr>
                      <td colSpan={5}>No segment summaries are available.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="segmentation-section">

        <div className="segmentation-section">
          <h3>Segment Distribution</h3>

          {data.segment_summary.length > 0 ? (
            <div
              style={{
                width: "100%",
                height: Math.max(
                  220,
                  data.segment_summary.length * 52,
                ),
                minWidth: 0,
              }}
              role="img"
              aria-label="Horizontal bar chart showing customer counts by segment"
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={data.segment_summary}
                  layout="vertical"
                  margin={{
                    top: 8,
                    right: 28,
                    bottom: 8,
                    left: 12,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    horizontal={false}
                  />
                  <XAxis
                    type="number"
                    allowDecimals={false}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    type="category"
                    dataKey="segment"
                    width={145}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip
                    formatter={(value) => [
                      Number(value).toLocaleString(),
                      "Customers",
                    ]}
                  />
                  <Bar
                    dataKey="customer_count"
                    name="Customers"
                    fill="#1976d2"
                    radius={[0, 4, 4, 0]}
                    maxBarSize={28}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="segmentation-note">
              No segment distribution data is available.
            </p>
          )}
        </div>

            <h3>Customer assignments</h3>
            <p className="segmentation-note">
              Showing {data.customers.length.toLocaleString()} customer records
              returned by the backend.
            </p>

            <div className="forecast-table-wrap">
              <table className="forecast-table segmentation-table">
                <thead>
                  <tr>
                    <th>Customer ID</th>
                    <th>Segment</th>
                    <th>Purchase frequency</th>
                    <th>Purchase value</th>
                    <th>Last purchase</th>
                    <th>Activity days</th>
                    <th>Cluster</th>
                    <th>Hierarchical cluster</th>
                  </tr>
                </thead>
                <tbody>
                  {data.customers.map((customer, index) => (
                    <tr
                      key={`${customer["Customer ID"] ?? "unknown"}-${index}`}
                    >
                      <td>{customer["Customer ID"] ?? "N/A"}</td>
                      <td>{customer.segment_name ?? "Unassigned"}</td>
                      <td>{formatNumber(customer.purchase_frequency)}</td>
                      <td>{formatNumber(customer.purchase_value)}</td>
                      <td>{customer.last_purchase_date ?? "N/A"}</td>
                      <td>{formatNumber(customer.customer_activity_days)}</td>
                      <td>{customer.cluster ?? "N/A"}</td>
                      <td>{customer.cluster_hierarchical ?? "N/A"}</td>
                    </tr>
                  ))}
                  {data.customers.length === 0 && (
                    <tr>
                      <td colSpan={8}>No customer records are available.</td>
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