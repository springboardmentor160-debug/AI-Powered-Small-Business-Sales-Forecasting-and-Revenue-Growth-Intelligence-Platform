import { useEffect, useRef, useState } from "react";
import { apiRequest } from "../lib/api";

/**
 * Loads the churn and anomaly reports once per sign-in (and on refresh),
 * so the Overview, Customers and Alerts tabs all share the same data.
 */
export function useInsights({ token, role, onSessionExpired, reloadKey }) {
  const [churn, setChurn] = useState(null);
  const [anomalies, setAnomalies] = useState(null);
  const [loading, setLoading] = useState(false);
  const expiredRef = useRef(onSessionExpired);

  useEffect(() => {
    expiredRef.current = onSessionExpired;
  }, [onSessionExpired]);

  useEffect(() => {
    if (!token || !role) {
      setChurn(null);
      setAnomalies(null);
      setLoading(false);
      return undefined;
    }

    const canSeeChurn = role === "owner" || role === "admin";
    const canSeeAnomalies = canSeeChurn || role === "store_manager";
    if (!canSeeChurn && !canSeeAnomalies) {
      setLoading(false);
      return undefined;
    }

    let active = true;

    async function load(endpoint, assign) {
      try {
        const data = await apiRequest(endpoint, token);
        if (active) assign(data);
      } catch (error) {
        if (error.status === 401) expiredRef.current?.();
        if (active) assign({ error: error.message });
      }
    }

    setLoading(true);
    Promise.all([
      canSeeChurn ? load("/churn", setChurn) : Promise.resolve(),
      canSeeAnomalies ? load("/anomalies", setAnomalies) : Promise.resolve(),
    ]).finally(() => {
      if (active) setLoading(false);
    });

    return () => {
      active = false;
    };
  }, [token, role, reloadKey]);

  return { churn, anomalies, loading };
}
