import React, { useState } from 'react';
import { Lock, User, ShieldCheck, ArrowRight, AlertCircle } from 'lucide-react';

export default function LoginModal({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!username || !password) {
      setError('Please enter username and password');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString()
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      onLoginSuccess(data);
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (usr) => {
    setUsername(usr);
    setPassword('password123');
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
        maxWidth: '440px',
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
            Role-Based Access Control Authentication
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
            <AlertCircle size={16} />
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
                placeholder="e.g. owner, manager, exec, admin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.5rem' }}>
              PASSWORD
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="password"
                className="select-input"
                style={{ width: '100%', paddingLeft: '40px' }}
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <button 
            type="submit" 
            className="btn" 
            style={{ width: '100%', padding: '0.75rem', fontSize: '0.95rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Sign In to Portal'} <ArrowRight size={16} />
          </button>
        </form>

        <div style={{ marginTop: '1.75rem', paddingTop: '1.25rem', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <div style={{ fontSize: '0.75rem', color: '#64748b', textAlign: 'center', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Demo Quick Login Shortcuts
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
            <button className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.4rem' }} onClick={() => handleQuickLogin('owner')}>
              👑 Owner
            </button>
            <button className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.4rem' }} onClick={() => handleQuickLogin('manager')}>
              🏪 Store Mgr
            </button>
            <button className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.4rem' }} onClick={() => handleQuickLogin('exec')}>
              💳 Sales Exec
            </button>
            <button className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.4rem' }} onClick={() => handleQuickLogin('admin')}>
              🛡️ Admin
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
