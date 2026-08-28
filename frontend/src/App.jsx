import React, { useState, useEffect } from 'react';
import { DollarSign, ShoppingBag, TrendingUp, AlertTriangle, Layers, Award, RefreshCw } from 'lucide-react';
import Header from './components/Header';
import KPICard from './components/KPICard';
import SalesChart from './components/SalesChart';
import InventoryTable from './components/InventoryTable';
import TransactionsTable from './components/TransactionsTable';
import LowStockAlert from './components/LowStockAlert';

const API_BASE = 'http://localhost:8000/api/v1';

export default function App() {
  const [selectedStore, setSelectedStore] = useState('ALL');
  const [activeRole, setActiveRole] = useState('business_owner');
  
  const [summary, setSummary] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const storeParam = selectedStore !== 'ALL' ? `?store_id=${selectedStore}` : '';
      
      // Fetch summary analytics
      const sumRes = await fetch(`${API_BASE}/analytics/summary${storeParam}`);
      if (!sumRes.ok) throw new Error('Failed to fetch summary metrics');
      const sumData = await sumRes.json();
      setSummary(sumData);

      // Fetch inventory list
      const invRes = await fetch(`${API_BASE}/inventory`);
      if (!invRes.ok) throw new Error('Failed to fetch inventory dataset');
      const invData = await invRes.json();
      setInventory(invData);
    } catch (err) {
      console.error('API Error:', err);
      setError(err.message || 'Error connecting to backend API');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedStore]);

  return (
    <div className="app-container">
      <Header 
        selectedStore={selectedStore} 
        setSelectedStore={setSelectedStore}
        activeRole={activeRole}
        setActiveRole={setActiveRole}
      />

      <main className="main-content">
        <div className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 className="page-title">
              {activeRole === 'business_owner' && 'Executive Business Owner Dashboard'}
              {activeRole === 'store_manager' && 'Store Operations & Inventory Hub'}
              {activeRole === 'sales_executive' && 'Sales Executive POS Terminal'}
              {activeRole === 'administrator' && 'System Administration & Control Center'}
            </h1>
            <p className="page-subtitle">
              {selectedStore === 'ALL' ? 'Real-time multi-store aggregate analytics' : `Filtered metrics for location ${selectedStore}`}
            </p>
          </div>

          <button className="btn btn-secondary" onClick={fetchData} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh Data
          </button>
        </div>

        {error && (
          <div className="alert-banner" style={{ marginBottom: '2rem' }}>
            <div className="alert-info">
              <AlertTriangle size={20} color="#ef4444" />
              <div>
                <strong>Backend Server Disconnected:</strong> {error}. Ensure backend is running at <code>http://localhost:8000</code>.
              </div>
            </div>
          </div>
        )}

        {/* Low Stock Reorder Notification Banner */}
        {summary && summary.low_stock_count > 0 && (
          <LowStockAlert 
            count={summary.low_stock_count} 
            onReorderClick={() => setActiveRole('store_manager')} 
          />
        )}

        {/* KPI Cards Grid */}
        <div className="kpi-grid">
          <KPICard 
            title="Total Revenue" 
            value={`$${summary ? summary.total_revenue.toLocaleString() : '0.00'}`} 
            icon={DollarSign}
            color="#10b981"
            subtitle="Gross POS line-item total"
          />
          <KPICard 
            title="Total Transactions" 
            value={summary ? summary.total_transactions : 0} 
            icon={ShoppingBag}
            color="#6366f1"
            subtitle="Processed sales orders"
          />
          <KPICard 
            title="Units Sold" 
            value={summary ? summary.total_items_sold : 0} 
            icon={TrendingUp}
            color="#06b6d4"
            subtitle="Total merchandise volume"
          />
          <KPICard 
            title="Low Stock Reorders" 
            value={summary ? summary.low_stock_count : 0} 
            icon={AlertTriangle}
            color={summary && summary.low_stock_count > 0 ? '#ef4444' : '#10b981'}
            subtitle="Items requiring replenishment"
          />
        </div>

        {/* ROLE-SPECIFIC VIEWS */}

        {/* 1. BUSINESS OWNER VIEW */}
        {activeRole === 'business_owner' && (
          <>
            <div className="content-grid">
              <div className="card">
                <div className="card-title">
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Layers size={18} color="#6366f1" /> Revenue Breakdown by Category
                  </span>
                </div>
                <SalesChart data={summary ? summary.category_breakdown : []} />
              </div>

              <div className="card">
                <div className="card-title">
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Award size={18} color="#f59e0b" /> Top Performing Products
                  </span>
                </div>
                <div className="table-container">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>Product</th>
                        <th>Units</th>
                        <th>Revenue</th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary && summary.top_products.map((tp, idx) => (
                        <tr key={idx}>
                          <td style={{ fontWeight: 600 }}>{tp.product_name}</td>
                          <td>{tp.units_sold}</td>
                          <td style={{ fontWeight: 700, color: '#10b981' }}>${tp.revenue.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-title">Recent Network Sales Feed</div>
              <TransactionsTable transactions={summary ? summary.recent_transactions : []} />
            </div>
          </>
        )}

        {/* 2. STORE MANAGER VIEW */}
        {activeRole === 'store_manager' && (
          <div className="card">
            <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Store Inventory & Reorder Management</span>
              <span className="badge badge-purple">{inventory.length} SKUs Monitored</span>
            </div>
            <InventoryTable items={inventory} />
          </div>
        )}

        {/* 3. SALES EXECUTIVE VIEW */}
        {activeRole === 'sales_executive' && (
          <div className="content-grid">
            <div className="card">
              <div className="card-title">Recent Terminal Sales History</div>
              <TransactionsTable transactions={summary ? summary.recent_transactions : []} />
            </div>
            <div className="card">
              <div className="card-title">Quick Product Lookup</div>
              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Price</th>
                      <th>Stock</th>
                    </tr>
                  </thead>
                  <tbody>
                    {inventory.slice(0, 7).map((item) => (
                      <tr key={item.product_id}>
                        <td style={{ fontWeight: 600 }}>{item.product_name}</td>
                        <td style={{ color: '#10b981', fontWeight: 600 }}>${item.unit_price.toFixed(2)}</td>
                        <td style={{ fontWeight: 700, color: item.needs_reorder ? '#ef4444' : '#f8fafc' }}>
                          {item.stock_level}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* 4. ADMINISTRATOR VIEW */}
        {activeRole === 'administrator' && (
          <div className="card">
            <div className="card-title">System Infrastructure & Database Audit</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>FASTAPI BACKEND</div>
                <div style={{ color: '#34d399', fontWeight: 700, fontSize: '1.1rem', marginTop: '4px' }}>ONLINE (Port 8000)</div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>SQLITE PERSISTENCE</div>
                <div style={{ color: '#818cf8', fontWeight: 700, fontSize: '1.1rem', marginTop: '4px' }}>{summary ? summary.total_transactions : 0} Records</div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>ETL CLEANING PIPELINE</div>
                <div style={{ color: '#fbbf24', fontWeight: 700, fontSize: '1.1rem', marginTop: '4px' }}>ACTIVE (clean_data.py)</div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>SECURITY MODULE</div>
                <div style={{ color: '#c084fc', fontWeight: 700, fontSize: '1.1rem', marginTop: '4px' }}>RBAC Layer Ready</div>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        MarketMind AI — Small Business Sales Intelligence Platform &copy; 2026. All rights reserved.
      </footer>
    </div>
  );
}
