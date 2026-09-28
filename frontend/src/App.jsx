import { useEffect, useState } from "react";

import { fetchDashboardData } from "./api";
import ErrorState from "./components/ErrorState";
import KpiCard from "./components/KpiCard";
import LoadingState from "./components/LoadingState";
import SectionHeading from "./components/SectionHeading";
import TopProductChart from "./components/TopProductChart";

const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});
const numberFormatter = new Intl.NumberFormat("en-IN");

function formatCurrency(value) {
  return currencyFormatter.format(value || 0);
}

function formatNumber(value) {
  return numberFormatter.format(value || 0);
}

function App() {
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let isCurrent = true;

    setIsLoading(true);
    setError(null);
    fetchDashboardData()
      .then((data) => {
        if (isCurrent) {
          setDashboardData(data);
        }
      })
      .catch((requestError) => {
        if (isCurrent) {
          setError(requestError.message || "The API is unavailable.");
        }
      })
      .finally(() => {
        if (isCurrent) {
          setIsLoading(false);
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [retryCount]);

  if (isLoading) {
    return <LoadingState />;
  }

  if (error || !dashboardData) {
    return <ErrorState message={error || "No dashboard data was returned."} onRetry={() => setRetryCount((count) => count + 1)} />;
  }

  const { sales, inventory, customers } = dashboardData;
  const topProduct = sales.top_selling_product;
  const lowStockCount = inventory.products_at_or_below_reorder_threshold;
  const totalVolume = Math.max(sales.total_quantity_sold, sales.total_transactions, 1);
  const stockCoverage = inventory.total_products
    ? ((inventory.total_products - lowStockCount) / inventory.total_products) * 100
    : 0;

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="MarketMind AI home">
          <span className="brand__mark">M</span>
          <span>
            <strong>MarketMind</strong>
            <small>AI / SALES INTELLIGENCE</small>
          </span>
        </a>
        <div className="topbar__status">
          <span className="status-dot" />
          <span>Live data</span>
        </div>
      </header>

      <main className="dashboard-content">
        <section className="welcome-row">
          <div>
            <p className="eyebrow">OPERATIONS OVERVIEW</p>
            <h1>Business pulse</h1>
            <p className="welcome-row__subcopy">A clear read on sales, stock, and customer reach.</p>
          </div>
          <div className="sync-note">
            <span className="sync-note__label">Source</span>
            <strong>Processed MarketMind data</strong>
          </div>
        </section>

        <section className="kpi-grid" aria-label="Key performance indicators">
          <KpiCard label="Total revenue" value={formatCurrency(sales.total_revenue)} detail="Across all transactions" accent="coral" />
          <KpiCard label="Total transactions" value={formatNumber(sales.total_transactions)} detail="Recorded orders" accent="blue" />
          <KpiCard label="Quantity sold" value={formatNumber(sales.total_quantity_sold)} detail="Units moved" accent="gold" />
          <KpiCard label="Total customers" value={formatNumber(customers.total_customers)} detail="Customer profiles" accent="green" />
        </section>

        <section className="content-grid">
          <article className="panel panel--sales">
            <SectionHeading eyebrow="SALES SUMMARY" title="Revenue in motion" action="All transactions" />
            <div className="sales-highlight">
              <div>
                <span className="muted-label">Gross revenue</span>
                <strong>{formatCurrency(sales.total_revenue)}</strong>
              </div>
              <div className="sales-highlight__metric">
                <span className="metric-pulse">↗</span>
                <span>{formatNumber(sales.total_transactions)} orders</span>
              </div>
            </div>
            <div className="sales-bars" aria-label="Sales volume comparison">
              <div className="sales-bars__row">
                <span>Transactions</span>
                <div className="sales-bars__track"><div className="sales-bars__fill sales-bars__fill--coral" style={{ width: `${(sales.total_transactions / totalVolume) * 100}%` }} /></div>
                <strong>{formatNumber(sales.total_transactions)}</strong>
              </div>
              <div className="sales-bars__row">
                <span>Units sold</span>
                <div className="sales-bars__track"><div className="sales-bars__fill sales-bars__fill--gold" style={{ width: `${(sales.total_quantity_sold / totalVolume) * 100}%` }} /></div>
                <strong>{formatNumber(sales.total_quantity_sold)}</strong>
              </div>
            </div>
          </article>

          <article className="panel panel--product">
            <SectionHeading eyebrow="PRODUCT SIGNAL" title="What is moving" />
            <TopProductChart product={topProduct} totalQuantity={sales.total_quantity_sold} />
            <div className="product-note">
              <span className="product-note__icon">+</span>
              <p><strong>{topProduct.product_name}</strong> leads the current product mix by units sold.</p>
            </div>
          </article>

          <article className="panel panel--inventory">
            <SectionHeading eyebrow="INVENTORY SUMMARY" title="Stock position" action="Across stores" />
            <div className="inventory-stats">
              <div className="inventory-stat">
                <span className="muted-label">Products tracked</span>
                <strong>{formatNumber(inventory.total_products)}</strong>
              </div>
              <div className="inventory-stat">
                <span className="muted-label">Total stock</span>
                <strong>{formatNumber(inventory.total_stock)}</strong>
              </div>
            </div>
            <div className="stock-meter" aria-label={`${lowStockCount} products at or below reorder threshold`}>
              <div className="stock-meter__top"><span>Stock coverage</span><strong>{formatNumber(inventory.total_stock)} units</strong></div>
              <div className="stock-meter__track"><div className="stock-meter__fill" style={{ width: `${stockCoverage}%` }} /></div>
              <span className="stock-meter__caption">Inventory records connected to product and store data</span>
            </div>
          </article>

          <article className="panel panel--reorder">
            <SectionHeading eyebrow="ACTION SIGNAL" title="Low-stock / reorder" />
            <div className={`reorder-callout ${lowStockCount ? "reorder-callout--active" : ""}`}>
              <div className="reorder-callout__number">{formatNumber(lowStockCount)}</div>
              <div>
                <strong>Products at or below threshold</strong>
                <p>{lowStockCount ? "Review replenishment before availability tightens." : "No products currently need replenishment review."}</p>
              </div>
            </div>
            <div className="signal-footer"><span className="signal-footer__dot" />Based on current inventory levels</div>
          </article>

          <article className="panel panel--customers">
            <SectionHeading eyebrow="CUSTOMER SUMMARY" title="Know your reach" />
            <div className="customer-summary">
              <div className="customer-summary__age">
                <span className="muted-label">Average customer age</span>
                <strong>{customers.basic_statistics.average_age}</strong>
                <span>years</span>
              </div>
              <div className="customer-summary__list">
                <div><span>Age range</span><strong>{customers.basic_statistics.minimum_age}–{customers.basic_statistics.maximum_age}</strong></div>
                <div><span>Cities represented</span><strong>{formatNumber(customers.basic_statistics.unique_cities)}</strong></div>
              </div>
            </div>
          </article>
        </section>
      </main>
    </div>
  );
}

export default App;
