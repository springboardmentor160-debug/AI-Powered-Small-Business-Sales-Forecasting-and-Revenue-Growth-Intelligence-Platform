import React, { useEffect, useState } from 'react';
import { getAnalyticsSummary, getSales, getInventoryAlerts } from '../api';
import KPICard from '../components/KPICard';
import SalesChart from '../components/SalesChart';
import SalesTable from '../components/SalesTable';
import InventoryAlerts from '../components/InventoryAlerts';
import PlannedFeaturesNotice from '../components/PlannedFeaturesNotice';

export default function OwnerDashboard({ user }) {
  const [analytics, setAnalytics] = useState(null);
  const [sales, setSales] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        const [analyticsData, salesData, alertsData] = await Promise.all([
          getAnalyticsSummary(),
          getSales(),
          getInventoryAlerts(),
        ]);
        setAnalytics(analyticsData);
        setSales(salesData);
        setAlerts(alertsData);
      } catch (err) {
        setError(err.message || 'Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner"></div>
        <span>Loading Executive Overview...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="msg-banner msg-error">
        <span>⚠️ Error: {error}</span>
      </div>
    );
  }

  return (
    <div>
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h2>Business Owner Executive Dashboard</h2>
          <p>Strategic sales performance, revenue analytics, and operational monitoring.</p>
        </div>
        <span className="role-badge role-owner">Strategic Access</span>
      </div>

      {/* Primary KPI Grid */}
      <div className="kpi-grid">
        <KPICard
          label="Total Revenue"
          value={`₹${analytics?.total_revenue?.toFixed(2) || '0.00'}`}
          subtext="Net sales revenue from all orders"
          icon="💵"
          accent="#6366f1"
        />
        <KPICard
          label="Total Orders"
          value={analytics?.total_orders || 0}
          subtext="Validated completed transactions"
          icon="📦"
          accent="#38bdf8"
        />
        <KPICard
          label="Units Sold"
          value={analytics?.total_units || 0}
          subtext="Quantity of physical items sold"
          icon="📊"
          accent="#10b981"
        />
        <KPICard
          label="Avg Order Value"
          value={`₹${analytics?.average_order_value?.toFixed(2) || '0.00'}`}
          subtext="Mean transaction value"
          icon="📈"
          accent="#a855f7"
        />
      </div>

      {/* Grid: Sales Trend & Top Products */}
      <div className="sections-grid-2">
        <div className="glass-card">
          <div className="card-header">
            <div className="card-title">
              <span>📈</span>
              <span>Daily Sales Trend</span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>January 2026</span>
          </div>
          <div className="card-body">
            <SalesChart data={analytics?.sales_trend} />
          </div>
        </div>

        <div className="glass-card">
          <div className="card-header">
            <div className="card-title">
              <span>🏆</span>
              <span>Top Revenue Products</span>
            </div>
          </div>
          <div className="card-body" style={{ padding: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {analytics?.top_products?.map((prod, idx) => (
                <div
                  key={prod.product_name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid rgba(255, 255, 255, 0.04)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span
                      style={{
                        width: '24px',
                        height: '24px',
                        borderRadius: '50%',
                        background: idx === 0 ? 'rgba(245, 158, 11, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                        color: idx === 0 ? '#f59e0b' : 'var(--text-muted)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                      }}
                    >
                      {idx + 1}
                    </span>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>{prod.product_name}</div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                        {prod.units_sold} units sold
                      </div>
                    </div>
                  </div>
                  <div style={{ fontWeight: 700, color: '#10b981', fontSize: '0.92rem' }}>
                    ₹{prod.total_revenue.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Grid: Recent Sales & Inventory Alert Summary */}
      <div className="sections-grid-2">
        <div className="glass-card">
          <div className="card-header">
            <div className="card-title">
              <span>🧾</span>
              <span>All Verified Sales Transactions</span>
            </div>
          </div>
          <div className="card-body">
            <SalesTable sales={sales} />
          </div>
        </div>

        <div className="glass-card">
          <div className="card-header">
            <div className="card-title">
              <span>⚠️</span>
              <span>Inventory Reorder Alerts</span>
            </div>
            <span className="status-pill status-alert">{alerts.length} Items</span>
          </div>
          <div className="card-body">
            <InventoryAlerts alerts={alerts} />
          </div>
        </div>
      </div>

      {/* Transparent Milestone 2 Roadmap */}
      <PlannedFeaturesNotice
        features={[
          'Prophet & XGBoost Sales Forecasting',
          'Customer RFM & K-Means Segmentation',
          'Customer Churn Probability Engine',
          'Automated Stock Replenishment Planning',
        ]}
      />
    </div>
  );
}
