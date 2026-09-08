import React, { useState, useEffect } from 'react';
import { getStoredUser, clearSession, getCurrentUser, setStoredUser } from './api';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import OwnerDashboard from './pages/OwnerDashboard';
import ManagerDashboard from './pages/ManagerDashboard';
import SalesDashboard from './pages/SalesDashboard';
import AdminDashboard from './pages/AdminDashboard';

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      const cachedUser = getStoredUser();
      if (cachedUser) {
        try {
          // Verify with backend /api/v1/auth/me
          const verifiedUser = await getCurrentUser();
          setUser(verifiedUser);
          setStoredUser(verifiedUser);
        } catch {
          // Token invalid or expired
          clearSession();
          setUser(null);
        }
      }
      setLoading(false);
    }

    checkAuth();

    const handleAuthExpired = () => {
      clearSession();
      setUser(null);
    };

    window.addEventListener('auth-expired', handleAuthExpired);
    return () => window.removeEventListener('auth-expired', handleAuthExpired);
  }, []);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    clearSession();
    setUser(null);
  };

  if (loading) {
    return (
      <div className="login-wrap">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <span>Initializing MarketMind AI...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  const renderDashboardByRole = () => {
    switch (user.role) {
      case 'owner':
        return <OwnerDashboard user={user} />;
      case 'manager':
        return <ManagerDashboard user={user} />;
      case 'sales_executive':
        return <SalesDashboard user={user} />;
      case 'admin':
        return <AdminDashboard user={user} />;
      default:
        return (
          <div className="glass-card" style={{ padding: '32px', textAlign: 'center' }}>
            <h3>Unrecognized Role: {user.role}</h3>
            <p style={{ color: 'var(--text-muted)', marginTop: '8px' }}>
              Please contact the system administrator to assign an active role.
            </p>
          </div>
        );
    }
  };

  return (
    <div className="app-container">
      <Navbar user={user} onLogout={handleLogout} />
      <main className="main-content">{renderDashboardByRole()}</main>
    </div>
  );
}
