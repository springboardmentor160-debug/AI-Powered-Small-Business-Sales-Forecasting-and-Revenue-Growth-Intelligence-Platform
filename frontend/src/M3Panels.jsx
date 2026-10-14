import { useEffect, useState } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function formatDetail(detail, status) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return "Please check the value you entered and try again.";
  return `Request failed (${status})`;
}

function M3Panels({ token, role, onSessionExpired }) {
  const [customerId, setCustomerId] = useState("17850");
  const [currentProduct, setCurrentProduct] = useState("");
  const [recommendations, setRecommendations] = useState(null);
  const [searchedProduct, setSearchedProduct] = useState("");
  const [churn, setChurn] = useState(null);
  const [anomalies, setAnomalies] = useState(null);
  const [recommendationError, setRecommendationError] = useState("");
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [loadingPanels, setLoadingPanels] = useState(true);

  async function fetchReport(endpoint) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(`${API}${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` },
        signal: controller.signal,
      });
      const body = await response.json().catch(() => ({}));
      if (response.status === 401 && onSessionExpired) {
        onSessionExpired();
      }
      if (!response.ok) {
        throw new Error(formatDetail(body.detail, response.status));
      }
      return body;
    } catch (error) {
      if (error.name === "AbortError") {
        throw new Error(
          "This section took too long to load. Please try again.",
        );
      }
      if (error instanceof TypeError) {
        throw new Error(
          "Couldn't reach the backend. Check that the server is running.",
        );
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  async function loadRecommendations(event) {
    event?.preventDefault();

    if (!/^\d+$/.test(customerId.trim())) {
      setRecommendationError("Enter a numeric customer ID, e.g. 17850.");
      return;
    }

    setLoadingRecommendations(true);
    setRecommendationError("");
    setRecommendations(null);

    try {
      const params = new URLSearchParams({
        customer_id: customerId.trim(),
      });

      if (currentProduct.trim()) {
        params.set("current_product", currentProduct.trim());
      }

      const data = await fetchReport(`/recommendations?${params.toString()}`);

      setRecommendations(data);
      setSearchedProduct(currentProduct.trim());
    } catch (error) {
      setRecommendationError(error.message);
    } finally {
      setLoadingRecommendations(false);
    }
  }

  useEffect(() => {
    let active = true;

    async function loadPanels() {
      setLoadingPanels(true);
      if (role === "owner" || role === "admin") {
        try {
          const data = await fetchReport("/churn");
          if (active) setChurn(data);
        } catch (error) {
          if (active) {
            setChurn({ error: error.message });
          }
        }
      }

      if (role === "owner" || role === "admin" || role === "store_manager") {
        try {
          const data = await fetchReport("/anomalies");
          if (active) setAnomalies(data);
        } catch (error) {
          if (active) setAnomalies({ error: error.message });
        }
      }
      if (active) setLoadingPanels(false);
    }

    loadPanels();

    return () => {
      active = false;
    };
  }, [token, role]);

  function renderError(message) {
    return <p className="m3-error">{message}</p>;
  }

  function renderList(items, emptyMessage) {
    if (!items || items.length === 0) {
      return (
        <p style={{ color: "#8b94a5", fontSize: "0.875rem" }}>{emptyMessage}</p>
      );
    }

    return (
      <ul className="m3-list">
        {items.map((item, index) => (
          <li key={`${item}-${index}`}>{item}</li>
        ))}
      </ul>
    );
  }

  if (!["owner", "admin", "store_manager"].includes(role)) return null;

  return (
    <div className="m3-panels">
      {/* PRODUCT RECOMMENDATIONS */}
      <section className="panel">
        <div className="panel-header">
          <h2>Product Recommendations</h2>
        </div>

        <p>
          Get personalized product suggestions and frequently bought together
          recommendations.
        </p>

        <form onSubmit={loadRecommendations} className="m3-form">
          <label htmlFor="m3-customer-id">Customer ID</label>
          <input
            id="m3-customer-id"
            value={customerId}
            onChange={(event) => setCustomerId(event.target.value)}
            placeholder="e.g. 17850"
            required
          />

          <label htmlFor="m3-current-product">Current product (optional)</label>
          <input
            id="m3-current-product"
            value={currentProduct}
            onChange={(event) => setCurrentProduct(event.target.value)}
            placeholder="Enter exact product name"
          />

          <button type="submit" disabled={loadingRecommendations}>
            {loadingRecommendations
              ? "Finding recommendations..."
              : "Get Recommendations"}
          </button>
        </form>

        {recommendationError && renderError(recommendationError)}

        {recommendations && (
          <div className="m3-results">
            <p style={{ color: "#cbd5e1" }}>
              Customer:{" "}
              <strong style={{ color: "#ffffff" }}>
                {recommendations.customer_id}
              </strong>
            </p>

            <h3>Recommended for you</h3>
            {renderList(
              recommendations.recommended_for_you,
              "No personalized recommendations found for this customer.",
            )}

            {searchedProduct && (
              <>
                <h3>Frequently bought with</h3>
                {renderList(
                  recommendations.frequently_bought_with || [],
                  "No matching product associations found.",
                )}
              </>
            )}
          </div>
        )}
      </section>

      {/* CHURN PREDICTION */}
      {(role === "owner" || role === "admin") && (
        <section className="panel">
          <div className="panel-header">
            <h2>Customer Churn Risk</h2>
            {churn && !churn.error && (
              <span className="row-count">
                {churn.total_customers} customers
              </span>
            )}
          </div>

          {!churn && loadingPanels && (
            <p role="status" style={{ color: "#8b94a5", fontSize: "0.875rem" }}>
              Loading churn predictions…
            </p>
          )}

          {churn?.error && renderError(churn.error)}

          {churn && !churn.error && churn.risk_summary && (
            <p style={{ color: "#cbd5e1", fontSize: "0.875rem" }}>
              High Risk:{" "}
              <strong style={{ color: "#f87171" }}>
                {churn.risk_summary["High Risk"]}
              </strong>
              {" · "}Medium Risk:{" "}
              <strong style={{ color: "#fbbf24" }}>
                {churn.risk_summary["Medium Risk"]}
              </strong>
              {" · "}Low Risk:{" "}
              <strong style={{ color: "#4ade80" }}>
                {churn.risk_summary["Low Risk"]}
              </strong>
              {churn.model_used && (
                <span style={{ color: "#8b94a5" }}>
                  {" "}
                  (model: {churn.model_used})
                </span>
              )}
            </p>
          )}

          {churn && !churn.error && (
            <div className="m3-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Customer</th>
                    <th>Probability</th>
                    <th>Risk</th>
                    <th>M2 Segment</th>
                  </tr>
                </thead>
                <tbody>
                  {(Array.isArray(churn.customers) ? churn.customers : []).map(
                    (row) => (
                      <tr key={row.CustomerID}>
                        <td>{row.CustomerID}</td>
                        <td>
                          {(Number(row.churn_probability) * 100).toFixed(1)}%
                        </td>
                        <td>
                          <span
                            className={`m3-risk ${String(row.retention_risk)
                              .toLowerCase()
                              .replace(/\s+/g, "-")}`}
                          >
                            {row.retention_risk}
                          </span>
                        </td>
                        <td>{row.segment || "Unassigned"}</td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>
          )}

          {churn && !churn.error && churn.total_customers > 100 && (
            <p className="m3-note">
              Showing the 100 customers with the highest predicted churn
              probability.
            </p>
          )}
        </section>
      )}

      {/* ANOMALY DETECTION */}
      <section className="panel">
        <div className="panel-header">
          <h2>Sales & Inventory Anomaly Alerts</h2>
          {anomalies && !anomalies.error && (
            <span className="row-count">{anomalies.total_alerts} alerts</span>
          )}
        </div>

        {!anomalies && loadingPanels && (
          <p role="status" style={{ color: "#8b94a5", fontSize: "0.875rem" }}>
            Loading anomaly alerts…
          </p>
        )}

        {anomalies?.error && renderError(anomalies.error)}

        {anomalies && !anomalies.error && (
          <>
            <p style={{ color: "#cbd5e1", fontSize: "0.875rem" }}>
              High-severity alerts:{" "}
              <strong style={{ color: "#f87171" }}>
                {anomalies.high_severity}
              </strong>
              {anomalies.medium_severity !== undefined && (
                <>
                  {" "}
                  · Medium severity:{" "}
                  <strong style={{ color: "#fbbf24" }}>
                    {anomalies.medium_severity}
                  </strong>
                </>
              )}
            </p>

            <div className="m3-table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Store</th>
                    <th>Product</th>
                    <th>Severity</th>
                    <th>Detected by</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {(Array.isArray(anomalies.alerts)
                    ? anomalies.alerts
                    : []
                  ).map((row) => (
                    <tr key={row.row_id}>
                      <td>{row.date}</td>
                      <td>{row.store_id}</td>
                      <td>{row.product_id}</td>
                      <td>
                        <span
                          className={`m3-risk ${String(row.severity).toLowerCase()}`}
                        >
                          {row.severity}
                        </span>
                      </td>
                      <td>{row.detected_by}</td>
                      <td>{row.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {anomalies.total_alerts > 100 && (
              <p className="m3-note">
                Showing the 100 highest-priority alerts (high severity first).
              </p>
            )}
          </>
        )}
      </section>
    </div>
  );
}

export default M3Panels;
