import React, { useState, useEffect } from 'react';
import { Lock, User, ArrowRight, MapPin, Sparkles, ShieldAlert, Check } from 'lucide-react';
import { apiLogin, getStoredDataset } from '../api';

const ROLES = [
  { id: 'business_owner', label: 'Owner', icon: '👑', fullTitle: 'Business Owner' },
  { id: 'store_manager', label: 'Manager', icon: '🏪', fullTitle: 'Store Manager' },
  { id: 'sales_executive', label: 'Sales', icon: '💳', fullTitle: 'Sales Executive' },
  { id: 'administrator', label: 'Admin', icon: '🛡️', fullTitle: 'Administrator' }
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

  return (
    <div className="login-viewport">
      <style>{`
        .login-viewport {
          position: fixed;
          inset: 0;
          background: 
            radial-gradient(circle at 85% 15%, #24134a 0%, transparent 42%),
            radial-gradient(circle at 15% 85%, #0f1c3f 0%, transparent 38%),
            linear-gradient(135deg, #0B0F19 0%, #070A10 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 1.5rem;
          overflow: hidden;
          perspective: 1200px;
        }

        /* 15-Second Drift Loops for 3D Floating Elements */
        @keyframes driftSphere1 {
          0%, 100% { transform: translate(0, 0) scale(1) rotate(0deg); }
          33% { transform: translate(30px, -45px) scale(1.08) rotate(4deg); }
          66% { transform: translate(-25px, 20px) scale(0.96) rotate(-3deg); }
        }
        @keyframes driftSphere2 {
          0%, 100% { transform: translate(0, 0) scale(1) rotate(0deg); }
          33% { transform: translate(-35px, 30px) scale(1.1) rotate(-5deg); }
          66% { transform: translate(25px, -35px) scale(0.94) rotate(4deg); }
        }
        @keyframes floatSticker {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-16px) rotate(8deg); }
        }
        @keyframes floatStickerSlow {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(-10deg); }
        }
        @keyframes pulseGlow {
          0%, 100% { opacity: 0.35; filter: blur(40px); }
          50% { opacity: 0.6; filter: blur(55px); }
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
        @keyframes shimmerBtn {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }

        .floating-orb {
          position: absolute;
          border-radius: 50%;
          pointer-events: none;
          mix-blend-mode: screen;
        }

        .orb-purple {
          width: 380px;
          height: 380px;
          background: radial-gradient(circle, rgba(168, 85, 247, 0.28) 0%, rgba(30, 17, 69, 0.1) 60%, transparent 75%);
          top: 8%;
          right: 12%;
          animation: driftSphere1 15s ease-in-out infinite;
        }

        .orb-blue {
          width: 340px;
          height: 340px;
          background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, rgba(15, 23, 42, 0.05) 60%, transparent 75%);
          bottom: 10%;
          left: 10%;
          animation: driftSphere2 15s ease-in-out infinite;
        }

        /* Glass Floating Emoji Stickers */
        .glass-sticker {
          position: absolute;
          width: 52px;
          height: 52px;
          border-radius: 16px;
          background: rgba(255, 255, 255, 0.04);
          backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.12);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
          pointer-events: none;
          z-index: 1;
        }

        .sticker-brain {
          top: 15%;
          left: 18%;
          animation: floatSticker 7s ease-in-out infinite;
        }
        .sticker-rocket {
          bottom: 18%;
          left: 22%;
          animation: floatStickerSlow 9s ease-in-out infinite;
        }
        .sticker-chart {
          top: 22%;
          right: 18%;
          animation: floatStickerSlow 8s ease-in-out infinite;
        }
        .sticker-briefcase {
          bottom: 22%;
          right: 20%;
          animation: floatSticker 10s ease-in-out infinite;
        }

        /* Minimalist Centered Glass Card */
        .portal-card {
          background: rgba(18, 24, 38, 0.75);
          backdrop-filter: blur(28px);
          -webkit-backdrop-filter: blur(28px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-top: 1px solid rgba(255, 255, 255, 0.25);
          border-radius: 28px;
          padding: 2.75rem 2.5rem;
          max-width: 480px;
          width: 100%;
          box-shadow: 
            0 30px 80px rgba(0, 0, 0, 0.75), 
            0 0 60px rgba(124, 58, 237, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
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
          .glass-sticker { display: none; }
          .portal-card { padding: 2rem 1.5rem; }
        }
      `}</style>

      {/* Floating 3D Spheres with 15s Drift Loop */}
      <div className="floating-orb orb-purple" />
      <div className="floating-orb orb-blue" />

      {/* Vibrant Neon Glass Stickers */}
      <div className="glass-sticker sticker-brain">🧠</div>
      <div className="glass-sticker sticker-rocket">🚀</div>
      <div className="glass-sticker sticker-chart">📈</div>
      <div className="glass-sticker sticker-briefcase">💼</div>

      {/* Centered Glassmorphic Command Center Card */}
      <div className="portal-card">
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '0.35rem 0.85rem',
            borderRadius: '20px',
            background: 'rgba(99, 102, 241, 0.12)',
            border: '1px solid rgba(99, 102, 241, 0.28)',
            color: '#a5b4fc',
            fontSize: '0.72rem',
            fontWeight: 700,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginBottom: '0.85rem'
          }}>
            <Sparkles size={12} color="#818cf8" /> MarketMind AI
          </div>

          <h1 style={{
            fontSize: '1.9rem',
            fontWeight: 800,
            letterSpacing: '-0.03em',
            color: '#f8fafc',
            margin: 0,
            background: 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Intelligence Portal
          </h1>

          {/* Motivational Business Quote */}
          <p style={{
            color: '#94a3b8',
            fontSize: '0.86rem',
            lineHeight: 1.55,
            marginTop: '0.5rem',
            maxWidth: '400px',
            margin: '0.5rem auto 0 auto'
          }}>
            <em>“Empowering decisions. Accelerating growth. Welcome to your intelligence command center.”</em> 🚀
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

          {/* Launch Command Center Button */}
          <button
            type="submit"
            className="btn-launch-command"
            disabled={loading}
          >
            <span>{loading ? 'Authenticating...' : 'Enter Command Center'}</span>
            <ArrowRight size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
