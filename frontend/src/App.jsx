import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(null);
  const [salesData, setSalesData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  async function handleLogin() {
    const response = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, password: password }),
    });
    const data = await response.json();
    if (response.ok) {
      setToken(data.access_token);
    } else {
      console.log("Login failed", data);
    }
  }

  function handleLogout() {
    setToken(null);
    setCurrentUser(null);
    setSalesData([]);
    setSummary(null);
  }

  useEffect(() => {
    if (token) {
      fetch("http://127.0.0.1:8000/me", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => setCurrentUser(data));

      fetch("http://127.0.0.1:8000/sales-transactions", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => (res.ok ? res.json() : []))
        .then((data) => setSalesData(data));

      fetch("http://127.0.0.1:8000/sales/summary", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => setSummary(data));
    }
  }, [token]);

  function renderMainPanel() {
    if (!currentUser) return null;

    switch (currentUser.role) {
      case "sales_exec":
        return (
          <div className="panel">
            <p className="restricted-msg">
              Sales transactions aren't part of your role's dashboard. Your
              assigned-customer transactions view is coming in a future
              milestone.
            </p>
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
              {currentUser.name}{" "}
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
          <div className="kpi-row">
            <div className="kpi-card">
              <div className="kpi-icon units">↑</div>
              <div>
                <p className="kpi-label">Total units sold</p>
                <p className="kpi-value">
                  {summary ? summary.total_units_sold.toLocaleString() : "..."}
                </p>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon inventory">▦</div>
              <div>
                <p className="kpi-label">Total inventory</p>
                <p className="kpi-value">
                  {summary ? summary.total_inventory.toLocaleString() : "..."}
                </p>
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon alert">!</div>
              <div>
                <p className="kpi-label">Low stock items</p>
                <p className="kpi-value">
                  {summary ? summary.low_stock_count.toLocaleString() : "..."}
                </p>
              </div>
            </div>
          </div>

          {renderMainPanel()}
        </div>
      ) : (
        <div className="login-wrap">
          <div className="login-container">
            <div className="brand-mark large">M</div>
            <h2>Sign in</h2>
            <p className="login-sub">Access your MarketMind AI dashboard</p>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button onClick={handleLogin}>Sign in</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
