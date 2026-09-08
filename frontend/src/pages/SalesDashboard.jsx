import React, { useEffect, useState } from 'react';
import { getSales, getSalesSummary } from '../api';
import KPICard from '../components/KPICard';
import SalesTable from '../components/SalesTable';
import PlannedFeaturesNotice from '../components/PlannedFeaturesNotice';

export default function SalesDashboard({ user }) {
  const [sales, setSales] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [salesData, summaryData] = await Promise.all([
          getSales(),
          getSalesSummary(),
        ]);
        setSales(salesData);
        setSummary(summaryData);
      } catch (err) {
        setError(err.message || 'Failed to load sales data.');
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
        <span>Loading Sales Representative Dashboard...</span>
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

  // Aggregate unique customers
  const uniqueCustomers = new Set(sales.map((s) => s.customer_name)).size;

  return (
    <div>
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h2>Sales Executive Workspace</h2>
          <p>Order transactions, client accounts, invoice status, and sales records.</p>
        </div>
        <span className="role-badge role-sales_executive">Sales Representative</span>
      </div>

      {/* Sales Executive KPIs */}
      <div className="kpi-grid">
        <KPICard
          label="Orders Closed"
          value={summary?.total_orders || 0}
          subtext="Completed sales orders"
          icon="💼"
          accent="#06b6d4"
        />
        <KPICard
          label="Total Value Invoiced"
          value={`$${summary?.total_revenue?.toFixed(2) || '0.00'}`}
          subtext="Gross billed amount"
          icon="💰"
          accent="#10b981"
        />
        <KPICard
          label="Active Accounts"
          value={uniqueCustomers}
          subtext="Customers transacted with"
          icon="👥"
          accent="#6366f1"
        />
        <KPICard
          label="Top Purchased Item"
          value={summary?.top_product || 'N/A'}
          subtext="Most frequent customer selection"
          icon="⭐"
          accent="#f59e0b"
        />
      </div>

      {/* Sales Transactions & Invoices Table */}
      <div className="glass-card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <div className="card-title">
            <span>📝</span>
            <span>Customer Sales Orders & Payment Settlement</span>
          </div>
        </div>
        <div className="card-body">
          <SalesTable sales={sales} />
        </div>
      </div>

      {/* Distinct Customer Account Summary */}
      <div className="glass-card" style={{ marginBottom: '32px' }}>
        <div className="card-header">
          <div className="card-title">
            <span>🏢</span>
            <span>Commercial Accounts Summary</span>
          </div>
        </div>
        <div className="card-body">
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Customer Code</th>
                  <th>Customer Name</th>
                  <th>Total Orders Placed</th>
                  <th>Total Spend</th>
                </tr>
              </thead>
              <tbody>
                {Array.from(
                  sales.reduce((acc, s) => {
                    const key = s.customer_id;
                    if (!acc.has(key)) {
                      acc.set(key, {
                        code: s.customer_id,
                        name: s.customer_name,
                        orders: 0,
                        total: 0.0,
                      });
                    }
                    const item = acc.get(key);
                    item.orders += 1;
                    item.total += s.total_amount;
                    return acc;
                  }, new Map()).values()
                ).map((cust) => (
                  <tr key={cust.code}>
                    <td style={{ fontWeight: 700, color: '#38bdf8' }}>{cust.code}</td>
                    <td style={{ fontWeight: 600 }}>{cust.name}</td>
                    <td>{cust.orders} transactions</td>
                    <td style={{ fontWeight: 700, color: '#10b981' }}>
                      ${cust.total.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <PlannedFeaturesNotice
        features={[
          'Personal Commission Calculator',
          'Client Re-Engagement Reminders',
          'Lead Opportunity Scoring',
        ]}
      />
    </div>
  );
}
