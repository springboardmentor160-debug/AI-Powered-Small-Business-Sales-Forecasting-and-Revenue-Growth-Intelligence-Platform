import React, { useState } from "react";
import { UtensilsCrossed } from "lucide-react";

const DEMO_ACCOUNTS = [
  { label: "Franchise Owner", username: "owner" },
  { label: "Outlet Manager", username: "manager" },
  { label: "Waiter", username: "waiter" },
  { label: "Admin", username: "admin" },
];

export default function LoginScreen({ onLogin, error, loading }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const submit = (e) => {
    e.preventDefault();
    onLogin(username, password);
  };

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="brand-icon-lg">
          <UtensilsCrossed color="#fff" size={26} />
        </div>
        <h1>MarketMind</h1>
        <p className="subtitle">Restaurant Chain Revenue Intelligence</p>

        {error && <div className="login-error">{error}</div>}

        <form onSubmit={submit}>
          <label>Username</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="e.g. owner" />
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="password123" />
          <button type="submit" className="login-submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="demo-accounts">
          <p>QUICK DEMO LOGIN</p>
          <div className="demo-grid">
            {DEMO_ACCOUNTS.map((acc) => (
              <button
                key={acc.username}
                className="demo-btn"
                onClick={() => onLogin(acc.username, "password123")}
              >
                {acc.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
