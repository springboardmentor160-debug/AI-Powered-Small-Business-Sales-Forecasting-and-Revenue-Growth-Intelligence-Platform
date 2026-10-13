import { useCallback, useEffect, useState, type FormEvent } from "react";
import { AlertCircle, RefreshCw, ShoppingBag } from "lucide-react";
import {
  ApiRequestError,
  getCustomerRecommendations,
  getRecommendationOverview,
  type CustomerRecommendationResponse,
  type RecommendationOverview,
} from "./lib/api";

interface RecommendationsPanelProps {
  token: string;
}

function formatNumber(value: number | null | undefined, digits = 2): string {
  if (value == null || !Number.isFinite(Number(value))) return "N/A";
  return Number(value).toLocaleString(undefined, {
    maximumFractionDigits: digits,
  });
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export default function RecommendationsPanel({
  token,
}: RecommendationsPanelProps) {
  const [overview, setOverview] = useState<RecommendationOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [customerId, setCustomerId] = useState("12347");
  const [stockCode, setStockCode] = useState("85123A");
  const [result, setResult] = useState<CustomerRecommendationResponse | null>(
    null,
  );
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupError, setLookupError] = useState("");

  const loadOverview = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      setOverview(await getRecommendationOverview(token));
    } catch (cause: unknown) {
      setError(
        cause instanceof ApiRequestError
          ? cause.message
          : "Unable to load the recommendation overview.",
      );
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => {
      if (active) void loadOverview();
    });
    return () => {
      active = false;
    };
  }, [loadOverview]);

  async function handleLookup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLookupError("");
    setResult(null);

    const id = Number(customerId);
    if (!Number.isInteger(id) || id <= 0) {
      setLookupError("Enter a valid numeric customer ID.");
      return;
    }

    setLookupLoading(true);
    try {
      setResult(await getCustomerRecommendations(id, stockCode, token));
    } catch (cause: unknown) {
      setLookupError(
        cause instanceof ApiRequestError
          ? cause.message
          : "Unable to load recommendations.",
      );
    } finally {
      setLookupLoading(false);
    }
  }

  const collaborative = overview?.evaluation.find(
    (row) => row.model === "collaborative_filtering",
  );
  const baseline = overview?.evaluation.find(
    (row) => row.model === "popularity_baseline",
  );

  return (
    <section className="segmentation-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">CUSTOMER INTELLIGENCE</p>
          <h2>
            <ShoppingBag size={22} /> Product recommendations
          </h2>
          <p>
            Personalised suggestions, frequently-bought-together products and
            upsell opportunities.
          </p>
        </div>

        <button
          type="button"
          className="button button-secondary"
          onClick={() => void loadOverview()}
          disabled={loading}
        >
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {error && (
        <p className="segmentation-error" role="alert">
          <AlertCircle size={17} /> {error}
        </p>
      )}

      <div className="segmentation-section">
        <h3>Look up recommendations</h3>
        <form className="m3-form" onSubmit={(event) => void handleLookup(event)}>
          <label>
            Customer ID
            <input
              value={customerId}
              onChange={(event) => setCustomerId(event.target.value)}
              inputMode="numeric"
              placeholder="e.g. 12347"
            />
          </label>
          <label>
            Product code (optional)
            <input
              value={stockCode}
              onChange={(event) => setStockCode(event.target.value)}
              placeholder="e.g. 85123A"
            />
          </label>
          <button
            type="submit"
            className="button button-primary"
            disabled={lookupLoading}
          >
            {lookupLoading ? "Loading..." : "Get recommendations"}
          </button>
        </form>

        {lookupError && (
          <p className="segmentation-error" role="alert">
            <AlertCircle size={17} /> {lookupError}
          </p>
        )}

        {result && (
          <>
            <h4>
              Recommended for customer {result.customer_id}
              {result.recommended_for_you.source === "popular_products" &&
                " (new customer: best sellers)"}
            </h4>
            {result.recommended_for_you.note && (
              <p className="segmentation-note">
                {result.recommended_for_you.note}
              </p>
            )}
            <div className="forecast-table-wrap">
              <table className="forecast-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Code</th>
                    <th>Unit price</th>
                  </tr>
                </thead>
                <tbody>
                  {result.recommended_for_you.recommendations.map((item) => (
                    <tr key={item.StockCode}>
                      <td>{item.Description}</td>
                      <td>{item.StockCode}</td>
                      <td>{formatNumber(item.unit_price)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {stockCode.trim() && (
              <>
                <h4>Frequently bought with {stockCode.trim().toUpperCase()}</h4>
                <div className="forecast-table-wrap">
                  <table className="forecast-table">
                    <thead>
                      <tr>
                        <th>Product</th>
                        <th>Confidence</th>
                        <th>Lift</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.frequently_bought_with.map((item) => (
                        <tr key={item.consequent_code}>
                          <td>{item.consequent_name}</td>
                          <td>{formatPercent(item.confidence)}</td>
                          <td>{formatNumber(item.lift, 1)}</td>
                        </tr>
                      ))}
                      {result.frequently_bought_with.length === 0 && (
                        <tr>
                          <td colSpan={3}>
                            No frequent pairings found for this product.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>

                <h4>Upsell opportunities</h4>
                <div className="forecast-table-wrap">
                  <table className="forecast-table">
                    <thead>
                      <tr>
                        <th>Product</th>
                        <th>Price</th>
                        <th>Price uplift</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.upsell_opportunities.map((item) => (
                        <tr key={item.upsell_code}>
                          <td>{item.upsell_name}</td>
                          <td>{formatNumber(item.upsell_price)}</td>
                          <td>+{formatNumber(item.price_uplift_pct, 0)}%</td>
                        </tr>
                      ))}
                      {result.upsell_opportunities.length === 0 && (
                        <tr>
                          <td colSpan={3}>
                            No upsell candidates for this product.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </>
        )}
      </div>

      {loading && <p>Loading recommendation insights...</p>}

      {overview && !loading && (
        <>
          <div className="inventory-metrics">
            <article>
              <span>Association rules</span>
              <strong>{formatNumber(overview.rule_count, 0)}</strong>
            </article>
            <article>
              <span>Upsell pairs</span>
              <strong>{formatNumber(overview.upsell_pair_count, 0)}</strong>
            </article>
            {collaborative && baseline && (
              <article>
                <span>Hit rate @10 vs best-seller baseline</span>
                <strong>
                  {formatPercent(collaborative.hit_rate_at_10)} vs{" "}
                  {formatPercent(baseline.hit_rate_at_10)}
                </strong>
              </article>
            )}
          </div>

          <div className="segmentation-section">
            <h3>Strongest product pairings</h3>
            <p className="segmentation-note">
              Lift above 1 means the two products are bought together more
              often than chance. One strongest pairing is shown per product.
            </p>
            <div className="forecast-table-wrap">
              <table className="forecast-table">
                <thead>
                  <tr>
                    <th>If a customer buys</th>
                    <th>They also buy</th>
                    <th>Support</th>
                    <th>Confidence</th>
                    <th>Lift</th>
                  </tr>
                </thead>
                <tbody>
                  {overview.top_rules.map((rule) => (
                    <tr key={`${rule.antecedent_name}-${rule.consequent_name}`}>
                      <td>{rule.antecedent_name}</td>
                      <td>{rule.consequent_name}</td>
                      <td>{formatPercent(rule.support)}</td>
                      <td>{formatPercent(rule.confidence)}</td>
                      <td>{formatNumber(rule.lift, 1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="segmentation-section">
            <h3>How good are the recommendations?</h3>
            <p className="segmentation-note">
              Measured on the final 90 days of data, which the models never saw
              during training.
            </p>
            <div className="forecast-table-wrap">
              <table className="forecast-table">
                <thead>
                  <tr>
                    <th>Model</th>
                    <th>Customers tested</th>
                    <th>Hit rate @10</th>
                    <th>Precision @10</th>
                    <th>Recall @10</th>
                  </tr>
                </thead>
                <tbody>
                  {overview.evaluation.map((row) => (
                    <tr key={row.model}>
                      <td>{row.model.replace(/_/g, " ")}</td>
                      <td>{formatNumber(row.customers_evaluated, 0)}</td>
                      <td>{formatPercent(row.hit_rate_at_10)}</td>
                      <td>{formatPercent(row.precision_at_10)}</td>
                      <td>{formatPercent(row.recall_at_10)}</td>
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
