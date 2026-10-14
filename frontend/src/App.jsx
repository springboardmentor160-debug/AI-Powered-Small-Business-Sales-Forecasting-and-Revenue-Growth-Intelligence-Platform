import { useState, useEffect } from "react";
import "./App.css";
import M3Panels from "./M3Panels";

function formatDetail(detail, status) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return "Please check the value you entered and try again.";
  return `Request failed (${status})`;
}

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(null);
  const [salesData, setSalesData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [myTransactions, setMyTransactions] = useState([]);
  const [segments, setSegments] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [loginError, setLoginError] = useState("");
  const [dashboardError, setDashboardError] = useState("");
  const [loadingDashboard, setLoadingDashboard] = useState(false);

  const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  async function apiFetch(endpoint, accessToken, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(`${API}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          ...(options.body ? { "Content-Type": "application/json" } : {}),
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
          ...options.headers,
        },
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        const err = new Error(formatDetail(body.detail, response.status));
        err.status = response.status;
        throw err;
      }
      return body;
    } catch (error) {
      if (error.name === "AbortError") throw new Error("The server took too long to respond. Please try again.");
      if (error instanceof TypeError) throw new Error("Couldn't reach the server. Check that the backend is running.");
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  async function handleLogin(event) {
    event?.preventDefault();
    setLoginError("");
    if (!email.trim() || !password) {
      setLoginError("Enter your email and password.");
      return;
    }
    try {
      const data = await apiFetch("/login", null, {
        method: "POST",
        body: JSON.stringify({ email: email.trim(), password }),
      });
      setToken(data.access_token);
    } catch (error) {
      setLoginError(error.message || "Sign-in failed. Please try again.");
    }
  }

  function handleLogout() {
    setToken(null);
    setCurrentUser(null);
    setSalesData([]);
    setSummary(null);
    setMyTransactions([]);
    setSegments([]);
    setForecast(null);
    setDashboardError("");
    setLoadingDashboard(false);
  }

  function expireSession() {
    handleLogout();
    setLoginError("Your session expired. Please sign in again.");
  }

  useEffect(() => {
    if (!token) return;
    let active = true;

    async function loadDashboard() {
      setLoadingDashboard(true);
      setDashboardError("");
      try {
        const me = await apiFetch("/me", token);
        if (!active) return;
        setCurrentUser(me);

        const results = await Promise.allSettled([
          apiFetch("/sales-transactions", token),
          apiFetch("/sales/summary", token),
          apiFetch("/transactions", token),
          apiFetch("/segments", token),
          apiFetch("/forecast/revenue", token),
        ]);
        if (!active) return;

        const [sales, summaryResult, transactions, segmentResult, forecastResult] = results;
        setSalesData(sales.status === "fulfilled" ? sales.value : []);
        setSummary(summaryResult.status === "fulfilled" ? summaryResult.value : null);
        setMyTransactions(transactions.status === "fulfilled" ? transactions.value : []);
        setSegments(segmentResult.status === "fulfilled" && Array.isArray(segmentResult.value) ? segmentResult.value : []);
        setForecast(forecastResult.status === "fulfilled" ? forecastResult.value : null);

        const rejected = results.filter((result) => result.status === "rejected");
        if (rejected.some((result) => result.reason?.status === 401)) {
          expireSession();
          return;
        }
        const failures = rejected.filter((result) => result.reason?.status !== 403);
        if (failures.length > 0) {
          const reasons = [...new Set(failures.map((f) => f.reason?.message).filter(Boolean))];
          setDashboardError(`Some dashboard sections couldn't load: ${reasons.join("; ")}`);
        }
      } catch (error) {
        if (active) {
          if (error.status === 401) {
            expireSession();
          } else {
            setDashboardError(error.message || "Couldn't load your dashboard. Please sign in again.");
            setCurrentUser(null);
          }
        }
      } finally {
        if (active) setLoadingDashboard(false);
      }
    }

    loadDashboard();
    return () => { active = false; };
  }, [token]);

  function renderMainPanel() {
    if (!currentUser) return null;

    switch (currentUser.role) {
      case "sales_exec":
        return (
          <div className="panel">
            <div className="panel-header">
              <h2>My customer transactions</h2>
              <span className="row-count">{myTransactions.length} rows</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Customer</th>
                  <th>Item</th>
                  <th>Qty</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {myTransactions.map((row) => (
                  <tr key={row.id}>
                    <td>{row.invoice_no}</td>
                    <td>{row.customer_id}</td>
                    <td>{row.description}</td>
                    <td>{row.quantity}</td>
                    <td>${row.total_amount.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );

      case "store_manager":
        return (
          <div className="panel">
            <div className="panel-header">
              <h2>Inventory overview</h2>
              <span className="row-count">{salesData.length} rows</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Store</th>
                  <th>Product</th>
                  <th>Inventory</th>
                  <th>Units sold</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {[...salesData]
                  .sort((a, b) => a.inventory_level - b.inventory_level)
                  .map((row) => (
                    <tr key={row.id}>
                      <td>{row.store_id}</td>
                      <td>{row.product_id}</td>
                      <td>
                        <span className={row.inventory_level < 100 ? "low" : ""}>
                          {row.inventory_level}
                        </span>
                      </td>
                      <td>{row.units_sold}</td>
                      <td>
                        {row.inventory_level < 100 ? (
                          <span className="low">Reorder soon</span>
                        ) : (
                          "In stock"
                        )}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        );

      default:
        return (
          <div className="panel">
            <div className="panel-header">
              <h2>Sales transactions</h2>
              <span className="row-count">{salesData.length} rows</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Store</th>
                  <th>Product</th>
                  <th>Date</th>
                  <th>Units sold</th>
                  <th>Inventory</th>
                </tr>
              </thead>
              <tbody>
                {salesData.map((row) => (
                  <tr key={row.id}>
                    <td>{row.store_id}</td>
                    <td>{row.product_id}</td>
                    <td>{row.date}</td>
                    <td>{row.units_sold}</td>
                    <td>
                      <span className={row.inventory_level < 100 ? "low" : ""}>
                        {row.inventory_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
    }
  }

  const maxSeg = Math.max(1, ...segments.map((s) => s.customer_count));
  const showKpis = currentUser && ["owner", "admin", "store_manager"].includes(currentUser.role);
  const kpiFallback = loadingDashboard ? "..." : "—";

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">M</div>
          <h1>MarketMind AI</h1>
        </div>
        {currentUser && (
          <div className="user-info">
            <span className="user-name">
              {currentUser.name}
              <span className="user-role">{currentUser.role}</span>
            </span>
            <button className="logout-btn" onClick={handleLogout}>
              Sign out
            </button>
          </div>
        )}
      </header>

      {token ? (
        <div className="dashboard">
          {loadingDashboard && <p className="status-message" role="status">Loading dashboard…</p>}
          {dashboardError && <div className="app-error" role="alert">{dashboardError}</div>}
          
          {showKpis && (
            <div className="kpi-row">
              <div className="kpi-card">
                <div className="kpi-icon units">↑</div>
                <div>
                  <p className="kpi-label">Total units sold</p>
                  <p className="kpi-value">
                    {summary ? Number(summary.total_units_sold || 0).toLocaleString() : kpiFallback}
                  </p>
                </div>
              </div>
              <div className="kpi-card">
                <div className="kpi-icon inventory">▦</div>
                <div>
                  <p className="kpi-label">Total inventory</p>
                  <p className="kpi-value">
                    {summary ? Number(summary.total_inventory || 0).toLocaleString() : kpiFallback}
                  </p>
                </div>
              </div>
              <div className="kpi-card">
                <div className="kpi-icon alert">!</div>
                <div>
                  <p className="kpi-label">Low stock items</p>
                  <p className="kpi-value">
                    {summary ? Number(summary.low_stock_count || 0).toLocaleString() : kpiFallback}
                  </p>
                </div>
              </div>
            </div>
          )}

          {(segments.length > 0 || forecast) && (
            <div className="insights-row">
              {segments.length > 0 && (
                <div className="panel">
                  <div className="panel-header">
                    <h2>Customer segments</h2>
                  </div>
                  {segments.map((s) => (
                    <div key={s.segment} className="seg-row">
                      <span className="seg-name">{s.segment}</span>
                      <div className="seg-bar">
                        <div
                          className="seg-fill"
                          style={{
                            width: `${(s.customer_count / maxSeg) * 100}%`,
                          }}
                        />
                      </div>
                      <span className="seg-count">
                        {s.customer_count.toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              )}
              {forecast && (
                <div className="panel">
                  <div className="panel-header">
                    <h2>Sales forecast</h2>
                  </div>
                  <p className="kpi-label" style={{ marginTop: '0.25rem' }}>
                    Predicted revenue ({forecast.period})
                  </p>
                  <p className="kpi-value" style={{ margin: '0.35rem 0' }}>
                    ${Number(forecast.predicted_revenue || 0).toLocaleString()}
                  </p>
                  <p className="kpi-label" style={{ marginTop: '0.75rem' }}>Model: {forecast.model_used}</p>
                </div>
              )}
            </div>
          )}

          {renderMainPanel()}

          {currentUser && (
            <M3Panels token={token} role={currentUser.role} onSessionExpired={expireSession} />
          )}
        </div>
      ) : (
        <div className="login-wrap">
          <div className="login-hero">
            <h2>Intelligent Retail <span>Analytics & Forecasting</span></h2>
            <p>
              MarketMind AI provides real-time demand forecasting, customer segmentation, churn prediction, and automated anomaly detection.
            </p>
            <div className="login-features">
              <span className="login-feature-pill">✦ Role-Based Access</span>
              <span className="login-feature-pill">✦ XGBoost Forecasting</span>
              <span className="login-feature-pill">✦ Smart Recommendations</span>
            </div>
          </div>
          <div className="login-container">
            <h3>Welcome back</h3>
            <p className="login-sub">Sign in to access your dashboard</p>
            <form onSubmit={handleLogin}>
              <input
                type="email"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              {loginError && <p className="m3-error login-error" role="alert">{loginError}</p>}
              <button type="submit">Sign in</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;