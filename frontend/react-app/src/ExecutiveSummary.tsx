import { useCallback, useEffect, useState } from "react";
import { AlertCircle, Download, Printer, RefreshCw } from "lucide-react";
import {
  ApiRequestError,
  getCustomerSegments,
  getForecastModelComparison,
  getSalesSummary,
  type CustomerSegments,
  type ForecastModel,
  type ForecastModelComparison,
  type SalesSummary,
} from "./lib/api";

interface ExecutiveSummaryProps {
  token: string;
}

type Section<T> = { data: T | null; error: string };

const EMPTY = { data: null, error: "" };

function describeError(cause: unknown, fallback: string): string {
  return cause instanceof ApiRequestError ? cause.message : fallback;
}

function bestModel(models: ForecastModel[] | undefined): ForecastModel | null {
  if (!models || models.length === 0) return null;
  return models.reduce((best, current) =>
    current.rmse < best.rmse ? current : best,
  );
}

function formatNumber(value: number): string {
  return Number(value).toLocaleString(undefined, {
    maximumFractionDigits: 2,
  });
}

export default function ExecutiveSummary({ token }: ExecutiveSummaryProps) {
  const [loading, setLoading] = useState(true);
  const [sales, setSales] = useState<Section<SalesSummary>>(EMPTY);
  const [segments, setSegments] = useState<Section<CustomerSegments>>(EMPTY);
  const [models, setModels] =
    useState<Section<ForecastModelComparison>>(EMPTY);
  const [generatedAt, setGeneratedAt] = useState("");

  const load = useCallback(async () => {
    setLoading(true);

    // Each section is independent: a role that cannot see one section
    // still gets the others.
    const [salesResult, segmentResult, modelResult] = await Promise.allSettled([
      getSalesSummary(token),
      getCustomerSegments(token),
      getForecastModelComparison(token),
    ]);

    setSales(
      salesResult.status === "fulfilled"
        ? { data: salesResult.value, error: "" }
        : {
            data: null,
            error: describeError(
              salesResult.reason,
              "Sales summary unavailable.",
            ),
          },
    );
    setSegments(
      segmentResult.status === "fulfilled"
        ? { data: segmentResult.value, error: "" }
        : {
            data: null,
            error: describeError(
              segmentResult.reason,
              "Customer segments unavailable.",
            ),
          },
    );
    setModels(
      modelResult.status === "fulfilled"
        ? { data: modelResult.value, error: "" }
        : {
            data: null,
            error: describeError(
              modelResult.reason,
              "Forecast models unavailable.",
            ),
          },
    );
    setGeneratedAt(new Date().toLocaleString());
    setLoading(false);
  }, [token]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => {
      if (active) void load();
    });
    return () => {
      active = false;
    };
  }, [load]);

  const largestSegment = segments.data?.segment_summary.reduce(
    (largest, current) =>
      current.customer_count > largest.customer_count ? current : largest,
  );
  const bestRevenueModel = bestModel(models.data?.uci_revenue_models);
  const bestDemandModel = bestModel(models.data?.m5_demand_models);

  function downloadReport() {
    const report = {
      generated_at: generatedAt,
      sales: sales.data,
      customer_segments: segments.data
        ? {
            total_customers: segments.data.total_customers,
            segment_count: segments.data.segment_count,
            segment_summary: segments.data.segment_summary,
          }
        : null,
      forecasting: models.data
        ? {
            best_uci_revenue_model: bestRevenueModel,
            best_m5_demand_model: bestDemandModel,
          }
        : null,
      note:
        "Revenue figures come from the UCI Online Retail II dataset; demand " +
        "forecasts come from the Walmart M5 dataset. The two sources are " +
        "reported separately and are not interchangeable.",
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "marketmindai-executive-summary.json";
    link.click();
    URL.revokeObjectURL(url);
  }

  const unavailable = (message: string) => (
    <p className="segmentation-error" role="alert">
      <AlertCircle size={17} /> {message}
    </p>
  );

  return (
    <section className="executive-summary">
      <div className="section-heading">
        <div>
          <p className="eyebrow">EXECUTIVE REPORTING</p>
          <h2>Executive summary</h2>
          <p>
            Key sales, customer and forecasting indicators in one printable
            view.
          </p>
        </div>
        <div>
          <button
            type="button"
            className="button button-secondary"
            onClick={() => void load()}
            disabled={loading}
          >
            <RefreshCw size={16} /> Refresh
          </button>{" "}
          <button
            type="button"
            className="button button-secondary"
            onClick={downloadReport}
            disabled={loading}
          >
            <Download size={16} /> Download
          </button>{" "}
          <button
            type="button"
            className="button button-secondary"
            onClick={() => window.print()}
            disabled={loading}
          >
            <Printer size={16} /> Print
          </button>
        </div>
      </div>

      {loading && <p>Loading executive summary...</p>}

      {!loading && (
        <>
          <h3>Sales (UCI Online Retail II)</h3>
          {sales.data ? (
            <div className="inventory-metrics">
              <article>
                <span>Total revenue</span>
                <strong>{formatNumber(sales.data.total_revenue)}</strong>
              </article>
              <article>
                <span>Total orders</span>
                <strong>{formatNumber(sales.data.total_orders)}</strong>
              </article>
              <article>
                <span>Top product</span>
                <strong>{sales.data.top_product || "Not available"}</strong>
              </article>
            </div>
          ) : (
            unavailable(sales.error)
          )}

          <h3>Customers</h3>
          {segments.data ? (
            <div className="inventory-metrics">
              <article>
                <span>Total customers</span>
                <strong>{formatNumber(segments.data.total_customers)}</strong>
              </article>
              <article>
                <span>Segments</span>
                <strong>{formatNumber(segments.data.segment_count)}</strong>
              </article>
              <article>
                <span>Largest segment</span>
                <strong>
                  {largestSegment
                    ? `${largestSegment.segment || "Unassigned"} (${formatNumber(
                        largestSegment.customer_count,
                      )})`
                    : "Not available"}
                </strong>
              </article>
            </div>
          ) : (
            unavailable(segments.error)
          )}

          <h3>Forecasting (best model by RMSE)</h3>
          {models.data ? (
            <div className="forecast-table-wrap">
              <table className="forecast-table">
                <thead>
                  <tr>
                    <th>Dataset</th>
                    <th>Best model</th>
                    <th>MAE</th>
                    <th>RMSE</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["UCI daily revenue", bestRevenueModel],
                    ["M5 item demand", bestDemandModel],
                  ].map(([label, model]) => {
                    const row = model as ForecastModel | null;
                    return (
                      <tr key={label as string}>
                        <td>{label as string}</td>
                        <td>{row ? row.model : "Not available"}</td>
                        <td>{row ? formatNumber(row.mae) : "-"}</td>
                        <td>{row ? formatNumber(row.rmse) : "-"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            unavailable(models.error)
          )}

          <p className="disclaimer">
            Generated {generatedAt}. Revenue comes from UCI data and demand
            forecasts from Walmart M5 data; the sources are kept separate and
            their product identifiers are not interchangeable.
          </p>
        </>
      )}
    </section>
  );
}
