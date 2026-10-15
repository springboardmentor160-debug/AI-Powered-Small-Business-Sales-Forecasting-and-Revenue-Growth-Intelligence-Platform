import { AlertsPanel } from "../M3Panels";

export default function AlertsView({ anomalies, loading }) {
  return <AlertsPanel anomalies={anomalies} loading={loading} />;
}
