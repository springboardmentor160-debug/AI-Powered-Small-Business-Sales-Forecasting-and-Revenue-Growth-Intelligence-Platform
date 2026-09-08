import React, { useState } from 'react';
import { login } from '../api';

export default function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!username || !password) {
      setError('Please enter both username/email and password.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await login(username, password);
      if (data && data.user) {
        onLoginSuccess(data.user);
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = (alias) => {
    setUsername(alias);
    setPassword('password123');
    setError(null);
    // Automatically trigger login for convenient testing
    setLoading(true);
    login(alias, 'password123')
      .then((data) => {
        if (data && data.user) {
          onLoginSuccess(data.user);
        }
      })
      .catch((err) => {
        setError(err.message || 'Demo login failed.');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">M</div>
          <h2>MarketMind AI</h2>
          <p>Sales Intelligence & RBAC Platform</p>
        </div>

        {error && (
          <div className="msg-banner msg-error">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="login-username">Username or Email</label>
            <input
              id="login-username"
              type="text"
              className="form-input"
              placeholder="e.g. owner or owner@marketmind.ai"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              className="form-input"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          <button
            id="login-submit-btn"
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '8px' }}
            disabled={loading}
          >
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div className="spinner" style={{ width: '16px', height: '16px' }}></div>
                Authenticating...
              </span>
            ) : (
              'Sign In to Dashboard'
            )}
          </button>
        </form>

        <div className="demo-box">
          <div className="demo-title">Instant 1-Click Demo Accounts</div>
          <div className="demo-grid">
            <button
              id="demo-btn-owner"
              type="button"
              className="demo-btn"
              onClick={() => handleDemoLogin('owner')}
              disabled={loading}
            >
              👑 Business Owner
              <span>Role: owner</span>
            </button>
            <button
              id="demo-btn-manager"
              type="button"
              className="demo-btn"
              onClick={() => handleDemoLogin('manager')}
              disabled={loading}
            >
              📦 Store Manager
              <span>Role: manager</span>
            </button>
            <button
              id="demo-btn-exec"
              type="button"
              className="demo-btn"
              onClick={() => handleDemoLogin('exec')}
              disabled={loading}
            >
              💼 Sales Executive
              <span>Role: sales_executive</span>
            </button>
            <button
              id="demo-btn-admin"
              type="button"
              className="demo-btn"
              onClick={() => handleDemoLogin('admin')}
              disabled={loading}
            >
              🛡️ Administrator
              <span>Role: admin</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
