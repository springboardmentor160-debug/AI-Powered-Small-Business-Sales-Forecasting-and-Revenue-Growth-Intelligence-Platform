import { useState } from "react";

import { login } from "../api";

const demoRoles = [
  ["Business Owner", "owner@marketmind.local", "Owner123!"],
  ["Store Manager", "manager@marketmind.local", "Manager123!"],
  ["Sales Executive", "sales@marketmind.local", "Sales123!"],
  ["System Administrator", "admin@marketmind.local", "Admin123!"],
];

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSubmitting(true);
    setError("");
    try {
      const session = await login(email, password);
      onLogin(session);
    } catch (requestError) {
      setError(requestError.message || "Unable to sign in.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function fillDemoUser(demoEmail, demoPassword) {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError("");
  }

  return (
    <main className="login-shell">
      <section className="login-panel">
        <div className="login-panel__intro">
          <span className="brand__mark">M</span>
          <p className="eyebrow">MARKETMIND AI</p>
          <h1>See the business clearly.</h1>
          <p>Sign in to the sales intelligence workspace for your role.</p>
        </div>
        <form className="login-form" onSubmit={handleSubmit}>
          <label htmlFor="email">Email address</label>
          <input id="email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          <label htmlFor="password">Password</label>
          <input id="password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          {error ? <p className="form-error" role="alert">{error}</p> : null}
          <button className="button button--dark login-form__submit" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <div className="demo-access">
          <p className="muted-label">Local role access</p>
          <div className="demo-access__grid">
            {demoRoles.map(([role, demoEmail, demoPassword]) => (
              <button key={role} className="demo-access__role" onClick={() => fillDemoUser(demoEmail, demoPassword)} type="button">
                <strong>{role}</strong>
                <span>Use demo account</span>
              </button>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
