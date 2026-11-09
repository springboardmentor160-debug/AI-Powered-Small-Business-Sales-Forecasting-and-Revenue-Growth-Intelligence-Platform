import React, { useState, useEffect } from 'react';
import { Lock, User, ArrowRight, MapPin, ShieldAlert } from 'lucide-react';
import { apiLogin, getStoredDataset } from '../api';

const ROLES = [
  { 
    id: 'business_owner', 
    label: 'Owner', 
    icon: '👑', 
    fullTitle: 'Business Owner',
    quote: '“Visionary leadership builds empires. Own your market, scale revenue, and command the future.”'
  },
  { 
    id: 'store_manager', 
    label: 'Manager', 
    icon: '🏪', 
    fullTitle: 'Store Manager',
    quote: '“Operational precision drives consistency. Master inventory velocity, empower teams, and optimize daily store flow.”'
  },
  { 
    id: 'sales_executive', 
    label: 'Sales', 
    icon: '💳', 
    fullTitle: 'Sales Executive',
    quote: '“Every transaction matters. Connect with customers, spark immediate loyalty, and close every deal with confidence.”'
  },
  { 
    id: 'administrator', 
    label: 'Admin', 
    icon: '🛡️', 
    fullTitle: 'Administrator',
    quote: '“Integrity is the bedrock of scale. Safeguard data reliability, enforce governance, and ensure flawless system control.”'
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

  useEffect(() => {
    try {
      const ds = getStoredDataset();
      const locs = ds?.locations || [];
      setAvailableLocations(locs);
      if (locs.length > 0) {
        setStoreLocation(locs[0]);
      }
    } catch (e) {
      console.error('Error reading locations:', e);
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

  const currentRoleObj = ROLES.find(r => r.id === role) || ROLES[0];

  return (
    <div className="login-viewport">
      <style>{`
        .login-viewport {
          position: fixed;
          inset: 0;
          background: transparent;
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 1.5rem;
          overflow: hidden;
          perspective: 1200px;
        }

        /* Luxury Subtle Grid Overlay */
        .luxury-grid-overlay {
          position: absolute;
          inset: 0;
          background-image: 
            linear-gradient(to right, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
          background-size: 44px 44px;
          mask-image: radial-gradient(ellipse 75% 65% at 50% 50%, #000 30%, transparent 85%);
          -webkit-mask-image: radial-gradient(ellipse 75% 65% at 50% 50%, #000 30%, transparent 85%);
          pointer-events: none;
        }

        /* Ambient Horizon Spotlight Beam */
        .top-light-beam {
          position: absolute;
          top: -120px;
          left: 50%;
          transform: translateX(-50%);
          width: 700px;
          height: 350px;
          background: radial-gradient(ellipse at center, rgba(168, 85, 247, 0.45) 0%, rgba(6, 182, 212, 0.25) 45%, transparent 70%);
          filter: blur(65px);
          pointer-events: none;
        }

        /* Dynamic Drift Loops for Vivid Glowing Aurora Orbs */
        @keyframes driftSphere1 {
          0% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(50px, 40px) scale(1.15); }
          100% { transform: translate(15px, 80px) scale(0.95); }
        }
        @keyframes driftSphere2 {
          0% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(-60px, 50px) scale(1.18); }
          100% { transform: translate(-25px, 90px) scale(0.92); }
        }
        @keyframes driftSphere3 {
          0% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(-45px, -50px) scale(1.12); }
          100% { transform: translate(-70px, -20px) scale(0.96); }
        }
        @keyframes driftSphere4 {
          0% { transform: translate(0, 0) scale(1); }
          50% { transform: translate(50px, -45px) scale(1.15); }
          100% { transform: translate(80px, -70px) scale(0.94); }
        }
        @keyframes cardEntrance {
          from {
            opacity: 0;
            transform: scale(0.95) translateY(20px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }

        .floating-orb {
          position: absolute;
          border-radius: 50%;
          pointer-events: none;
          mix-blend-mode: screen;
        }

        .orb-violet {
          width: 540px;
          height: 540px;
          background: radial-gradient(circle, #8b5cf6 0%, #a855f7 35%, rgba(124, 58, 237, 0) 70%);
          top: -80px;
          left: -80px;
          filter: blur(80px);
          opacity: 0.7;
          animation: driftSphere1 14s ease-in-out infinite alternate;
        }

        .orb-cyan {
          width: 500px;
          height: 500px;
          background: radial-gradient(circle, #00f2fe 0%, #06b6d4 35%, rgba(14, 165, 233, 0) 70%);
          top: -60px;
          right: -60px;
          filter: blur(80px);
          opacity: 0.65;
          animation: driftSphere2 16s ease-in-out infinite alternate;
        }

        .orb-pink {
          width: 480px;
          height: 480px;
          background: radial-gradient(circle, #f43f5e 0%, #ec4899 35%, rgba(244, 63, 94, 0) 70%);
          bottom: -80px;
          right: 2%;
          filter: blur(85px);
          opacity: 0.6;
          animation: driftSphere3 18s ease-in-out infinite alternate;
        }

        .orb-blue {
          width: 460px;
          height: 460px;
          background: radial-gradient(circle, #3b82f6 0%, #6366f1 35%, rgba(59, 130, 246, 0) 70%);
          bottom: -80px;
          left: 5%;
          filter: blur(85px);
          opacity: 0.65;
          animation: driftSphere4 15s ease-in-out infinite alternate;
        }

        /* Minimalist Centered Glass Card */
        .portal-card {
          background: rgba(11, 15, 29, 0.74);
          backdrop-filter: blur(28px);
          -webkit-backdrop-filter: blur(28px);
          border: 1px solid rgba(255, 255, 255, 0.16);
          border-top: 1px solid rgba(255, 255, 255, 0.4);
          border-radius: 28px;
          padding: 2.75rem 2.5rem;
          max-width: 480px;
          width: 100%;
          box-shadow: 
            0 30px 80px rgba(0, 0, 0, 0.75), 
            0 0 70px rgba(139, 92, 246, 0.28),
            0 0 35px rgba(6, 182, 212, 0.22),
            inset 0 1px 0 rgba(255, 255, 255, 0.35);
          position: relative;
          z-index: 10;
          animation: cardEntrance 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        /* Minimalist Segmented Slider */
        .segmented-slider {
          display: flex;
          background: rgba(10, 15, 26, 0.7);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 14px;
          padding: 4px;
          gap: 4px;
          margin-bottom: 1.25rem;
          position: relative;
        }

        .segment-pill {
          flex: 1;
          background: transparent;
          border: none;
          color: #94a3b8;
          padding: 0.55rem 0.4rem;
          border-radius: 10px;
          font-size: 0.82rem;
          font-weight: 600;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
          user-select: none;
        }

        .segment-pill:hover {
          color: #f8fafc;
          background: rgba(255, 255, 255, 0.04);
        }

        .segment-pill.active {
          background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
          color: #ffffff;
          box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.3);
          transform: translateY(-1px);
        }

        /* Clean Minimalist Input Styling */
        .minimal-input-wrap {
          position: relative;
          margin-bottom: 1.15rem;
        }

        .minimal-input {
          width: 100%;
          background: rgba(10, 15, 26, 0.65);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 14px;
          padding: 0.85rem 1rem 0.85rem 2.75rem;
          color: #f8fafc;
          font-size: 0.92rem;
          outline: none;
          transition: all 0.25s ease;
          box-sizing: border-box;
        }

        .minimal-input::placeholder {
          color: #64748b;
          font-size: 0.88rem;
        }

        .minimal-input:focus {
          border-color: #818cf8;
          background: rgba(15, 23, 42, 0.85);
          box-shadow: 0 0 20px rgba(99, 102, 241, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .input-icon-left {
          position: absolute;
          left: 14px;
          top: 50%;
          transform: translateY(-50%);
          color: #64748b;
          transition: color 0.2s ease;
          pointer-events: none;
        }

        .minimal-input:focus + .input-icon-left,
        .minimal-input-wrap:focus-within .input-icon-left {
          color: #818cf8;
        }

        /* Client-Facing Gradient Button */
        .btn-launch-command {
          width: 100%;
          background: linear-gradient(135deg, #6366f1 0%, #7c3aed 50%, #ec4899 100%);
          background-size: 200% 100%;
          color: white;
          border: none;
          border-top: 1px solid rgba(255, 255, 255, 0.35);
          padding: 0.95rem 1.5rem;
          border-radius: 14px;
          font-weight: 700;
          font-size: 0.98rem;
          letter-spacing: -0.01em;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          box-shadow: 0 12px 28px rgba(124, 58, 237, 0.4), 0 4px 0 #4c1d95;
          transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
          transform: translateY(0);
          margin-top: 0.75rem;
        }

        .btn-launch-command:hover {
          transform: translateY(-2px);
          box-shadow: 0 16px 36px rgba(124, 58, 237, 0.55), 0 6px 0 #4c1d95;
          background-position: 100% 0;
        }

        .btn-launch-command:active {
          transform: translateY(3px);
          box-shadow: 0 6px 14px rgba(124, 58, 237, 0.35), 0 1px 0 #4c1d95;
        }

        @media (max-width: 640px) {
          .portal-card { padding: 2rem 1.5rem; }
        }
      `}</style>

      {/* Centered Glassmorphic Card */}
      <div className="portal-card">
        {/* Sales Header */}
        <div style={{ textAlign: 'center', marginBottom: '1.6rem' }}>
          <h1 style={{
            fontSize: '2.1rem',
            fontWeight: 800,
            letterSpacing: '-0.025em',
            margin: 0,
            background: 'linear-gradient(135deg, #ffffff 0%, #c4b5fd 45%, #67e8f9 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            filter: 'drop-shadow(0 2px 12px rgba(139, 92, 246, 0.35))'
          }}>
            SalesPulse
          </h1>

          <p style={{
            color: '#cbd5e1',
            fontSize: '0.86rem',
            lineHeight: 1.55,
            marginTop: '0.45rem',
            maxWidth: '390px',
            margin: '0.45rem auto 0 auto',
            minHeight: '44px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.3s ease'
          }}>
            <em>{currentRoleObj.quote}</em>
          </p>
        </div>

        {error && (
          <div style={{
            backgroundColor: 'rgba(239, 68, 68, 0.14)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#fca5a5',
            padding: '0.7rem 0.9rem',
            borderRadius: '12px',
            fontSize: '0.83rem',
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
          {/* Elegant Segmented Slider Role Selector */}
          <div style={{ marginBottom: '0.4rem' }}>
            <label style={{
              display: 'block',
              fontSize: '0.72rem',
              fontWeight: 700,
              color: '#64748b',
              marginBottom: '0.45rem',
              textTransform: 'uppercase',
              letterSpacing: '0.06em'
            }}>
              Operational Scope
            </label>
            <div className="segmented-slider">
              {ROLES.map((r) => (
                <button
                  type="button"
                  key={r.id}
                  onClick={() => setRole(r.id)}
                  className={`segment-pill ${role === r.id ? 'active' : ''}`}
                >
                  <span>{r.icon}</span>
                  <span>{r.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Username Input */}
          <div className="minimal-input-wrap">
            <input
              type="text"
              className="minimal-input"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
            />
            <User size={17} className="input-icon-left" />
          </div>

          {/* Password Input */}
          <div className="minimal-input-wrap">
            <input
              type="password"
              className="minimal-input"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Lock size={17} className="input-icon-left" />
          </div>

          {/* Location Picker (Only for Manager & Sales) */}
          {(role === 'store_manager' || role === 'sales_executive') && (
            <div className="minimal-input-wrap" style={{
              animation: 'cardEntrance 0.3s ease-out'
            }}>
              {availableLocations && availableLocations.length > 0 ? (
                <select
                  className="minimal-input"
                  style={{ cursor: 'pointer' }}
                  value={storeLocation}
                  onChange={(e) => setStoreLocation(e.target.value)}
                >
                  {availableLocations.map((loc) => (
                    <option key={loc} value={loc} style={{ background: '#0f172a' }}>
                      {loc}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  className="minimal-input"
                  placeholder="Store location (e.g. Branch-1)"
                  value={storeLocation}
                  onChange={(e) => setStoreLocation(e.target.value)}
                />
              )}
              <MapPin size={17} className="input-icon-left" />
            </div>
          )}

          {/* Sign In Button */}
          <button
            type="submit"
            className="btn-launch-command"
            disabled={loading}
          >
            <span>{loading ? 'Authenticating...' : 'Enter SalesPulse'}</span>
            <ArrowRight size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
