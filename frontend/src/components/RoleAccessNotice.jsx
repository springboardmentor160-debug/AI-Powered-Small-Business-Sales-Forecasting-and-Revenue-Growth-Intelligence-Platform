export default function RoleAccessNotice({ user, onLogout }) {
  return (
    <main className="role-access-shell">
      <section className="role-access-panel">
        <span className="brand__mark">M</span>
        <p className="eyebrow">{user.role}</p>
        <h1>Your workspace is being prepared.</h1>
        <p>
          You are signed in as <strong>{user.name}</strong>. The current Day 9-10 build protects this role while its permitted transaction and customer workflows are added in their planned milestone.
        </p>
        <div className="role-access-panel__scope">
          <span className="muted-label">Current access</span>
          <strong>Customer summary</strong>
          <small>Sales dashboard, inventory policy, forecasting, and churn views are not available for this role.</small>
        </div>
        <button className="button button--dark" onClick={onLogout} type="button">Log out</button>
      </section>
    </main>
  );
}
