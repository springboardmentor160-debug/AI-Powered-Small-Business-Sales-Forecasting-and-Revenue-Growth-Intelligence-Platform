import React from 'react';
import { BarChart3, Store, LogOut, Shield } from 'lucide-react';

export default function Header({ selectedStore, setSelectedStore, activeRole, authUser, onLogout }) {
  return (
    <header className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <BarChart3 size={24} color="#ffffff" />
        </div>
        <div>
          <span className="brand-title">MarketMind AI</span>
          <span className="brand-badge" style={{ marginLeft: '8px' }}>v1.0 RBAC</span>
        </div>
      </div>

      <div className="nav-controls">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Store size={18} color="#94a3b8" />
          <select 
            className="select-input"
            value={selectedStore} 
            onChange={(e) => setSelectedStore(e.target.value)}
            disabled={activeRole === 'store_manager' || activeRole === 'sales_executive'}
          >
            <option value="ALL">All Store Locations</option>
            <option value="STORE-001">Downtown Flagship (STORE-001)</option>
            <option value="STORE-002">Uptown Outlet (STORE-002)</option>
            <option value="STORE-003">Metro Mall Branch (STORE-003)</option>
          </select>
        </div>

        {authUser && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: 'rgba(30,41,59,0.8)', padding: '0.35rem 0.85rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
            <Shield size={16} color="#818cf8" />
            <div style={{ fontSize: '0.85rem' }}>
              <span style={{ fontWeight: 700, color: '#f8fafc' }}>{authUser.username}</span>
              <span className="badge badge-purple" style={{ marginLeft: '6px', fontSize: '0.7rem' }}>
                {authUser.role}
              </span>
            </div>
            <button 
              className="btn btn-secondary" 
              onClick={onLogout}
              style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', marginLeft: '0.25rem', display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <LogOut size={12} /> Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
