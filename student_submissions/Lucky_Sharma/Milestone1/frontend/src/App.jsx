import React from "react";
import { useEffect, useState } from "react";
import { api, setToken } from "./api";

const demoUsers = [
  ["Business Owner", "owner@marketmind.ai", "owner123", "business_owner"],
  ["Store Manager", "manager@marketmind.ai", "manager123", "store_manager"],
  ["Sales Executive", "sales@marketmind.ai", "sales123", "sales_executive"],
  ["Administrator", "admin@marketmind.ai", "admin123", "admin"],
];

function Login({ onLogin }) {
  const [email, setEmail] = useState("owner@marketmind.ai");
  const [password, setPassword] = useState("owner123");
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");

    try {
      const { data } = await api.post("/auth/login", { email, password });
      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);
      onLogin(data.role);
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="brand">MarketMind <span>AI</span></div>
        <p className="muted">Small Business Sales Intelligence Platform</p>

        <form onSubmit={submit}>
          <label>Email</label>
          <input value={email} onChange={(e) => setEmail(e.target.value)} />

          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <div className="error">{error}</div>}

          <button className="primary full">Login</button>
        </form>

        <div className="demo-box">
          <strong>Demo accounts</strong>
          {demoUsers.map(([name, mail, pass]) => (
            <button
              className="demo-user"
              key={mail}
              onClick={() => {
                setEmail(mail);
                setPassword(pass);
              }}
            >
              {name} — {mail}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function Metric({ title, value, prefix = "" }) {
  return (
    <div className="metric">
      <div className="muted">{title}</div>
      <div className="metric-value">{prefix}{value}</div>
    </div>
  );
}

function Dashboard({ role, onLogout }) {
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState("");

  async function load() {
    try {
      const [s, t, p] = await Promise.all([
        api.get("/dashboard/summary"),
        api.get("/dashboard/sales-trend"),
        api.get("/dashboard/top-products"),
      ]);
      setSummary(s.data);
      setTrend(t.data);
      setTopProducts(p.data);

      if (["business_owner", "store_manager", "admin"].includes(role)) {
        const a = await api.get("/inventory/alerts");
        setAlerts(a.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load dashboard");
    }
  }

  useEffect(() => {
    load();
  }, []);

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    onLogout();
  }

  if (!summary && !error) {
    return <div className="loading">Loading MarketMind AI...</div>;
  }

  return (
    <div className="app-shell">
      <aside>
        <div className="brand">MarketMind <span>AI</span></div>
        <div className="role-badge">{role.replaceAll("_", " ")}</div>

        <nav>
          <a className="active">Dashboard</a>
          <a>Sales</a>
          {["business_owner", "store_manager", "admin"].includes(role) && <a>Inventory</a>}
          <a>Customers</a>
          <a>Invoices</a>
          <a>Forecasting</a>
          <a>Segmentation</a>
          <a>Churn</a>
          <a>Recommendations</a>
          <a>Anomalies</a>
        </nav>

        <button className="logout" onClick={logout}>Logout</button>
      </aside>

      <main>
        <header>
          <div>
            <h1>Sales Intelligence Dashboard</h1>
            <p className="muted">
              Monitor sales, inventory and business performance.
            </p>
          </div>
          <div className="profile">{role.replaceAll("_", " ")}</div>
        </header>

        {error && <div className="error">{error}</div>}

        {summary && (
          <>
            <section className="metrics">
              <Metric title="Total Revenue" value={summary.total_revenue.toLocaleString("en-IN")} prefix="₹" />
              <Metric title="Total Orders" value={summary.total_orders.toLocaleString("en-IN")} />
              <Metric title="Customers" value={summary.total_customers.toLocaleString("en-IN")} />
              <Metric title="Products" value={summary.total_products.toLocaleString("en-IN")} />
            </section>

            <section className="grid-two">
              <div className="panel">
                <div className="panel-head">
                  <h2>Sales Trend</h2>
                  <span>2025</span>
                </div>
                <div className="chart">
                  {trend.length === 0 ? (
                    <p className="muted">No sales data</p>
                  ) : (
                    trend.slice(-30).map((item) => {
                      const max = Math.max(...trend.slice(-30).map(x => x.revenue));
                      const height = Math.max(4, (item.revenue / max) * 170);
                      return (
                        <div className="bar-wrap" key={item.date} title={`${item.date}: ₹${item.revenue.toLocaleString("en-IN")}`}>
                          <div className="bar" style={{ height: `${height}px` }} />
                        </div>
                      );
                    })
                  )}
                </div>
              </div>

              <div className="panel">
                <div className="panel-head">
                  <h2>Business Highlights</h2>
                </div>
                <div className="highlight">
                  <span>Top Product</span>
                  <strong>{summary.top_product}</strong>
                </div>
                <div className="highlight">
                  <span>Low Stock Items</span>
                  <strong>{summary.low_stock_items}</strong>
                </div>
                <div className="highlight">
                  <span>Platform Status</span>
                  <strong>Operational</strong>
                </div>
              </div>
            </section>

            <section className="grid-two">
              <div className="panel">
                <div className="panel-head">
                  <h2>Top Products</h2>
                </div>
                <div className="table">
                  <div className="table-row header">
                    <span>Product</span><span>Qty</span><span>Revenue</span>
                  </div>
                  {topProducts.map((p) => (
                    <div className="table-row" key={p.product_name}>
                      <span>{p.product_name}</span>
                      <span>{p.quantity}</span>
                      <span>₹{p.revenue.toLocaleString("en-IN")}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="panel">
                <div className="panel-head">
                  <h2>Inventory Alerts</h2>
                  <span>{alerts.length} alerts</span>
                </div>
                {["business_owner", "store_manager", "admin"].includes(role) ? (
                  alerts.length ? (
                    alerts.slice(0, 6).map((a) => (
                      <div className="alert-row" key={a.product_id}>
                        <div>
                          <strong>{a.product_name}</strong>
                          <small>{a.warehouse}</small>
                        </div>
                        <span>{a.stock_level} / {a.reorder_point}</span>
                      </div>
                    ))
                  ) : <p className="muted">No low-stock alerts.</p>
                ) : (
                  <p className="muted">Inventory access is restricted for this role.</p>
                )}
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default function App() {
  const [role, setRole] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setToken(token);
      api.get("/auth/me")
        .then(({ data }) => setRole(data.role))
        .catch(() => {
          localStorage.removeItem("token");
          setToken(null);
        });
    }
  }, []);

  if (!role) {
    return <Login onLogin={setRole} />;
  }

  return (
    <Dashboard
      role={role}
      onLogout={() => setRole(null)}
    />
  );
}
