import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

function App() {
  const [revenue, setRevenue] = useState(0);
  const [orders, setOrders] = useState(0);
  const [unitsSold, setUnitsSold] = useState(0);

  const [revenueTrend, setRevenueTrend] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [topCustomers, setTopCustomers] = useState([]);
  const [salesByCountry, setSalesByCountry] = useState([]);

  const [totalStock, setTotalStock] = useState(0);
  const [lowStockProducts, setLowStockProducts] = useState(0);

  const [insights, setInsights] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/sales/revenue")
      .then((response) => response.json())
      .then((data) => {
        setRevenue(data.total_revenue);
      })
      .catch((error) => {
        console.error("Revenue API error:", error);
      });

    fetch("http://127.0.0.1:8000/sales/summary")
      .then((response) => response.json())
      .then((data) => {
        setOrders(data.total_orders);
        setUnitsSold(data.total_quantity);
      })
      .catch((error) => {
        console.error("Summary API error:", error);
      });

    fetch("http://127.0.0.1:8000/sales/revenue/trends")
      .then((response) => response.json())
      .then((data) => {
        setRevenueTrend(data);
      })
      .catch((error) => {
        console.error("Revenue trend API error:", error);
      });

    fetch("http://127.0.0.1:8000/products/top")
      .then((response) => response.json())
      .then((data) => {
        setTopProducts(data);
      })
      .catch((error) => {
        console.error("Top products API error:", error);
      });

    fetch("http://127.0.0.1:8000/customers/top")
      .then((response) => response.json())
      .then((data) => {
        setTopCustomers(data);
      })
      .catch((error) => {
        console.error("Top customers API error:", error);
      });

    fetch("http://127.0.0.1:8000/sales/countries")
      .then((response) => response.json())
      .then((data) => {
        setSalesByCountry(data.slice(0, 8));
      })
      .catch((error) => {
        console.error("Country API error:", error);
      });

    fetch("http://127.0.0.1:8000/inventory/summary")
      .then((response) => response.json())
      .then((data) => {
        setTotalStock(data.total_stock_units);
        setLowStockProducts(data.low_stock_products);
      })
      .catch((error) => {
        console.error("Inventory API error:", error);
      });

    fetch("http://127.0.0.1:8000/insights/overview")
      .then((response) => response.json())
      .then((data) => {
        setInsights(data);
      })
      .catch((error) => {
        console.error("Insights API error:", error);
      });
  }, []);

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="brand-row">
            <div className="brand-icon">M</div>

            <div>
              <h1>MarketMind AI</h1>
              <p>Sales & Business Intelligence Platform</p>
            </div>
          </div>

          <div className="connection-status">
            <span className="status-dot"></span>
            Analytics API Connected
          </div>
        </div>
      </header>

      <main className="dashboard">

        {/* Dashboard Introduction */}
        <div className="dashboard-intro">
          <div>
            <h2>Business Overview</h2>
            <p>
              Monitor sales performance, customers, products and inventory.
            </p>
          </div>

          <div className="data-badge">
            LIVE DATA
          </div>
        </div>

        {/* KPI Cards */}
        <section className="kpi-grid">

          <div className="kpi-card revenue-card">
            <div className="kpi-top">
              <div className="kpi-icon">₹</div>
              <span>Revenue</span>
            </div>

            <p>₹{revenue.toLocaleString()}</p>

            <small>Total sales revenue</small>
          </div>

          <div className="kpi-card">
            <div className="kpi-top">
              <div className="kpi-icon">📦</div>
              <span>Units Sold</span>
            </div>

            <p>{unitsSold.toLocaleString()}</p>

            <small>Total quantity sold</small>
          </div>

          <div className="kpi-card">
            <div className="kpi-top">
              <div className="kpi-icon">🧾</div>
              <span>Orders</span>
            </div>

            <p>{orders.toLocaleString()}</p>

            <small>Total transactions</small>
          </div>

          <div className="kpi-card">
            <div className="kpi-top">
              <div className="kpi-icon">👥</div>
              <span>Customers</span>
            </div>

            <p>4,338</p>

            <small>Unique customers</small>
          </div>

          <div className="kpi-card">
            <div className="kpi-top">
              <div className="kpi-icon">🏷️</div>
              <span>Products</span>
            </div>

            <p>3,922</p>

            <small>Products in catalog</small>
          </div>

        </section>

        {/* Main Dashboard */}
        <section className="content-grid">

          {/* Revenue Trend */}
          <div className="panel large-panel">

            <div className="panel-header">
              <div>
                <h2>Revenue Trend</h2>
                <p>Daily revenue performance</p>
              </div>

              <span className="panel-badge">
                Performance
              </span>
            </div>

            <div className="chart-container">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart
                  data={revenueTrend}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 10,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                  />

                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                  />

                  <YAxis
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                  />

                  <Tooltip
                    formatter={(value) => [
                      `₹${Number(value).toLocaleString()}`,
                      "Revenue",
                    ]}
                  />

                  <Line
                    type="monotone"
                    dataKey="revenue"
                    strokeWidth={3}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

          </div>

          {/* Top Products */}
          <div className="panel">

            <div className="panel-header">
              <div>
                <h2>Top Products</h2>
                <p>Highest selling products</p>
              </div>

              <span className="panel-badge">
                Top 10
              </span>
            </div>

            <div className="product-chart">
              <ResponsiveContainer width="100%" height={350}>
                <BarChart
                  data={topProducts}
                  layout="vertical"
                  margin={{
                    top: 5,
                    right: 20,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    horizontal={false}
                  />

                  <XAxis
                    type="number"
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                  />

                  <YAxis
                    type="category"
                    dataKey="product_name"
                    width={150}
                    tick={{ fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                  />

                  <Tooltip
                    formatter={(value) => [
                      Number(value).toLocaleString(),
                      "Units Sold",
                    ]}
                  />

                  <Bar
                    dataKey="quantity_sold"
                    barSize={18}
                    radius={[0, 5, 5, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

          </div>

          {/* Top Customers */}
          <div className="panel">

            <div className="panel-header">
              <div>
                <h2>Top Customers</h2>
                <p>Customers by purchase volume</p>
              </div>

              <span className="panel-badge">
                Top 10
              </span>
            </div>

            <div className="customer-chart">
              <ResponsiveContainer width="100%" height={350}>
                <BarChart
                  data={topCustomers}
                  layout="vertical"
                  margin={{
                    top: 5,
                    right: 20,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    horizontal={false}
                  />

                  <XAxis
                    type="number"
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                  />

                  <YAxis
                    type="category"
                    dataKey="customer_name"
                    width={140}
                    tick={{ fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                  />

                  <Tooltip
                    formatter={(value) => [
                      Number(value).toLocaleString(),
                      "Units Purchased",
                    ]}
                  />

                  <Bar
                    dataKey="quantity_purchased"
                    barSize={18}
                    radius={[0, 5, 5, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

          </div>

          {/* Sales by Country */}
          <div className="panel">

            <div className="panel-header">
              <div>
                <h2>Sales by Country</h2>
                <p>Geographic sales distribution</p>
              </div>

              <span className="panel-badge">
                Top 8
              </span>
            </div>

            <div className="country-chart">
              <ResponsiveContainer width="100%" height={350}>
                <BarChart
                  data={salesByCountry}
                  layout="vertical"
                  margin={{
                    top: 5,
                    right: 20,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    horizontal={false}
                  />

                  <XAxis
                    type="number"
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                  />

                  <YAxis
                    type="category"
                    dataKey="country"
                    width={120}
                    tick={{ fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                  />

                  <Tooltip
                    formatter={(value) => [
                      Number(value).toLocaleString(),
                      "Units Sold",
                    ]}
                  />

                  <Bar
                    dataKey="quantity_sold"
                    barSize={20}
                    radius={[0, 5, 5, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

          </div>

          {/* AI Insights */}
          <div className="panel insights-panel">

            <div className="panel-header">
              <div>
                <h2>🤖 AI Insights</h2>
                <p>Automated business intelligence</p>
              </div>

              <span className="ai-badge">
                AI ANALYSIS
              </span>
            </div>

            {insights ? (
              <div className="insights-list">

                <div className="insight-item">
                  <div className="insight-label">
                    <span className="insight-icon">₹</span>
                    <span>Revenue</span>
                  </div>

                  <strong>
                    ₹{insights.total_revenue.toLocaleString()}
                  </strong>
                </div>

                <div className="insight-item">
                  <div className="insight-label">
                    <span className="insight-icon">📦</span>
                    <span>Units Sold</span>
                  </div>

                  <strong>
                    {insights.total_units_sold.toLocaleString()}
                  </strong>
                </div>

                <div className="insight-item">
                  <div className="insight-label">
                    <span className="insight-icon">🏆</span>
                    <span>Best Product</span>
                  </div>

                  <strong>
                    {insights.best_product?.product_name || "N/A"}
                  </strong>
                </div>

                <div className="insight-item">
                  <div className="insight-label">
                    <span className="insight-icon">👤</span>
                    <span>Top Customer</span>
                  </div>

                  <strong>
                    {insights.top_customer?.customer_name || "N/A"}
                  </strong>
                </div>

                <div className="insight-item">
                  <div className="insight-label">
                    <span className="insight-icon">🌍</span>
                    <span>Best Country</span>
                  </div>

                  <strong>
                    {insights.best_country?.country || "N/A"}
                  </strong>
                </div>

                <div className="insight-item">
                  <div className="insight-label">
                    <span className="insight-icon">⚠️</span>
                    <span>Low Stock</span>
                  </div>

                  <strong>
                    {insights.low_stock_products.toLocaleString()}
                  </strong>
                </div>

              </div>
            ) : (
              <div className="loading-insights">
                Loading business insights...
              </div>
            )}

          </div>

          {/* Inventory */}
          <div className="panel inventory-panel">

            <div className="panel-header">
              <div>
                <h2>📦 Inventory</h2>
                <p>Current inventory overview</p>
              </div>

              <span className="stock-status">
                Healthy
              </span>
            </div>

            <div className="inventory-stats">

              <div className="inventory-stat">
                <span>Total Stock</span>

                <strong>
                  {totalStock.toLocaleString()}
                </strong>

                <small>
                  Units available
                </small>
              </div>

              <div className="inventory-stat">
                <span>Low Stock Products</span>

                <strong>
                  {lowStockProducts.toLocaleString()}
                </strong>

                <small>
                  Require attention
                </small>
              </div>

            </div>

          </div>

        </section>
      </main>

      <footer className="footer">
        <span>MarketMind AI</span>
        <span>Business Intelligence Dashboard</span>
      </footer>
    </div>
  );
}

export default App;