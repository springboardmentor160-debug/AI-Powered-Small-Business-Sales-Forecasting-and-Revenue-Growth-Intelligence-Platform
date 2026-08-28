import React from 'react';
import { BarChart3, Store, UserCheck } from 'lucide-react';

export default function Header({ selectedStore, setSelectedStore, activeRole, setActiveRole }) {
  return (
    <header className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <BarChart3 size={24} color="#ffffff" />
        </div>
        <div>
          <span className="brand-title">MarketMind AI</span>
          <span className="brand-badge" style={{ marginLeft: '8px' }}>v1.0 Milestone 1</span>
        </div>
      </div>

      <div className="nav-controls">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Store size={18} color="#94a3b8" />
          <select 
            className="select-input"
            value={selectedStore} 
            onChange={(e) => setSelectedStore(e.target.value)}
          >
            <option value="ALL">All Store Locations</option>
            <option value="STORE-001">Downtown Flagship (STORE-001)</option>
            <option value="STORE-002">Uptown Outlet (STORE-002)</option>
            <option value="STORE-003">Metro Mall Branch (STORE-003)</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <UserCheck size={18} color="#94a3b8" />
          <select 
            className="select-input"
            value={activeRole} 
            onChange={(e) => setActiveRole(e.target.value)}
          >
            <option value="business_owner">Business Owner (Global View)</option>
            <option value="store_manager">Store Manager (Inventory View)</option>
            <option value="sales_executive">Sales Executive (Sales View)</option>
            <option value="administrator">Administrator (System View)</option>
          </select>
        </div>
      </div>
    </header>
  );
}
