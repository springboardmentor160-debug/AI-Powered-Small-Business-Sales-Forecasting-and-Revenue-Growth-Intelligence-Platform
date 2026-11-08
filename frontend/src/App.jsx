import React, { useState, useEffect } from 'react';
import { DollarSign, ShoppingBag, TrendingUp, AlertTriangle, Layers, Award, RefreshCw, Users, BarChart3, LineChart, PieChart, ShieldCheck, PlusCircle, UploadCloud, Trash2, Sparkles } from 'lucide-react';
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
  apiGetLocations,
  apiGetInventory, 
  apiGetUsers, 
  apiGetForecast, 
  apiGetSegmentation,
  recordSaleTransaction,
  importTransactionsFromCSV,
  removeAllData,
  loadSampleDataset
} from './api';

export default function App() {
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('mm_token') || null);
  const [authUser, setAuthUser] = useState(() => {
    const saved = localStorage.getItem('mm_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [activeTab, setActiveTab] = useState('pos');
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
    setNotice(`✅ Recorded sale for ${newTransaction.product_name} ($${newTransaction.total_amount.toFixed(2)}) at ${newTransaction.store_id}!`);
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

  const handleLoadSample = () => {
    loadSampleDataset();
    setSelectedStore('ALL');
    fetchData();
    setNotice('Sample data loaded for demonstration.');
    setTimeout(() => setNotice(null), 4000);
  };

  if (!authToken || !authUser) {
    return <LoginModal onLoginSuccess={handleLoginSuccess} />;
  }

  const activeRole = authUser.role;
  const hasTransactions = summary && summary.total_transactions > 0;

  return (
    <div className="app-container">
      <Header 
        selectedStore={selectedStore} 
        setSelectedStore={setSelectedStore}
        activeRole={activeRole}
        authUser={authUser}
        onLogout={handleLogout}
        locations={locations}
        onOpenNewSale={() => setIsNewSaleOpen(true)}
        onOpenImportCsv={() => setIsImportCsvOpen(true)}
        onClearAllData={handleClearAllData}
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
              <BarChart3 size={16} /> 📊 POS & Sales
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
          </div>

          {(activeRole === 'business_owner' || activeRole === 'administrator') && (
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <button
                onClick={handleClearAllData}
                style={{
                  background: 'transparent',
                  border: '1px solid rgba(239, 68, 68, 0.25)',
                  color: '#fca5a5',
                  fontSize: '0.78rem',
                  padding: '0.4rem 0.75rem',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  cursor: 'pointer'
                }}
                title="Remove all data from dashboard"
              >
                <Trash2 size={13} /> Clear Data
              </button>

              {!hasTransactions && (
                <button
                  onClick={handleLoadSample}
                  style={{
                    background: 'transparent',
                    border: '1px solid rgba(99, 102, 241, 0.3)',
                    color: '#818cf8',
                    fontSize: '0.78rem',
                    padding: '0.4rem 0.75rem',
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                    cursor: 'pointer'
                  }}
                >
                  <Sparkles size={13} /> Sample Data
                </button>
              )}
            </div>
          )}
        </div>

        {/* Dashboard Title & Actions Bar */}
        <div className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="page-title">
              {activeRole === 'business_owner' && 'Executive Business Dashboard'}
              {activeRole === 'store_manager' && `Store Manager Operations (${selectedStore})`}
              {activeRole === 'sales_executive' && `Sales Terminal (${selectedStore})`}
              {activeRole === 'administrator' && 'System Administration'}
            </h1>
            <p className="page-subtitle">
              User: <strong>{authUser.username}</strong> | Role: <span className="badge badge-purple">{activeRole}</span>
              {selectedStore !== 'ALL' && <span> | Location: <strong style={{ color: '#818cf8' }}>{selectedStore}</strong></span>}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn" onClick={() => setIsNewSaleOpen(true)} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <PlusCircle size={15} /> Record Sale
            </button>
            <button className="btn btn-secondary" onClick={fetchData} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
            </button>
          </div>
        </div>

        {/* Feedback Notice */}
        {notice && (
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

        {/* TAB 1: POS & Sales */}
        {activeTab === 'pos' && (
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

            {/* Empty State Banner if 0 records */}
            {!hasTransactions ? (
              <div className="card" style={{ padding: '3.5rem 2rem', textAlign: 'center', marginTop: '1.5rem' }}>
                <div style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '16px',
                  backgroundColor: 'rgba(99, 102, 241, 0.12)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1.25rem'
                }}>
                  <ShoppingBag size={30} color="#818cf8" />
                </div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.5rem' }}>
                  No Sales Records Yet
                </h2>
                <p style={{ color: '#94a3b8', maxWidth: '480px', margin: '0 auto 1.5rem', fontSize: '0.9rem', lineHeight: 1.6 }}>
                  Start by recording an individual sale or import your sales CSV file. The dashboard will automatically calculate your revenue, product rankings, and locations.
                </p>
                <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
                  <button className="btn" onClick={() => setIsNewSaleOpen(true)} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <PlusCircle size={16} /> Record First Sale
                  </button>
                  {(activeRole === 'business_owner' || activeRole === 'administrator') && (
                    <button className="btn btn-secondary" onClick={() => setIsImportCsvOpen(true)} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <UploadCloud size={16} /> Import CSV File
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <>
                {/* Low Stock Banner */}
                {summary && summary.low_stock_count > 0 && (
                  <LowStockAlert 
                    count={summary.low_stock_count} 
                    onReorderClick={() => {}} 
                  />
                )}

                {/* ROLE VIEWS */}
                {activeRole === 'business_owner' && (
                  <>
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
                      <div className="card-title">Recent Sales Feed</div>
                      <TransactionsTable transactions={summary ? summary.recent_transactions : []} />
                    </div>
                  </>
                )}

                {activeRole === 'store_manager' && (
                  <div className="card">
                    <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Store Inventory ({selectedStore})</span>
                      <span className="badge badge-purple">{inventory.length} Items</span>
                    </div>
                    <InventoryTable items={inventory} />
                  </div>
                )}

                {activeRole === 'sales_executive' && (
                  <div className="content-grid">
                    <div className="card">
                      <div className="card-title">Recent Transactions ({selectedStore})</div>
                      <TransactionsTable transactions={summary ? summary.recent_transactions : []} />
                    </div>
                    <div className="card">
                      <div className="card-title">Store Products</div>
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

                {activeRole === 'administrator' && (
                  <div className="card">
                    <div className="card-title">Recent Sales Activity</div>
                    <TransactionsTable transactions={summary ? summary.recent_transactions : []} />
                  </div>
                )}
              </>
            )}
          </>
        )}

        {/* TAB 2: Sales Forecasting */}
        {activeTab === 'forecast' && (
          <ForecastView forecastData={forecastData} userRole={activeRole} />
        )}

        {/* TAB 3: Customer Segments */}
        {activeTab === 'segmentation' && (
          <SegmentationView segmentationData={segmentationData} />
        )}

        {/* TAB 4: System Users (Admin only) */}
        {activeTab === 'admin' && activeRole === 'administrator' && (
          <div className="card">
            <div className="card-title">👥 Registered Users</div>
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
        MarketMind AI &copy; 2026. All rights reserved.
      </footer>
    </div>
  );
}
