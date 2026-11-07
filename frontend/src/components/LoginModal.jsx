import React, { useState } from 'react';
import { Lock, User, ShieldCheck, ArrowRight, Store, ShieldAlert } from 'lucide-react';
import { apiLogin } from '../api';

export default function LoginModal({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('business_owner');
  const [storeId, setStoreId] = useState('STORE-001');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!username.trim()) {
      setError('Please enter your username');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await apiLogin(username, password, role, storeId);
      onLoginSuccess(data);
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(15, 23, 42, 0.85)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%)',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        borderRadius: '20px',
        padding: '2.5rem',
        maxWidth: '460px',
        width: '100%',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '14px',
            background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1rem',
            boxShadow: '0 0 20px rgba(99, 102, 241, 0.5)'
          }}>
            <ShieldCheck size={28} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800 }}>MarketMind AI</h2>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            Enterprise Sales & Inventory Intelligence
          </p>
        </div>

        {error && (
          <div style={{
            backgroundColor: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#fca5a5',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            fontSize: '0.85rem',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <ShieldAlert size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.5rem' }}>
              USERNAME
            </label>
            <div style={{ position: 'relative' }}>
              <User size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                className="select-input"
                style={{ width: '100%', paddingLeft: '40px' }}
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoFocus
              />
            </div>
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.5rem' }}>
              PASSWORD
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="password"
                className="select-input"
                style={{ width: '100%', paddingLeft: '40px' }}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.5rem' }}>
              SELECT OPERATIONAL ROLE
            </label>
            <select
              className="select-input"
              style={{ width: '100%' }}
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="business_owner">Business Owner (Executive Full Access)</option>
              <option value="store_manager">Store Manager (Store Inventory & Operations)</option>
              <option value="sales_executive">Sales Executive (POS Sales Terminal)</option>
              <option value="administrator">System Administrator (Full Control & User Directory)</option>
            </select>
          </div>

          {(role === 'store_manager' || role === 'sales_executive') && (
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.5rem' }}>
                ASSIGNED STORE LOCATION
              </label>
              <div style={{ position: 'relative' }}>
                <Store size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                <select
                  className="select-input"
                  style={{ width: '100%', paddingLeft: '40px' }}
                  value={storeId}
                  onChange={(e) => setStoreId(e.target.value)}
                >
                  <option value="STORE-001">Downtown Flagship (STORE-001)</option>
                  <option value="STORE-002">Uptown Outlet (STORE-002)</option>
                  <option value="STORE-003">Metro Mall Branch (STORE-003)</option>
                </select>
              </div>
            </div>
          )}

          <button 
            type="submit" 
            className="btn" 
            style={{ width: '100%', padding: '0.75rem', fontSize: '0.95rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Sign In to Portal'} <ArrowRight size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
