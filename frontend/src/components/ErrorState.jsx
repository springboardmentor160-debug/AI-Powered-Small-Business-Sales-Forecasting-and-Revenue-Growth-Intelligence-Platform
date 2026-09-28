export default function ErrorState({ message, onRetry }) {
  return (
    <main className="error-state" role="alert">
      <span className="error-state__badge">!</span>
      <div>
        <p className="section-heading__eyebrow">Connection issue</p>
        <h1>We could not load the dashboard.</h1>
        <p>{message}</p>
        <button className="button button--dark" onClick={onRetry} type="button">
          Try again
        </button>
      </div>
    </main>
  );
}
