import { ChurnPanel, RecommendationsPanel } from "../M3Panels";

export default function CustomersView({ role, token, churn, insightsLoading, onSessionExpired }) {
  const canSeeChurn = role === "owner" || role === "admin";
  return (
    <div className="space-y-5">
      <RecommendationsPanel token={token} onSessionExpired={onSessionExpired} />
      {canSeeChurn && <ChurnPanel churn={churn} loading={insightsLoading} />}
    </div>
  );
}
