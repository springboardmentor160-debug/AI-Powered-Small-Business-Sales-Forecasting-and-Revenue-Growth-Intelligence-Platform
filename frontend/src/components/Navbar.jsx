import React from 'react';

const ROLE_LABELS = {
  owner: 'Business Owner',
  manager: 'Store Manager',
  sales_executive: 'Sales Executive',
  admin: 'System Administrator',
};

export default function Navbar({ user, onLogout }) {
  if (!user) return null;

  const roleClass = `role-${user.role}`;
  const roleLabel = ROLE_LABELS[user.role] || user.role;

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <a href="/" className="brand">
          <div className="brand-icon">M</div>
          <div className="brand-text">
            <h1>MarketMind AI</h1>
            <span>Sales Intelligence</span>
          </div>
        </a>

        <div className="navbar-user">
          <div className="user-info-box">
            <span className="user-name">{user.name}</span>
            <span className="user-email">{user.email}</span>
          </div>

          <span className={`role-badge ${roleClass}`}>
            ● {roleLabel}
          </span>

          <button
            id="logout-button"
            className="btn btn-outline btn-sm"
            onClick={onLogout}
            title="Sign out of current account"
          >
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
}
