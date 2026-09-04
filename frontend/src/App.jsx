import React, { useState } from 'react';

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [emailInput, setEmailInput] = useState('owner@marketmind.ai');
  const [errorMessage, setErrorMessage] = useState('');

  const fetchDashboard = (role) => {
    fetch(`http://127.0.0.1:8000/api/dashboard/${role}`)
      .then((res) => res.json())
      .then((data) => setDashboardData(data))
      .catch((err) => console.error("Error loading dashboard:", err));
  };

  const handleLogin = (e) => {
    e.preventDefault();
    setErrorMessage('');

    fetch('http://127.0.0.1:8000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: emailInput }),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error('Invalid email address');
        return res.json();
      })
      .then((user) => {
        setCurrentUser(user);
        fetchDashboard(user.role);
      })
      .catch((err) => setErrorMessage(err.message));
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setDashboardData(null);
  };

  // 1. LOGIN SCREEN
  if (!currentUser) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', backgroundColor: '#f1f5f9', fontFamily: 'Segoe UI, sans-serif' }}>
        <div style={{ background: '#fff', padding: '32px', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', width: '380px' }}>
          <h2 style={{ marginTop: 0, color: '#0f172a' }}>MarketMind AI</h2>
          <p style={{ color: '#64748b', fontSize: '14px' }}>Sign in with an authorized role email:</p>

          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '6px' }}>Email Address</label>
              <input
                type="email"
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #cbd5e1', boxSizing: 'border-box' }}
                required
              />
            </div>

            {errorMessage && <p style={{ color: '#dc2626', fontSize: '13px', marginBottom: '12px' }}>{errorMessage}</p>}

            <button type="submit" style={{ width: '100%', padding: '10px', backgroundColor: '#2563eb', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}>
              Sign In
            </button>
          </form>

          <div style={{ marginTop: '20px', borderTop: '1px solid #e2e8f0', paddingTop: '12px', fontSize: '12px', color: '#64748b' }}>
            <p style={{ margin: '4px 0' }}><strong>Quick Test Emails:</strong></p>
            <p style={{ margin: '2px 0', cursor: 'pointer', color: '#2563eb' }} onClick={() => setEmailInput('owner@marketmind.ai')}>• owner@marketmind.ai (Business Owner)</p>
            <p style={{ margin: '2px 0', cursor: 'pointer', color: '#2563eb' }} onClick={() => setEmailInput('manager@marketmind.ai')}>• manager@marketmind.ai (Store Manager)</p>
            <p style={{ margin: '2px 0', cursor: 'pointer', color: '#2563eb' }} onClick={() => setEmailInput('sales@marketmind.ai')}>• sales@marketmind.ai (Sales Executive)</p>
            <p style={{ margin: '2px 0', cursor: 'pointer', color: '#2563eb' }} onClick={() => setEmailInput('admin@marketmind.ai')}>• admin@marketmind.ai (Administrator)</p>
          </div>
        </div>
      </div>
    );
  }

  // 2. DASHBOARD VIEW (RBAC RENDERED)
  return (
    <div style={{ fontFamily: 'Segoe UI, sans-serif', padding: '24px', backgroundColor: '#f8fafc', minHeight: '100vh', color: '#1e293b' }}>
      {/* Top Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '1px solid #e2e8f0', paddingBottom: '16px' }}>
        <div>
          <h2 style={{ margin: 0 }}>MarketMind AI Platform</h2>
          <span style={{ fontSize: '14px', color: '#64748b' }}>
            Logged in as: <strong>{currentUser.name}</strong> ({currentUser.email})
          </span>
        </div>
        <div>
          <span style={{ display: 'inline-block', backgroundColor: '#e0e7ff', color: '#3730a3', padding: '6px 12px', borderRadius: '20px', fontSize: '13px', fontWeight: 600, marginRight: '12px' }}>
            Role: {currentUser.role}
          </span>
          <button onClick={handleLogout} style={{ padding: '6px 12px', backgroundColor: '#ef4444', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
            Logout
          </button>
        </div>
      </header>

      {dashboardData && (
        <>
          {/* Dynamic KPI Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: `repeat(${dashboardData.cards.length}, 1fr)`, gap: '16px', marginBottom: '24px' }}>
            {dashboardData.cards.map((card, idx) => (
              <div key={idx} style={{ background: '#fff', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <span style={{ fontSize: '13px', color: '#64748b' }}>{card.label}</span>
                <h2 style={{ margin: '8px 0 0', color: card.alert ? '#dc2626' : '#0f172a' }}>{card.value}</h2>
              </div>
            ))}
          </div>

          {/* Role-Specific Panels */}
          <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            {currentUser.role === 'Business Owner' && (
              <div>
                <h3>Executive Portfolio Overview</h3>
                <p>{dashboardData.sections.strategy_note}</p>
                <h4>Customer Segments Breakdown</h4>
                <ul>
                  {Object.entries(dashboardData.sections.customer_segments).map(([seg, count]) => (
                    <li key={seg}><strong>{seg}:</strong> {count} users</li>
                  ))}
                </ul>
              </div>
            )}

            {currentUser.role === 'Store Manager' && (
              <div>
                <h3>Inventory & Store Operations</h3>
                <p style={{ color: '#dc2626', fontWeight: 600 }}>{dashboardData.sections.inventory_action}</p>
              </div>
            )}

            {currentUser.role === 'Sales Executive' && (
              <div>
                <h3>Top 5 High Demand Products</h3>
                <ul>
                  {Object.entries(dashboardData.sections.top_products).map(([prod, rev]) => (
                    <li key={prod} style={{ marginBottom: '6px' }}><strong>{prod}:</strong> ${rev.toLocaleString()} in sales</li>
                  ))}
                </ul>
              </div>
            )}

            {currentUser.role === 'Administrator' && (
              <div>
                <h3>System User Management</h3>
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '12px' }}>
                  <thead>
                    <tr style={{ background: '#f8fafc', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>
                      <th style={{ padding: '8px' }}>User ID</th>
                      <th style={{ padding: '8px' }}>Name</th>
                      <th style={{ padding: '8px' }}>Email</th>
                      <th style={{ padding: '8px' }}>Assigned Role</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboardData.sections.user_list.map((u) => (
                      <tr key={u.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                        <td style={{ padding: '8px' }}>{u.id}</td>
                        <td style={{ padding: '8px' }}>{u.name}</td>
                        <td style={{ padding: '8px' }}>{u.email}</td>
                        <td style={{ padding: '8px' }}><strong>{u.role}</strong></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default App;