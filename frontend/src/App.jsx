import React, { useState, useEffect } from 'react';
import { 
  DollarSign, ShoppingBag, TrendingUp, AlertTriangle, Layers, Award, 
  RefreshCw, Users, BarChart3, LineChart, PieChart, ShieldCheck, 
  PlusCircle, UploadCloud, Trash2, ShoppingCart, Package, Settings, Sparkles, Activity
} from 'lucide-react';

import Header from './components/Header';
import KPICard from './components/KPICard';
import SalesChart from './components/SalesChart';
import InventoryTable from './components/InventoryTable';
import TransactionsTable from './components/TransactionsTable';
import LowStockAlert from './components/LowStockAlert';
import LoginModal from './components/LoginModal';
import ForecastView from './components/ForecastView';
import SegmentationView from './components/SegmentationView';
import POSTerminal from './components/POSTerminal';
import NewSaleModal from './components/NewSaleModal';
import ImportCsvModal from './components/ImportCsvModal';

import { 
  apiGetSummary, 
  apiGetLocations,
  apiGetInventory, 
  apiGetUsers, 
  apiGetForecast, 
  apiGetSegmentation,
  recordSaleTransaction,
  importTransactionsFromCSV,
  removeAllData
} from './api';

export default function App() {
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('mm_token') || null);
  const [authUser, setAuthUser] = useState(() => {
    const saved = localStorage.getItem('mm_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [activeTab, setActiveTab] = useState('pos_register');
  const [selectedStore, setSelectedStore] = useState('ALL');
  const [locations, setLocations] = useState([]);
  const [summary, setSummary] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [forecastData, setForecastData] = useState(null);
  const [segmentationData, setSegmentationData] = useState(null);
  const [usersList, setUsersList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);

  // Modals
  const [isNewSaleOpen, setIsNewSaleOpen] = useState(false);
  const [isImportCsvOpen, setIsImportCsvOpen] = useState(false);

  useEffect(() => {
    if (authUser && authUser.store_id) {
      setSelectedStore(authUser.store_id);
    }
  }, [authUser]);

  const handleLoginSuccess = (data) => {
    setAuthToken(data.access_token);
    setAuthUser(data);
    localStorage.setItem('mm_token', data.access_token);
    localStorage.setItem('mm_user', JSON.stringify(data));
    // Default tab based on role
    if (data.role === 'sales_executive') {
      setActiveTab('pos_register');
    } else if (data.role === 'store_manager') {
      setActiveTab('inventory');
    } else {
      setActiveTab('overview');
    }
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
      const locs = await apiGetLocations();
      setLocations(locs);

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
      setError(err.message || 'Error loading records');
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
    setNotice(`✅ Logged sale for ${newTransaction.product_name} ($${newTransaction.total_amount.toFixed(2)}) at ${newTransaction.store_id}!`);
    setTimeout(() => setNotice(null), 5000);
  };

  const handleCsvImported = (rows) => {
    importTransactionsFromCSV(rows);
    setSelectedStore('ALL');
    fetchData();
    setNotice(`✅ Successfully imported ${rows.length} records! Locations and analytics updated.`);
    setTimeout(() => setNotice(null), 6000);
  };

  const handleClearAllData = () => {
    if (window.confirm('Are you sure you want to remove all data and start with an empty dashboard?')) {
      removeAllData();
      setSelectedStore('ALL');
      fetchData();
      setNotice('All data has been cleared. The platform is ready for your input.');
      setTimeout(() => setNotice(null), 4000);
    }
  };

  if (!authToken || !authUser) {
    return <LoginModal onLoginSuccess={handleLoginSuccess} />;
  }

  const activeRole = authUser.role;
  const isExecutive = activeRole === 'business_owner' || activeRole === 'administrator';
  const hasTransactions = summary && summary.total_transactions > 0;

  return (
    <div className="app-container">
      {/* Top Navbar */}
      <Header 
        selectedStore={selectedStore} 
        setSelectedStore={setSelectedStore}
        activeRole={activeRole}
        authUser={authUser}
        onLogout={handleLogout}
        locations={locations}
        onOpenNewSale={() => setIsNewSaleOpen(true)}
        onOpenImportCsv={() => setIsImportCsvOpen(true)}
      />

      <main className="main-content">
        {/* Modern Navigation Tabs Bar */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          paddingBottom: '1.25rem',
          marginBottom: '2rem',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => setActiveTab('overview')}
              className={`btn ${activeTab === 'overview' ? '' : 'btn-secondary'}`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}
            >
              <BarChart3 size={16} /> 📊 Executive Overview
            </button>

            <button
              onClick={() => setActiveTab('pos_register')}
              className={`btn ${activeTab === 'pos_register' ? '' : 'btn-secondary'}`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}
            >
              <ShoppingCart size={16} /> ⚡ POS Cash Register
            </button>

            <button
              onClick={() => setActiveTab('inventory')}
              className={`btn ${activeTab === 'inventory' ? '' : 'btn-secondary'}`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}
            >
              <Package size={16} /> 📦 Store Inventory
            </button>

            <button
              onClick={() => setActiveTab('forecast')}
              className={`btn ${activeTab === 'forecast' ? '' : 'btn-secondary'}`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}
            >
              <LineChart size={16} /> 📈 30-Day Sales Forecast
            </button>

            <button
              onClick={() => setActiveTab('segmentation')}
              className={`btn ${activeTab === 'segmentation' ? '' : 'btn-secondary'}`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}
            >
              <PieChart size={16} /> 👥 Customer Segments
            </button>

            {activeRole === 'administrator' && (
              <button
                onClick={() => setActiveTab('admin')}
                className={`btn ${activeTab === 'admin' ? '' : 'btn-secondary'}`}
                style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}
              >
                <ShieldCheck size={16} /> 🛡️ System Users
              </button>
            )}

            {isExecutive && (
              <button
                onClick={() => setActiveTab('data_tools')}
                className={`btn ${activeTab === 'data_tools' ? '' : 'btn-secondary'}`}
                style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}
              >
                <Settings size={16} /> ⚙️ Data Tools
              </button>
            )}
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#34d399', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '0.35rem 0.75rem', borderRadius: '20px' }}>
              <Activity size={12} />
              <span>Live Engine • 0ms</span>
            </div>
          </div>
        </div>

        {/* Dashboard Header Bar */}
        <div className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.75rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="page-title">
              {activeRole === 'business_owner' && 'Executive Business Dashboard'}
              {activeRole === 'store_manager' && `Store Operations (${selectedStore})`}
              {activeRole === 'sales_executive' && `Sales Terminal (${selectedStore})`}
              {activeRole === 'administrator' && 'System Administration'}
            </h1>
            <p className="page-subtitle">
              User: <strong style={{ color: '#f8fafc' }}>{authUser.username}</strong> | Role: <span className="badge badge-purple">{activeRole}</span>
              {selectedStore !== 'ALL' && <span> | Branch: <strong style={{ color: '#818cf8' }}>{selectedStore}</strong></span>}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.65rem' }}>
            <button className="btn" onClick={() => setIsNewSaleOpen(true)} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <PlusCircle size={15} /> Quick Sale
            </button>
            <button className="btn btn-secondary" onClick={fetchData} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
            </button>
          </div>
        </div>

        {/* Feedback Notice */}
        {notice && (
          <div style={{
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%)',
            border: '1px solid rgba(16, 185, 129, 0.35)',
            color: '#34d399',
            padding: '0.9rem 1.4rem',
            borderRadius: '12px',
            marginBottom: '1.5rem',
            fontSize: '0.9rem',
            fontWeight: 600,
            boxShadow: '0 8px 25px -5px rgba(16, 185, 129, 0.2)'
          }}>
            {notice}
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

        {/* TAB 1: EXECUTIVE OVERVIEW */}
        {activeTab === 'overview' && (
          <>
            {/* KPI Cards Grid */}
            <div className="kpi-grid">
              <KPICard 
                title="Total Revenue" 
                value={`$${summary ? summary.total_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'}`} 
                icon={DollarSign}
                color="#10b981"
                subtitle="Calculated sales total"
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

            {!hasTransactions ? (
              <div className="card" style={{ padding: '4rem 2rem', textAlign: 'center', marginTop: '1.5rem' }}>
                <div style={{
                  width: '68px',
                  height: '68px',
                  borderRadius: '18px',
                  background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.1) 100%)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1.5rem'
                }}>
                  <ShoppingCart size={32} color="#818cf8" />
                </div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc', marginBottom: '0.6rem' }}>
                  Ready to Start Ringing Sales
                </h2>
                <p style={{ color: '#94a3b8', maxWidth: '520px', margin: '0 auto 1.75rem', fontSize: '0.92rem', lineHeight: 1.6 }}>
                  No CSV import needed! Click below to open the interactive <strong>POS Cash Register</strong>, tap products, and ring up sales live in seconds.
                </p>
                <div style={{ display: 'flex', gap: '0.85rem', justifyContent: 'center' }}>
                  <button className="btn" onClick={() => setActiveTab('pos_register')} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '0.75rem 1.5rem', fontSize: '0.95rem' }}>
                    <ShoppingCart size={18} /> Open POS Cash Register
                  </button>
                  <button className="btn btn-secondary" onClick={() => setIsNewSaleOpen(true)} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '0.75rem 1.5rem', fontSize: '0.95rem' }}>
                    <PlusCircle size={18} /> Quick Custom Sale
                  </button>
                </div>
              </div>
            ) : (
              <>
                {summary && summary.low_stock_count > 0 && (
                  <LowStockAlert 
                    count={summary.low_stock_count} 
                    onReorderClick={() => setActiveTab('inventory')} 
                  />
                )}

                <div className="content-grid">
                  <div className="card">
                    <div className="card-title">
                      <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Layers size={18} color="#6366f1" /> Revenue by Category
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
                            <th>Units Sold</th>
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
                  <div className="card-title">Recent Sales Feed</div>
                  <TransactionsTable transactions={summary ? summary.recent_transactions : []} />
                </div>
              </>
            )}
          </>
        )}

        {/* TAB 2: INTERACTIVE POS REGISTER (NO CSV NEEDED!) */}
        {activeTab === 'pos_register' && (
          <POSTerminal 
            onSaleCompleted={handleSaleRecorded}
            currentLocation={selectedStore}
            locations={locations}
          />
        )}

        {/* TAB 3: STORE INVENTORY */}
        {activeTab === 'inventory' && (
          <div className="card">
            <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Store Inventory & Stock Levels ({selectedStore})</span>
              <span className="badge badge-purple">{inventory.length} Monitored Items</span>
            </div>
            <InventoryTable items={inventory} />
          </div>
        )}

        {/* TAB 4: 30-DAY SALES FORECAST */}
        {activeTab === 'forecast' && (
          <ForecastView forecastData={forecastData} userRole={activeRole} />
        )}

        {/* TAB 5: CUSTOMER SEGMENTS */}
        {activeTab === 'segmentation' && (
          <SegmentationView segmentationData={segmentationData} />
        )}

        {/* TAB 6: SYSTEM USERS (Admin only) */}
        {activeTab === 'admin' && activeRole === 'administrator' && (
          <div className="card">
            <div className="card-title">👥 Registered Platform Users</div>
            <div className="table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>User ID</th>
                    <th>Username</th>
                    <th>Full Name</th>
                    <th>Role</th>
                    <th>Location</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {usersList.map((u) => (
                    <tr key={u.user_id}>
                      <td style={{ fontFamily: 'monospace', color: '#818cf8' }}>#{u.user_id}</td>
                      <td style={{ fontWeight: 700 }}>{u.username}</td>
                      <td>{u.full_name}</td>
                      <td><span className="badge badge-purple">{u.role_name}</span></td>
                      <td>{u.store_id || 'All'}</td>
                      <td><span className="badge badge-success">ACTIVE</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 7: DATA TOOLS (Owner & Admin only) */}
        {activeTab === 'data_tools' && isExecutive && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
            <div className="card">
              <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <UploadCloud size={20} color="#6366f1" />
                <span>Bulk CSV Import (Optional)</span>
              </div>
              <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '1.5rem', lineHeight: 1.5 }}>
                Have existing historical sales data from Excel or POS? You can optionally import your CSV file to batch load transactions and auto-populate store locations.
              </p>
              <button 
                className="btn" 
                onClick={() => setIsImportCsvOpen(true)}
                style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              >
                <UploadCloud size={16} /> Choose CSV File to Import
              </button>
            </div>

            <div className="card">
              <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fca5a5' }}>
                <Trash2 size={20} color="#ef4444" />
                <span>Data Management & Wipe</span>
              </div>
              <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '1.5rem', lineHeight: 1.5 }}>
                Wipe all sales records, inventory, and locations from the platform to reset to an empty state for fresh testing.
              </p>
              <button 
                onClick={handleClearAllData}
                style={{
                  width: '100%',
                  padding: '0.65rem 1rem',
                  borderRadius: '10px',
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  color: '#fca5a5',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                <Trash2 size={16} /> Wipe All Records
              </button>
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
        existingLocations={locations}
      />

      {/* Import CSV Modal */}
      <ImportCsvModal 
        isOpen={isImportCsvOpen} 
        onClose={() => setIsImportCsvOpen(false)} 
        onCsvImported={handleCsvImported} 
      />

      <footer className="footer">
        MarketMind AI — Enterprise Intelligence Suite &copy; 2026. All rights reserved.
      </footer>
    </div>
  );
}
