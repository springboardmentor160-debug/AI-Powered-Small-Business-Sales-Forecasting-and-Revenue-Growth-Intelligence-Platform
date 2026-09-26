import React, { useEffect, useState } from 'react';
import { getInventory, getInventoryAlerts, getSales, getSalesSummary } from '../api';
import KPICard from '../components/KPICard';
import InventoryAlerts from '../components/InventoryAlerts';
import SalesTable from '../components/SalesTable';
import PlannedFeaturesNotice from '../components/PlannedFeaturesNotice';
import CustomerSegmentation from '../components/CustomerSegmentation';
import SalesForecast from '../components/SalesForecast';


export default function ManagerDashboard({ user }) {
  const [inventory, setInventory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [sales, setSales] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [invData, alertsData, salesData, summaryData] = await Promise.all([
          getInventory(),
          getInventoryAlerts(),
          getSales(),
          getSalesSummary(),
        ]);
        setInventory(invData);
        setAlerts(alertsData);
        setSales(salesData);
        setSummary(summaryData);
      } catch (err) {
        setError(err.message || 'Failed to load store operations data.');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner"></div>
        <span>Loading Store Inventory & Operations...</span>
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

  const totalStockUnits = inventory.reduce((sum, item) => sum + item.stock_level, 0);

  return (
    <div>
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h2>Store Manager Operations Dashboard</h2>
          <p>Real-time inventory levels, replenishment tracking, and daily fulfillment.</p>
        </div>
        <span className="role-badge role-manager">Operational Access</span>
      </div>

      {/* Operational KPI Grid */}
      <div className="kpi-grid">
        <KPICard
          label="Total Stock on Hand"
          value={`${totalStockUnits} units`}
          subtext="Across all product categories"
          icon="📦"
          accent="#10b981"
        />
        <KPICard
          label="Reorder Alerts"
          value={alerts.length}
          subtext="Items below reorder threshold"
          icon="⚠️"
          accent={alerts.length > 0 ? '#ef4444' : '#10b981'}
        />
        <KPICard
          label="Total Sales Volume"
          value={summary?.total_orders || 0}
          subtext="Fulfillments recorded"
          icon="🛒"
          accent="#38bdf8"
        />
        <KPICard
          label="Net Store Revenue"
          value={`₹${summary?.total_revenue?.toFixed(2) || '0.00'}`}
          subtext="Total revenue generated"
          icon="💵"
          accent="#6366f1"
        />
      </div>

      {/* Low Stock Alerts Section */}
      <div className="glass-card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <div className="card-title">
            <span>🚨</span>
            <span>Immediate Replenishment Alerts ({alerts.length} Items)</span>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Trigger: stock_level &lt; reorder_point
          </span>
        </div>
        <div className="card-body">
          <InventoryAlerts alerts={alerts} />
        </div>
      </div>

      {/* Product Stock Catalog Table */}
      <div className="glass-card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <div className="card-title">
            <span>📋</span>
            <span>Complete Inventory Stock Status</span>
          </div>
        </div>
        <div className="card-body">
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Product Name</th>
                  <th>Category</th>
                  <th>Unit Price</th>
                  <th>Stock on Hand</th>
                  <th>Reorder Point</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {inventory.map((item) => (
                  <tr key={item.id}>
                    <td style={{ fontWeight: 600 }}>{item.product_name}</td>
                    <td>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        {item.category}
                      </span>
                    </td>
                    <td>₹{item.unit_price.toFixed(2)}</td>
                    <td style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                      {item.stock_level} units
                    </td>
                    <td>{item.reorder_point} units</td>
                    <td>
                      {item.is_low_stock ? (
                        <span className="status-pill status-alert">Low Stock</span>
                      ) : (
                        <span className="status-pill status-healthy">Healthy</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Store Sales Transactions */}
      <div className="glass-card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <div className="card-title">
            <span>🧾</span>
            <span>Recent Store Fulfillment Transactions</span>
          </div>
        </div>
        <div className="card-body">
          <SalesTable sales={sales} />
        </div>
      </div>

      {/* Milestone 2: Customer Segmentation & Multi-Model Sales Forecasting */}
      <CustomerSegmentation />
      <SalesForecast />

      <PlannedFeaturesNotice
        features={[
          'Milestone 3: AI Product Recommendations Engine (/recommendations)',
          'Milestone 3: Automated Supplier Reorder & Stock Replenishment Planning',
        ]}
      />
    </div>
  );
}

