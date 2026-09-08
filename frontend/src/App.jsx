import React, { useState, useEffect, useCallback } from "react";
import LoginScreen from "./components/LoginScreen.jsx";
import Sidebar from "./components/Sidebar.jsx";
import KpiGrid from "./components/KpiGrid.jsx";
import CategoryChart from "./components/CategoryChart.jsx";
import TopItemsPanel from "./components/TopItemsPanel.jsx";
import OrdersTable from "./components/OrdersTable.jsx";
import MenuTable from "./components/MenuTable.jsx";

const API_BASE = "/api/v1";

export default function App() {
  const [session, setSession] = useState(() => {
    const raw = sessionStorage.getItem("marketmind_session");
    return raw ? JSON.parse(raw) : null;
  });
  const [loginError, setLoginError] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [summary, setSummary] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [orders, setOrders] = useState([]);

  const authFetch = useCallback(
    (path) =>
      fetch(`${API_BASE}${path}`, {
        headers: { Authorization: `Bearer ${session?.access_token}` },
      }).then((r) => {
        if (!r.ok) throw new Error("Request failed");
        return r.json();
      }),
    [session]
  );

  const handleLogin = async (username, password) => {
    setLoginLoading(true);
    setLoginError("");
    try {
      const body = new URLSearchParams({ username, password });
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      if (!res.ok) throw new Error("Invalid username or password");
      const data = await res.json();
      sessionStorage.setItem("marketmind_session", JSON.stringify(data));
      setSession(data);
    } catch (err) {
      setLoginError(err.message);
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem("marketmind_session");
    setSession(null);
    setActiveTab("overview");
  };

  useEffect(() => {
    if (!session) return;
    authFetch("/insights/summary").then(setSummary).catch(() => {});
    authFetch("/menu").then(setMenuItems).catch(() => {});
    authFetch("/orders?limit=25").then(setOrders).catch(() => {});
  }, [session, authFetch]);

  if (!session) {
    return <LoginScreen onLogin={handleLogin} error={loginError} loading={loginLoading} />;
  }

  return (
    <div className="app-shell">
      <Sidebar
        role={session.role}
        username={session.username}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <main className="main-content">
        <div className="topbar">
          <div>
            <h1>
              {activeTab === "overview" && "Business Overview"}
              {activeTab === "menu" && "Menu & Stock"}
              {activeTab === "orders" && "Orders"}
              {activeTab === "staff" && "Staff Administration"}
            </h1>
            <p>
              {session.outlet_id
                ? `Showing data for outlet ${session.outlet_id}`
                : "Showing data across all outlets"}
            </p>
          </div>
          <button className="logout-btn" onClick={handleLogout}>Sign Out</button>
        </div>

        {activeTab === "overview" && summary && (
          <>
            <KpiGrid summary={summary} />
            <div className="panel-grid">
              <CategoryChart data={summary.category_breakdown} />
              <TopItemsPanel items={summary.top_menu_items} />
            </div>
            <div className="panel-grid">
              <OrdersTable orders={summary.recent_orders} />
            </div>
          </>
        )}

        {activeTab === "menu" && (
          <div className="panel-grid">
            <MenuTable items={menuItems} />
          </div>
        )}

        {activeTab === "orders" && (
          <div className="panel-grid">
            <OrdersTable orders={orders} />
          </div>
        )}

        {activeTab === "staff" && (
          <div className="panel">
            <p style={{ color: "#5B5478" }}>
              Staff administration (list/create staff, RBAC) is available via the
              <code> /api/v1/staff</code> endpoints — wire this panel up to those once you
              extend the UI.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
