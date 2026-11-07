import React, { useState, useEffect } from 'react';
import { DollarSign, ShoppingBag, TrendingUp, AlertTriangle, Layers, Award, RefreshCw, Users, BarChart3, LineChart, PieChart, ShieldCheck, PlusCircle, UploadCloud, RotateCcw } from 'lucide-react';
import Header from './components/Header';
import KPICard from './components/KPICard';
import SalesChart from './components/SalesChart';
import InventoryTable from './components/InventoryTable';
import TransactionsTable from './components/TransactionsTable';
import LowStockAlert from './components/LowStockAlert';
import LoginModal from './components/LoginModal';
import ForecastView from './components/ForecastView';
import SegmentationView from './components/SegmentationView';
import NewSaleModal from './components/NewSaleModal';
import ImportCsvModal from './components/ImportCsvModal';
import { 
  apiGetSummary, 
  apiGetInventory, 
  apiGetUsers, 
  apiGetForecast, 
  apiGetSegmentation,
  recordSaleTransaction,
  importTransactionsFromCSV,
  resetPlatformData
} from './api';

export default function App() {
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('mm_token') || null);
  const [authUser, setAuthUser] = useState(() => {
    const saved = localStorage.getItem('mm_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [activeTab, setActiveTab] = useState('pos');
  const [selectedStore, setSelectedStore] = useState('ALL');
  const [summary, setSummary] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [forecastData, setForecastData] = useState(null);
  const [segmentationData, setSegmentationData] = useState(null);
  const [usersList, setUsersList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successNotice, setSuccessNotice] = useState(null);

  // Modals
  const [isNewSaleOpen, setIsNewSaleOpen] = useState(false);
  const [isImportCsvOpen, setIsImportCsvOpen] = useState(false);

  // Sync store dropdown if user belongs to a specific store
  useEffect(() => {
    if (authUser && authUser.store_id) {
      setSelectedStore(authUser.store_id);
    } else {
      setSelectedStore('ALL');
    }
  }, [authUser]);

  const handleLoginSuccess = (data) => {
    setAuthToken(data.access_token);
    setAuthUser(data);
    localStorage.setItem('mm_token', data.access_token);
    localStorage.setItem('mm_user', JSON.stringify(data));
  };

  const handleLogout = () => {
    setAuthToken(null);
    setAuthUser(null);
    localStorage.removeItem('mm_token');
    localStorage.removeItem('mm_user');
  };

  const fetchData = async () => {
    if (!authToken) return;
    setLoading(true);
    setError(null);
    try {
      const sumData = await apiGetSummary(selectedStore);
      setSummary(sumData);

      const invData = await apiGetInventory();
      setInventory(invData);

      const fcData = await apiGetForecast();
      setForecastData(fcData);

      const segData = await apiGetSegmentation();
      setSegmentationData(segData);

      if (authUser?.role === 'administrator') {
        const uData = await apiGetUsers();
        setUsersList(uData);
      }
    } catch (err) {
      console.error('API Error:', err);
      setError(err.message || 'Error loading platform datasets');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authToken) {
      fetchData();
    }
  }, [authToken, selectedStore]);

  const handleSaleRecorded = (txn) => {
    const { newTransaction } = recordSaleTransaction(txn);
    fetchData();
    setSuccessNotice(`✅ Sale recorded successfully: ${newTransaction.product_name} (${newTransaction.quantity} units, $${newTransaction.total_amount.toFixed(2)}). Dashboard updated!`);
    setTimeout(() => setSuccessNotice(null), 5000);
  };

  const handleCsvImported = (rows) => {
    importTransactionsFromCSV(rows);
    fetchData();
    setSuccessNotice(`✅ Successfully imported ${rows.length} transactions from your custom CSV dataset. All metrics recalculated!`);
    setTimeout(() => setSuccessNotice(null), 6000);
  };

  const handleResetData = () => {
    if (window.confirm('Reset platform data back to initial clean records?')) {
      resetPlatformData();
      fetchData();
      setSuccessNotice('Platform records reset to default state.');
      setTimeout(() => setSuccessNotice(null), 4000);
    }
  };

  if (!authToken || !authUser) {
    return <LoginModal onLoginSuccess={handleLoginSuccess} />;
  }

  const activeRole = authUser.role;

  return (
    <div className="app-container">
      <Header 
        selectedStore={selectedStore} 
        setSelectedStore={setSelectedStore}
        activeRole={activeRole}
        authUser={authUser}
        onLogout={handleLogout}
        onOpenNewSale={() => setIsNewSaleOpen(true)}
        onOpenImportCsv={() => setIsImportCsvOpen(true)}
        onResetData={handleResetData}
      />

      <main className="main-content">
        {/* Navigation Tabs Bar */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          paddingBottom: '1rem',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => setActiveTab('pos')}
              className={`btn ${activeTab === 'pos' ? '' : 'btn-secondary'}`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}
            >
              <BarChart3 size={16} /> 📊 POS & Sales Intelligence
            </button>

            <button
              onClick={() => setActiveTab('forecast')}
              className={`btn ${activeTab === 'forecast' ? '' : 'btn-secondary'}`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}
            >
              <LineChart size={16} /> 📈 30-Day Sales Forecast (Prophet)
            </button>

            <button
              onClick={() => setActiveTab('segmentation')}
              className={`btn ${activeTab === 'segmentation' ? '' : 'btn-secondary'}`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}
            >
              <PieChart size={16} /> 👥 Customer Segmentation (RFM)
            </button>

            {activeRole === 'administrator' && (
              <button
                onClick={() => setActiveTab('admin')}
                className={`btn ${activeTab === 'admin' ? '' : 'btn-secondary'}`}
                style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}
              >
                <ShieldCheck size={16} /> 🛡️ RBAC Users & System Info
              </button>
            )}
          </div>

          <button 
            onClick={handleResetData}
            style={{ 
              background: 'transparent', 
              border: '1px solid rgba(255,255,255,0.1)', 
              color: '#94a3b8', 
              fontSize: '0.78rem',
              padding: '0.4rem 0.75rem',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: 'pointer'
            }}
          >
            <RotateCcw size={12} /> Reset Data
          </button>
        </div>

        {/* Dashboard Title & Refresh Bar */}
        <div className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="page-title">
              {activeRole === 'business_owner' && 'Executive Business Owner Dashboard'}
              {activeRole === 'store_manager' && `Store Manager Operations (${selectedStore})`}
              {activeRole === 'sales_executive' && `Sales Executive Terminal (${selectedStore})`}
              {activeRole === 'administrator' && 'System Administration & RBAC Control Panel'}
            </h1>
            <p className="page-subtitle">
              Active User: <strong>{authUser.username}</strong> | Role: <span className="badge badge-purple">{activeRole}</span>
              {authUser.store_id && <span> | Store: <strong style={{ color: '#818cf8' }}>{authUser.store_id}</strong></span>}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn" onClick={() => setIsNewSaleOpen(true)} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <PlusCircle size={15} /> Record Sale
            </button>
            <button className="btn btn-secondary" onClick={fetchData} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh Data
            </button>
          </div>
        </div>

        {/* Success Notice Banner */}
        {successNotice && (
          <div style={{
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: '#34d399',
            padding: '0.85rem 1.25rem',
            borderRadius: '10px',
            marginBottom: '1.5rem',
            fontSize: '0.9rem',
            fontWeight: 500
          }}>
            {successNotice}
          </div>
        )}

        {error && (
          <div className="alert-banner" style={{ marginBottom: '1.5rem' }}>
            <div className="alert-info">
              <AlertTriangle size={20} color="#ef4444" />
              <div>
                <strong>Notice:</strong> {error}
              </div>
            </div>
          </div>
        )}

        {/* TAB 1: POS & Sales Intelligence */}
        {activeTab === 'pos' && (
          <>
            {/* Low Stock Reorder Notification Banner */}
            {summary && summary.low_stock_count > 0 && (
              <LowStockAlert 
                count={summary.low_stock_count} 
                onReorderClick={() => {}} 
              />
            )}

            {/* KPI Cards Grid */}
            <div className="kpi-grid">
              <KPICard 
                title="Total Revenue" 
                value={`$${summary ? summary.total_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'}`} 
                icon={DollarSign}
                color="#10b981"
                subtitle="Calculated POS total"
              />
              <KPICard 
                title="Total Transactions" 
                value={summary ? summary.total_transactions : 0} 
                icon={ShoppingBag}
                color="#6366f1"
                subtitle="Logged sales records"
              />
              <KPICard 
                title="Units Sold" 
                value={summary ? summary.total_items_sold : 0} 
                icon={TrendingUp}
                color="#06b6d4"
                subtitle="Total merchandise volume"
              />
              <KPICard 
                title="Low Stock Items" 
                value={summary ? summary.low_stock_count : 0} 
                icon={AlertTriangle}
                color={summary && summary.low_stock_count > 0 ? '#ef4444' : '#10b981'}
                subtitle="Items below reorder limit"
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
                  <span>Store Inventory & Stock Replenishment ({selectedStore})</span>
                  <span className="badge badge-purple">{inventory.length} SKUs Monitored</span>
                </div>
                <InventoryTable items={inventory} />
              </div>
            )}

            {/* 3. SALES EXECUTIVE VIEW */}
            {activeRole === 'sales_executive' && (
              <div className="content-grid">
                <div className="card">
                  <div className="card-title">My Recent Sales Transactions ({selectedStore})</div>
                  <TransactionsTable transactions={summary ? summary.recent_transactions : []} />
                </div>
                <div className="card">
                  <div className="card-title">Store Product Catalog & Stock</div>
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
                        {inventory.slice(0, 8).map((item) => (
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
              <>
                <div className="card" style={{ marginBottom: '2rem' }}>
                  <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Users size={18} color="#6366f1" /> System User Directory
                    </span>
                    <span className="badge badge-success">Admin Scope Authorized</span>
                  </div>
                  <div className="table-container">
                    <table className="custom-table">
                      <thead>
                        <tr>
                          <th>User ID</th>
                          <th>Username</th>
                          <th>Full Name</th>
                          <th>Email</th>
                          <th>Role</th>
                          <th>Assigned Store</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {usersList.map((u) => (
                          <tr key={u.user_id}>
                            <td style={{ fontFamily: 'monospace', fontWeight: 600, color: '#818cf8' }}>#{u.user_id}</td>
                            <td style={{ fontWeight: 700 }}>{u.username}</td>
                            <td>{u.full_name}</td>
                            <td style={{ color: '#94a3b8' }}>{u.email}</td>
                            <td><span className="badge badge-purple">{u.role_name}</span></td>
                            <td>{u.store_id || 'Global'}</td>
                            <td><span className="badge badge-success">ACTIVE</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="card">
                  <div className="card-title">Infrastructure Health & Data Pipeline Logs</div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
                    <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>CLOUD STATUS</div>
                      <div style={{ color: '#34d399', fontWeight: 700, fontSize: '1.1rem', marginTop: '4px' }}>ONLINE (Vercel Edge)</div>
                    </div>
                    <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>AUTH SYSTEM</div>
                      <div style={{ color: '#818cf8', fontWeight: 700, fontSize: '1.1rem', marginTop: '4px' }}>ACTIVE (RBAC)</div>
                    </div>
                    <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>DATA ENGINE</div>
                      <div style={{ color: '#fbbf24', fontWeight: 700, fontSize: '1.1rem', marginTop: '4px' }}>DYNAMIC (Interactive)</div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </>
        )}

        {/* TAB 2: Sales Forecasting */}
        {activeTab === 'forecast' && (
          <ForecastView forecastData={forecastData} userRole={activeRole} />
        )}

        {/* TAB 3: Customer Segmentation */}
        {activeTab === 'segmentation' && (
          <SegmentationView segmentationData={segmentationData} />
        )}

        {/* TAB 4: Admin & RBAC Matrix */}
        {activeTab === 'admin' && activeRole === 'administrator' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="card">
              <div className="card-title">🔐 Enterprise Role-Based Access Control (RBAC) Matrix</div>
              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>Platform Capability / Route</th>
                      <th>Business Owner</th>
                      <th>Store Manager</th>
                      <th>Sales Executive</th>
                      <th>Administrator</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style={{ fontWeight: 600 }}>POS Sales KPIs (/analytics/summary)</td>
                      <td><span className="badge badge-success">Full Access</span></td>
                      <td><span className="badge badge-purple">STORE-001 Isolated</span></td>
                      <td><span className="badge badge-purple">Personal Sales</span></td>
                      <td><span className="badge badge-success">Full Access</span></td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Customer RFM Segments (/segments)</td>
                      <td><span className="badge badge-success">Full Access</span></td>
                      <td><span className="badge badge-success">Full Access</span></td>
                      <td><span className="badge badge-success">Full Access</span></td>
                      <td><span className="badge badge-success">Full Access</span></td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Sales Forecasting (/forecast/revenue)</td>
                      <td><span className="badge badge-success">Full Access</span></td>
                      <td><span className="badge badge-purple">View Only</span></td>
                      <td><span className="badge badge-danger">403 Restricted</span></td>
                      <td><span className="badge badge-success">Full Access</span></td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>User Management (/api/v1/users)</td>
                      <td><span className="badge badge-secondary">No Access</span></td>
                      <td><span className="badge badge-secondary">No Access</span></td>
                      <td><span className="badge badge-secondary">No Access</span></td>
                      <td><span className="badge badge-success">Full Access</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="card">
              <div className="card-title">👥 Registered User Accounts</div>
              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>User ID</th>
                      <th>Username</th>
                      <th>Full Name</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Assigned Store</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {usersList.map((u) => (
                      <tr key={u.user_id}>
                        <td style={{ fontFamily: 'monospace', fontWeight: 600, color: '#818cf8' }}>#{u.user_id}</td>
                        <td style={{ fontWeight: 700 }}>{u.username}</td>
                        <td>{u.full_name}</td>
                        <td style={{ color: '#94a3b8' }}>{u.email}</td>
                        <td><span className="badge badge-purple">{u.role_name}</span></td>
                        <td>{u.store_id || 'Global'}</td>
                        <td><span className="badge badge-success">ACTIVE</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Record New Sale Modal */}
      <NewSaleModal 
        isOpen={isNewSaleOpen} 
        onClose={() => setIsNewSaleOpen(false)} 
        onSaleRecorded={handleSaleRecorded} 
        defaultStore={selectedStore} 
      />

      {/* Import CSV Modal */}
      <ImportCsvModal 
        isOpen={isImportCsvOpen} 
        onClose={() => setIsImportCsvOpen(false)} 
        onCsvImported={handleCsvImported} 
      />

      <footer className="footer">
        MarketMind AI — Enterprise Sales Intelligence Platform &copy; 2026. All rights reserved.
      </footer>
    </div>
  );
}
