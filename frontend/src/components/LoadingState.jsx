export default function LoadingState() {
  return (
    <main className="loading-state" aria-live="polite">
      <div className="loading-state__mark" />
      <p>Reading your business data...</p>
    </main>
  );
}
