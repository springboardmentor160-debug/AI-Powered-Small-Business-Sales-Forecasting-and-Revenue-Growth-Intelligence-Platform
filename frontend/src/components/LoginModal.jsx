import React, { useState, useEffect } from 'react';
import { Lock, User, ShieldCheck, ArrowRight, MapPin, ShieldAlert, Crown, Store, CreditCard, Shield } from 'lucide-react';
import { apiLogin, getStoredDataset } from '../api';

const ROLE_INFO = {
  business_owner: {
    label: 'Business Owner',
    icon: Crown,
    color: '#f59e0b',
    desc: 'Full executive oversight, sales forecasting, and customer segments across all locations.'
  },
  store_manager: {
    label: 'Store Manager',
    icon: Store,
    color: '#6366f1',
    desc: 'Inventory monitoring, stock replenishment, and sales for an assigned branch location.'
  },
  sales_executive: {
    label: 'Sales Executive',
    icon: CreditCard,
    color: '#06b6d4',
    desc: 'Point-of-sale register terminal for recording customer sales transactions.'
  },
  administrator: {
    label: 'Administrator',
    icon: Shield,
    color: '#10b981',
    desc: 'System user directory administration, platform health, and security controls.'
  }
};

export default function LoginModal({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('business_owner');
  const [storeLocation, setStoreLocation] = useState('');
  const [availableLocations, setAvailableLocations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load locations dynamically from platform storage (populated when owner imports CSV)
  useEffect(() => {
    try {
      const ds = getStoredDataset();
      const locs = ds?.locations || [];
      setAvailableLocations(locs);
      if (locs.length > 0) {
        setStoreLocation(locs[0]);
      }
    } catch (e) {
      console.error('Error fetching locations for login modal:', e);
    }
  }, []);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!username.trim()) {
      setError('Please enter your username');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const finalStore = (role === 'store_manager' || role === 'sales_executive') 
        ? (storeLocation.trim() || 'Store-1') 
        : null;

      const data = await apiLogin(username, password, role, finalStore);
      onLoginSuccess(data);
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const currentRoleConfig = ROLE_INFO[role] || ROLE_INFO.business_owner;
  const RoleIcon = currentRoleConfig.icon;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(15, 23, 42, 0.88)',
      backdropFilter: 'blur(14px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.98) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        borderRadius: '24px',
        padding: '2.5rem',
        maxWidth: '480px',
        width: '100%',
        boxShadow: '0 25px 60px rgba(0, 0, 0, 0.65)'
      }}>
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <div style={{
            width: '60px',
            height: '60px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1rem',
            boxShadow: '0 0 25px rgba(99, 102, 241, 0.5)'
          }}>
            <ShieldCheck size={30} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc' }}>
            MarketMind AI
          </h2>
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
            borderRadius: '10px',
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
          {/* Username Input */}
          <div style={{ marginBottom: '1.15rem' }}>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Username
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

          {/* Password Input */}
          <div style={{ marginBottom: '1.15rem' }}>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Password
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

          {/* Interactive Role Selector */}
          <div style={{ marginBottom: '1.15rem' }}>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Select Operational Role
            </label>
            <select
              className="select-input"
              style={{ width: '100%' }}
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="business_owner">👑 Business Owner (Executive Full Access)</option>
              <option value="store_manager">🏪 Store Manager (Store Operations & Stock)</option>
              <option value="sales_executive">💳 Sales Executive (POS Sales Terminal)</option>
              <option value="administrator">🛡️ Administrator (System Administration & Users)</option>
            </select>

            {/* Dynamic Role Description Pill */}
            <div style={{
              marginTop: '0.6rem',
              padding: '0.6rem 0.85rem',
              borderRadius: '10px',
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              border: `1px solid ${currentRoleConfig.color}33`,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <RoleIcon size={15} color={currentRoleConfig.color} />
              <span style={{ fontSize: '0.78rem', color: '#cbd5e1', lineHeight: 1.4 }}>
                {currentRoleConfig.desc}
              </span>
            </div>
          </div>

          {/* Dynamic Assigned Location: Only shown for Store Manager and Sales Executive */}
          {(role === 'store_manager' || role === 'sales_executive') && (
            <div style={{
              marginBottom: '1.25rem',
              padding: '1rem',
              borderRadius: '12px',
              backgroundColor: 'rgba(99, 102, 241, 0.08)',
              border: '1px solid rgba(99, 102, 241, 0.2)'
            }}>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#cbd5e1', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Assigned Store Location
              </label>

              <div style={{ position: 'relative' }}>
                <MapPin size={18} color="#818cf8" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                
                {availableLocations && availableLocations.length > 0 ? (
                  /* Shows ONLY the locations imported from the user's CSV */
                  <select
                    className="select-input"
                    style={{ width: '100%', paddingLeft: '40px' }}
                    value={storeLocation}
                    onChange={(e) => setStoreLocation(e.target.value)}
                  >
                    {availableLocations.map((loc) => (
                      <option key={loc} value={loc}>
                        {loc}
                      </option>
                    ))}
                  </select>
                ) : (
                  /* If no CSV has been imported yet, allow entering a location name */
                  <input
                    type="text"
                    className="select-input"
                    style={{ width: '100%', paddingLeft: '40px' }}
                    placeholder="Enter store location (e.g. Branch-1)"
                    value={storeLocation}
                    onChange={(e) => setStoreLocation(e.target.value)}
                  />
                )}
              </div>

              {availableLocations.length === 0 ? (
                <div style={{ color: '#94a3b8', fontSize: '0.75rem', marginTop: '0.4rem' }}>
                  💡 <em>No CSV imported yet. Log in as Business Owner to upload your store CSV, or type a location name above.</em>
                </div>
              ) : (
                <div style={{ color: '#34d399', fontSize: '0.75rem', marginTop: '0.4rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  ✓ <em>Loaded {availableLocations.length} locations from your imported sales dataset.</em>
                </div>
              )}
            </div>
          )}

          {/* Submit Button */}
          <button 
            type="submit" 
            className="btn" 
            style={{ width: '100%', padding: '0.85rem', fontSize: '0.95rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginTop: '0.5rem' }}
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Sign In to Portal'} <ArrowRight size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
