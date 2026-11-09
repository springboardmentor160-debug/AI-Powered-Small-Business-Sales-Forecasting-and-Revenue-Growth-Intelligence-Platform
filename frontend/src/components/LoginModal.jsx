import React, { useState, useEffect } from 'react';
import { Lock, User, ArrowRight, MapPin, ShieldAlert } from 'lucide-react';
import { apiLogin, getStoredDataset } from '../api';
import ParticleCanvas from './ParticleCanvas';

const ROLES = [
  { 
    id: 'business_owner', 
    label: 'Owner', 
    icon: '👑', 
    fullTitle: 'Business Owner',
    quote: '“True ownership isn’t just running a business—it’s mastering your margins, scaling capital, and building a legacy.”'
  },
  { 
    id: 'store_manager', 
    label: 'Manager', 
    icon: '🏪', 
    fullTitle: 'Store Manager',
    quote: '“Every aisle, every shelf, every unit. Run your store with discipline, minimize stockouts, and lead your team to daily targets.”'
  },
  { 
    id: 'sales_executive', 
    label: 'Sales', 
    icon: '💳', 
    fullTitle: 'Sales Executive',
    quote: '“Speed at the counter, smile at the register. Turn shoppers into repeat buyers and drive daily cash velocity.”'
  },
  { 
    id: 'administrator', 
    label: 'Admin', 
    icon: '🛡️', 
    fullTitle: 'Administrator',
    quote: '“Zero downtime, ironclad protection. Control access privileges, protect audit logs, and keep the infrastructure rock solid.”'
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
      {/* Animated Floating Luminous Particles / Moving Dots in Background */}
      <ParticleCanvas particleCount={48} />

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

        /* ==========================================================================
           OVERHEAD HANGING LAMP & SPOTLIGHT BEAM (Match Video Reference)
           ========================================================================== */
        .overhead-lamp-rig {
          position: absolute;
          top: 0;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          flex-direction: column;
          align-items: center;
          z-index: 5;
          pointer-events: none;
        }

        .lamp-ceiling-base {
          width: 36px;
          height: 7px;
          background: linear-gradient(180deg, #64748b 0%, #1e293b 100%);
          border-radius: 0 0 5px 5px;
          box-shadow: 0 3px 10px rgba(0, 0, 0, 0.7);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-top: none;
        }

        .lamp-wire {
          width: 2px;
          height: 75px;
          background: linear-gradient(to bottom, #94a3b8 0%, #475569 50%, #1e293b 100%);
          box-shadow: 0 0 4px rgba(0, 0, 0, 0.6);
        }

        .lamp-head {
          position: relative;
          display: flex;
          flex-direction: column;
          align-items: center;
          filter: drop-shadow(0 6px 18px rgba(0, 0, 0, 0.8));
          animation: lampGentleSway 8s ease-in-out infinite alternate;
          transform-origin: 50% -75px;
        }

        @keyframes lampGentleSway {
          0% { transform: rotate(-1.5deg); }
          50% { transform: rotate(1.2deg); }
          100% { transform: rotate(-1.2deg); }
        }

        .lamp-shade-svg {
          display: block;
        }

        /* Glowing Bulb Filament */
        .lamp-bulb-element {
          position: absolute;
          bottom: -8px;
          left: 50%;
          transform: translateX(-50%);
          width: 22px;
          height: 15px;
          border-radius: 0 0 12px 12px;
          background: radial-gradient(circle at 50% 30%, #ffffff 0%, #fef08a 45%, #fbbf24 85%, #f59e0b 100%);
          box-shadow: 
            0 0 14px #fde047,
            0 0 28px rgba(245, 158, 11, 0.95),
            0 0 60px rgba(217, 119, 6, 0.75);
          z-index: 6;
          animation: bulbPulse 3s ease-in-out infinite alternate;
        }

        @keyframes bulbPulse {
          0% { 
            filter: brightness(0.96); 
            box-shadow: 0 0 12px #fde047, 0 0 26px rgba(245, 158, 11, 0.85); 
          }
          100% { 
            filter: brightness(1.1); 
            box-shadow: 0 0 18px #fef08a, 0 0 38px rgba(251, 191, 36, 0.95), 0 0 75px rgba(245, 158, 11, 0.85); 
          }
        }

        .lamp-bulb-flare {
          position: absolute;
          bottom: -24px;
          left: 50%;
          transform: translateX(-50%);
          width: 90px;
          height: 44px;
          background: radial-gradient(ellipse at center, rgba(254, 240, 138, 0.8) 0%, rgba(251, 191, 36, 0.35) 45%, transparent 75%);
          filter: blur(10px);
          z-index: 5;
          pointer-events: none;
        }

        /* Wide Radiant Light Cone Shining Downward Over the Card */
        .lamp-light-cone {
          position: absolute;
          top: 118px;
          left: 50%;
          transform: translateX(-50%);
          width: 640px;
          height: 700px;
          background: radial-gradient(ellipse at 50% 0%, rgba(254, 240, 138, 0.28) 0%, rgba(251, 191, 36, 0.14) 35%, rgba(245, 158, 11, 0.05) 65%, transparent 85%);
          clip-path: polygon(44% 0%, 56% 0%, 100% 100%, 0% 100%);
          pointer-events: none;
          z-index: 3;
          filter: blur(8px);
          animation: coneShimmer 7s ease-in-out infinite alternate;
        }

        /* Inner High-Intensity Core Light Beam */
        .lamp-light-core {
          position: absolute;
          top: 118px;
          left: 50%;
          transform: translateX(-50%);
          width: 480px;
          height: 600px;
          background: radial-gradient(ellipse at 50% 0%, rgba(255, 255, 255, 0.38) 0%, rgba(254, 240, 138, 0.22) 32%, transparent 70%);
          clip-path: polygon(46% 0%, 54% 0%, 92% 100%, 8% 100%);
          pointer-events: none;
          z-index: 4;
          filter: blur(14px);
        }

        @keyframes coneShimmer {
          0% { opacity: 0.88; transform: translateX(-50%) scaleX(0.98); }
          50% { opacity: 1; transform: translateX(-50%) scaleX(1.02); }
          100% { opacity: 0.92; transform: translateX(-50%) scaleX(1); }
        }

        /* Responsive lamp cord height */
        @media (max-height: 800px) {
          .lamp-wire { height: 45px; }
          .lamp-light-cone { top: 88px; height: 560px; }
          .lamp-light-core { top: 88px; height: 500px; }
        }

        @media (max-width: 640px) {
          .lamp-light-cone { width: 380px; }
          .lamp-light-core { width: 320px; }
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

        /* Minimalist Centered Glass Card Bathing Under the Overhead Light */
        .portal-card {
          background: rgba(11, 15, 29, 0.78);
          backdrop-filter: blur(28px);
          -webkit-backdrop-filter: blur(28px);
          border: 1px solid rgba(255, 255, 255, 0.16);
          border-top: 1.5px solid rgba(254, 240, 138, 0.65);
          border-radius: 28px;
          padding: 2.75rem 2.5rem;
          max-width: 480px;
          width: 100%;
          box-shadow: 
            0 30px 80px rgba(0, 0, 0, 0.75), 
            0 -12px 35px rgba(251, 191, 36, 0.22),
            0 0 70px rgba(139, 92, 246, 0.26),
            0 0 35px rgba(6, 182, 212, 0.2),
            inset 0 1px 0 rgba(254, 240, 138, 0.45);
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

        @keyframes quoteFadeIn {
          from { opacity: 0; transform: translateY(5px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .role-quote-fade {
          animation: quoteFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        @media (max-width: 640px) {
          .portal-card { padding: 2rem 1.5rem; }
        }
      `}</style>

      {/* ==========================================================================
          OVERHEAD HANGING LAMP WITH DOWNWARD RADIANT LIGHT CONE
          ========================================================================== */}
      <div className="overhead-lamp-rig">
        {/* Ceiling Mount */}
        <div className="lamp-ceiling-base" />

        {/* Hanging Wire */}
        <div className="lamp-wire" />

        {/* Lamp Fixture & Shade Assembly */}
        <div className="lamp-head">
          <svg className="lamp-shade-svg" width="94" height="48" viewBox="0 0 94 48" fill="none">
            <defs>
              <linearGradient id="shadeExterior" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#64748b" />
                <stop offset="30%" stopColor="#334155" />
                <stop offset="70%" stopColor="#1e293b" />
                <stop offset="100%" stopColor="#0f172a" />
              </linearGradient>
              <linearGradient id="brassCollar" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#d97706" />
                <stop offset="50%" stopColor="#fef08a" />
                <stop offset="100%" stopColor="#b45309" />
              </linearGradient>
              <linearGradient id="innerRimGlow" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.75" />
                <stop offset="50%" stopColor="#fffbeb" stopOpacity="1" />
                <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.75" />
              </linearGradient>
            </defs>

            {/* Top Brass Collar */}
            <rect x="39" y="0" width="16" height="5" rx="1.5" fill="url(#brassCollar)" />

            {/* Flared Industrial Shade */}
            <path
              d="M37 5 L57 5 L88 40 C88 43 78 45 47 45 C16 45 6 43 6 40 Z"
              fill="url(#shadeExterior)"
              stroke="rgba(255, 255, 255, 0.22)"
              strokeWidth="1.2"
            />

            {/* Warm Golden Inner Rim */}
            <ellipse cx="47" cy="41" rx="40" ry="4" fill="none" stroke="url(#innerRimGlow)" strokeWidth="2" />
          </svg>

          {/* Glowing Filament Light Bulb */}
          <div className="lamp-bulb-element" />

          {/* Lamp Bulb Ambient Glow Flare */}
          <div className="lamp-bulb-flare" />
        </div>

        {/* Downward Light Beams */}
        <div className="lamp-light-cone" />
        <div className="lamp-light-core" />
      </div>

      {/* Centered Glassmorphic Card */}
      <div className="portal-card">
        {/* Sales Header */}
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <h1 style={{
            fontSize: '2.15rem',
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

          <p
            key={role}
            className="role-quote-fade"
            style={{
              color: '#cbd5e1',
              fontSize: '0.86rem',
              lineHeight: 1.55,
              marginTop: '0.5rem',
              maxWidth: '390px',
              margin: '0.5rem auto 0 auto',
              minHeight: '44px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
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
            <span>{loading ? 'Logging in...' : 'Login'}</span>
            <ArrowRight size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
