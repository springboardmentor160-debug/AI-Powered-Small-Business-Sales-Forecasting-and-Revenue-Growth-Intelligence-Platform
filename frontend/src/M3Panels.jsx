import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function M3Panels({ token, role }) {
  const [customerId, setCustomerId] = useState("17850");
  const [currentProduct, setCurrentProduct] = useState("");
  const [recommendations, setRecommendations] = useState(null);
  const [searchedProduct, setSearchedProduct] = useState("");
  const [churn, setChurn] = useState(null);
  const [anomalies, setAnomalies] = useState(null);
  const [recommendationError, setRecommendationError] = useState("");
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  async function fetchReport(endpoint) {
    const response = await fetch(`${API}${endpoint}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed (${response.status})`);
    }

    return response.json();
  }

  async function loadRecommendations(event) {
    event?.preventDefault();

    if (!customerId.trim()) {
      setRecommendationError("Enter a customer ID.");
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
          if (active) {
            setAnomalies({ error: error.message });
          }
        }
      }
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
      return <p>{emptyMessage}</p>;
    }

    return (
      <ul className="m3-list">
        {items.map((item, index) => (
          <li key={`${item}-${index}`}>{item}</li>
        ))}
      </ul>
    );
  }

  // Sales executives have no access to M3 endpoints (the API returns 403), so
  // render nothing for them rather than a recommendation form that always errors.
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
            <p>
              Customer: <strong>{recommendations.customer_id}</strong>
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

          {!churn && <p>Loading churn predictions...</p>}

          {churn?.error && renderError(churn.error)}

          {churn && !churn.error && churn.risk_summary && (
            <p>
              High: <strong>{churn.risk_summary["High Risk"]}</strong>
              {" · "}Medium:{" "}
              <strong>{churn.risk_summary["Medium Risk"]}</strong>
              {" · "}Low: <strong>{churn.risk_summary["Low Risk"]}</strong>
              {churn.model_used && <> (model: {churn.model_used})</>}
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
                  {churn.customers.map((row) => (
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
                  ))}
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

        {!anomalies && <p>Loading anomaly alerts...</p>}

        {anomalies?.error && renderError(anomalies.error)}

        {anomalies && !anomalies.error && (
          <>
            <p>
              High-severity alerts: <strong>{anomalies.high_severity}</strong>
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
                  {anomalies.alerts.map((row) => (
                    <tr key={row.row_id}>
                      <td>{row.date}</td>
                      <td>{row.store_id}</td>
                      <td>{row.product_id}</td>
                      <td>
                        <span
                          className={`m3-risk ${String(
                            row.severity,
                          ).toLowerCase()}`}
                        >
                          {row.severity}
                        </span>
                      </td>
                      <td>{row.detected_by}</td>
                      <td className="m3-message">{row.message}</td>
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
