import React from 'react';
import { BarChart3, MapPin, LogOut, Shield, PlusCircle, UploadCloud } from 'lucide-react';

export default function Header({ 
  selectedStore, 
  setSelectedStore, 
  activeRole, 
  authUser, 
  onLogout,
  locations = [],
  onOpenNewSale,
  onOpenImportCsv
}) {
  const isExecutive = activeRole === 'business_owner' || activeRole === 'administrator';

  return (
    <header className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <BarChart3 size={24} color="#ffffff" />
        </div>
        <div>
          <span className="brand-title">MarketMind AI</span>
        </div>
      </div>

      <div className="nav-controls" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
        {/* Record Sale is available to all roles */}
        <button
          onClick={onOpenNewSale}
          className="btn"
          style={{ padding: '0.45rem 0.85rem', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          <PlusCircle size={15} /> Record Sale
        </button>

        {/* Import CSV is STRICTLY restricted to Business Owner and Administrator */}
        {isExecutive && (
          <button
            onClick={onOpenImportCsv}
            className="btn btn-secondary"
            style={{ padding: '0.45rem 0.85rem', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <UploadCloud size={15} /> Import CSV
          </button>
        )}

        {/* Dynamic Location Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <MapPin size={17} color="#94a3b8" />
          <select 
            className="select-input"
            value={selectedStore} 
            onChange={(e) => setSelectedStore(e.target.value)}
            disabled={activeRole === 'store_manager' || activeRole === 'sales_executive'}
            style={{ fontSize: '0.85rem', minWidth: '150px' }}
          >
            <option value="ALL">All Locations</option>
            {locations && locations.map((loc) => (
              <option key={loc} value={loc}>
                {loc}
              </option>
            ))}
          </select>
        </div>

        {authUser && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', background: 'rgba(30,41,59,0.8)', padding: '0.35rem 0.85rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
            <Shield size={15} color="#818cf8" />
            <div style={{ fontSize: '0.85rem' }}>
              <span style={{ fontWeight: 700, color: '#f8fafc' }}>{authUser.username}</span>
              <span className="badge badge-purple" style={{ marginLeft: '6px', fontSize: '0.7rem' }}>
                {authUser.role}
              </span>
            </div>
            <button 
              className="btn btn-secondary" 
              onClick={onLogout}
              style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem', marginLeft: '0.25rem', display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <LogOut size={12} /> Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
