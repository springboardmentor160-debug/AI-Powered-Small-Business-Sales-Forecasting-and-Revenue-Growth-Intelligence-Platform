import React, { useState, useEffect } from 'react';
import { Lock, User, ShieldCheck, ArrowRight, MapPin, ShieldAlert, Crown, Store, CreditCard, Shield, Sparkles, Check } from 'lucide-react';
import { apiLogin, getStoredDataset } from '../api';

const ROLES = [
  {
    id: 'business_owner',
    title: 'Business Owner',
    subtitle: 'Executive Access',
    icon: Crown,
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    shadowColor: 'rgba(245, 158, 11, 0.35)',
    borderGlow: '#f59e0b',
    borderDark: '#b45309',
    desc: 'Full executive oversight, sales forecasting, and customer segments across all locations.'
  },
  {
    id: 'store_manager',
    title: 'Store Manager',
    subtitle: 'Store Operations',
    icon: Store,
    gradient: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
    shadowColor: 'rgba(99, 102, 241, 0.35)',
    borderGlow: '#6366f1',
    borderDark: '#4338ca',
    desc: 'Inventory monitoring, stock replenishment, and sales for your assigned branch.'
  },
  {
    id: 'sales_executive',
    title: 'Sales Executive',
    subtitle: 'POS Terminal',
    icon: CreditCard,
    gradient: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
    shadowColor: 'rgba(6, 182, 212, 0.35)',
    borderGlow: '#06b6d4',
    borderDark: '#0e7490',
    desc: 'Point-of-sale checkout terminal for ringing customer orders and logging store sales.'
  },
  {
    id: 'administrator',
    title: 'Administrator',
    subtitle: 'System Control',
    icon: Shield,
    gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    shadowColor: 'rgba(16, 185, 129, 0.35)',
    borderGlow: '#10b981',
    borderDark: '#047857',
    desc: 'Security control: system user directory administration and technical logs.'
  }
];

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
      console.error('Error fetching locations:', e);
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
        ? (storeLocation.trim() || (availableLocations[0] || 'Store-1')) 
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

  const currentRole = ROLES.find(r => r.id === role) || ROLES[0];

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(10, 15, 30, 0.88)',
      backdropFilter: 'blur(16px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1.25rem',
      perspective: '1200px'
    }}>
      <style>{`
        @keyframes float3d {
          0%, 100% {
            transform: translateY(0px) rotateY(0deg) rotateX(0deg);
          }
          50% {
            transform: translateY(-8px) rotateY(10deg) rotateX(4deg);
          }
        }
        @keyframes pulseRings {
          0% {
            box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.5);
          }
          70% {
            box-shadow: 0 0 0 16px rgba(99, 102, 241, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
          }
        }
        @keyframes modalScaleIn {
          from {
            opacity: 0;
            transform: scale(0.93) translateY(24px) rotateX(4deg);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0) rotateX(0deg);
          }
        }
        @keyframes bgOrbGlow {
          0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.35; }
          50% { transform: translate(25px, -20px) scale(1.15); opacity: 0.55; }
        }

        .login-card-3d {
          background: linear-gradient(145deg, rgba(30, 41, 59, 0.98) 0%, rgba(15, 23, 42, 0.96) 100%);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-top: 1px solid rgba(255, 255, 255, 0.35);
          border-radius: 26px;
          padding: 2.5rem;
          max-width: 520px;
          width: 100%;
          box-shadow: 0 30px 70px rgba(0, 0, 0, 0.7), 0 0 50px rgba(99, 102, 241, 0.15);
          animation: modalScaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
          position: relative;
          overflow: hidden;
        }

        .login-icon-3d {
          animation: float3d 4s ease-in-out infinite, pulseRings 3s infinite;
          transform-style: preserve-3d;
        }

        .role-btn-3d {
          background: rgba(30, 41, 59, 0.65);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-top: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 14px;
          padding: 0.85rem 0.9rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          box-shadow: 0 4px 0 rgba(10, 15, 30, 0.9), 0 8px 16px rgba(0, 0, 0, 0.3);
          transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
          transform: translateY(0);
          user-select: none;
          text-align: left;
        }
        .role-btn-3d:hover {
          transform: translateY(-3px);
          border-color: rgba(255, 255, 255, 0.3);
          box-shadow: 0 7px 0 rgba(10, 15, 30, 0.9), 0 14px 22px rgba(0, 0, 0, 0.4);
        }
        .role-btn-3d.active {
          transform: translateY(-2px);
        }

        .btn-3d-submit {
          background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
          color: white;
          border: none;
          border-top: 1px solid rgba(255, 255, 255, 0.35);
          padding: 0.95rem 1.5rem;
          border-radius: 14px;
          font-weight: 700;
          font-size: 1rem;
          cursor: pointer;
          box-shadow: 0 5px 0 #3730a3, 0 14px 28px rgba(99, 102, 241, 0.45);
          transition: all 0.15s ease-out;
          transform: translateY(0);
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          width: 100%;
        }
        .btn-3d-submit:hover {
          transform: translateY(-2px);
          box-shadow: 0 7px 0 #3730a3, 0 18px 34px rgba(99, 102, 241, 0.55);
        }
        .btn-3d-submit:active {
          transform: translateY(4px);
          box-shadow: 0 1px 0 #3730a3, 0 6px 14px rgba(99, 102, 241, 0.35);
        }

        .input-glow:focus {
          border-color: #818cf8 !important;
          box-shadow: 0 0 15px rgba(99, 102, 241, 0.3) !important;
        }
      `}</style>

      {/* Ambient 3D Neon Background Glow */}
      <div style={{
        position: 'absolute',
        width: '320px',
        height: '320px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, transparent 70%)',
        top: '20%',
        left: '25%',
        filter: 'blur(50px)',
        pointerEvents: 'none',
        animation: 'bgOrbGlow 8s ease-in-out infinite'
      }} />

      <div style={{
        position: 'absolute',
        width: '280px',
        height: '280px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(168, 85, 247, 0.2) 0%, transparent 70%)',
        bottom: '20%',
        right: '25%',
        filter: 'blur(50px)',
        pointerEvents: 'none',
        animation: 'bgOrbGlow 8s ease-in-out infinite reverse'
      }} />

      {/* Main 3D Glassmorphism Login Card */}
      <div className="login-card-3d">
        {/* Brand Header with 3D Floating Icon */}
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <div className="login-icon-3d" style={{
            width: '64px',
            height: '64px',
            borderRadius: '18px',
            background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
            borderTop: '2px solid rgba(255, 255, 255, 0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1rem',
            boxShadow: '0 12px 25px rgba(99, 102, 241, 0.5)'
          }}>
            <ShieldCheck size={32} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: '1.85rem', fontWeight: 800, letterSpacing: '-0.03em', color: '#f8fafc' }}>
            MarketMind AI
          </h2>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginTop: '0.3rem' }}>
            Enterprise Sales Intelligence Portal
          </p>
        </div>

        {error && (
          <div style={{
            backgroundColor: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.35)',
            color: '#fca5a5',
            padding: '0.75rem 1rem',
            borderRadius: '12px',
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
          {/* Username Input with 3D Bevel */}
          <div style={{ marginBottom: '1.15rem' }}>
            <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Username
            </label>
            <div style={{ position: 'relative' }}>
              <User size={18} color="#64748b" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="text"
                className="select-input input-glow"
                style={{ width: '100%', paddingLeft: '42px', borderRadius: '12px', background: 'rgba(15, 23, 42, 0.7)' }}
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoFocus
              />
            </div>
          </div>

          {/* Password Input with 3D Bevel */}
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={18} color="#64748b" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="password"
                className="select-input input-glow"
                style={{ width: '100%', paddingLeft: '42px', borderRadius: '12px', background: 'rgba(15, 23, 42, 0.7)' }}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          {/* 3D Graphical Role Buttons (2x2 Grid) */}
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.6rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Select Operational Role
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              {ROLES.map((r) => {
                const isSelected = role === r.id;
                const IconComponent = r.icon;
                return (
                  <div
                    key={r.id}
                    onClick={() => setRole(r.id)}
                    className={`role-btn-3d ${isSelected ? 'active' : ''}`}
                    style={{
                      border: isSelected ? `2px solid ${r.borderGlow}` : '1px solid rgba(255, 255, 255, 0.1)',
                      borderTop: isSelected ? `2px solid ${r.borderGlow}` : '1px solid rgba(255, 255, 255, 0.25)',
                      boxShadow: isSelected 
                        ? `0 4px 0 ${r.borderDark}, 0 0 20px ${r.shadowColor}` 
                        : '0 4px 0 rgba(10, 15, 30, 0.9), 0 6px 12px rgba(0, 0, 0, 0.25)',
                      background: isSelected ? 'rgba(30, 41, 59, 0.95)' : 'rgba(30, 41, 59, 0.5)'
                    }}
                  >
                    <div style={{
                      width: '38px',
                      height: '38px',
                      borderRadius: '10px',
                      background: r.gradient,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: `0 4px 12px ${r.shadowColor}`,
                      flexShrink: 0
                    }}>
                      <IconComponent size={20} color="#ffffff" />
                    </div>

                    <div style={{ flex: 1, overflow: 'hidden' }}>
                      <div style={{ fontWeight: 700, fontSize: '0.84rem', color: isSelected ? '#ffffff' : '#e2e8f0', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {r.title}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: isSelected ? r.borderGlow : '#94a3b8', fontWeight: 600 }}>
                        {r.subtitle}
                      </div>
                    </div>

                    {isSelected && (
                      <div style={{ width: '18px', height: '18px', borderRadius: '50%', background: r.borderGlow, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        <Check size={12} color="#ffffff" strokeWidth={3} />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Dynamic Role Description Pill */}
            <div style={{
              marginTop: '0.75rem',
              padding: '0.65rem 0.95rem',
              borderRadius: '12px',
              backgroundColor: 'rgba(15, 23, 42, 0.65)',
              border: `1px solid ${currentRole.borderGlow}33`,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <currentRole.icon size={16} color={currentRole.borderGlow} />
              <span style={{ fontSize: '0.78rem', color: '#cbd5e1', lineHeight: 1.4 }}>
                {currentRole.desc}
              </span>
            </div>
          </div>

          {/* Dynamic Assigned Location (Only for Store Manager & Sales Executive) */}
          {(role === 'store_manager' || role === 'sales_executive') && (
            <div style={{
              marginBottom: '1.25rem',
              padding: '1rem',
              borderRadius: '14px',
              backgroundColor: 'rgba(99, 102, 241, 0.08)',
              border: '1px solid rgba(99, 102, 241, 0.25)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
            }}>
              <label style={{ display: 'block', fontSize: '0.76rem', fontWeight: 700, color: '#cbd5e1', marginBottom: '0.45rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Assigned Store Location
              </label>

              <div style={{ position: 'relative' }}>
                <MapPin size={18} color="#818cf8" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                
                {availableLocations && availableLocations.length > 0 ? (
                  <select
                    className="select-input input-glow"
                    style={{ width: '100%', paddingLeft: '40px', borderRadius: '10px' }}
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
                  <input
                    type="text"
                    className="select-input input-glow"
                    style={{ width: '100%', paddingLeft: '40px', borderRadius: '10px' }}
                    placeholder="Enter store location (e.g. Branch-1)"
                    value={storeLocation}
                    onChange={(e) => setStoreLocation(e.target.value)}
                  />
                )}
              </div>

              {availableLocations.length === 0 ? (
                <div style={{ color: '#94a3b8', fontSize: '0.74rem', marginTop: '0.45rem' }}>
                  💡 <em>No CSV imported yet. Log in as Business Owner to upload your store CSV, or type a location name above.</em>
                </div>
              ) : (
                <div style={{ color: '#34d399', fontSize: '0.74rem', marginTop: '0.45rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  ✓ <em>Loaded {availableLocations.length} locations from your imported sales dataset.</em>
                </div>
              )}
            </div>
          )}

          {/* 3D Tactile Submit Button */}
          <button 
            type="submit" 
            className="btn-3d-submit"
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Sign In to Portal'} <ArrowRight size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
