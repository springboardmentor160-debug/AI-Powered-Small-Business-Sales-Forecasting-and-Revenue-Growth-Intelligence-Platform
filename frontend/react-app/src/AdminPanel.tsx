import { useCallback, useEffect, useState } from "react";
import { RefreshCw, ShieldCheck, Users } from "lucide-react";
import {
  ApiRequestError,
  getAdminUsers,
  type AdminUsersResponse,
} from "./lib/api";

interface AdminPanelProps {
  token: string;
}

export default function AdminPanel({ token }: AdminPanelProps) {
  const [data, setData] = useState<AdminUsersResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      setData(await getAdminUsers(token));
    } catch (cause: unknown) {
      setError(
        cause instanceof ApiRequestError
          ? cause.message
          : "Unable to load registered users.",
      );
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => {
      if (active) void loadUsers();
    });
    return () => {
      active = false;
    };
  }, [loadUsers]);

  return (
    <section className="admin-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">ACCESS CONTROL</p>
          <h2><ShieldCheck size={22} /> Administration</h2>
          <p>Review registered accounts and their assigned roles.</p>
        </div>

        <button
          type="button"
          className="button button-secondary"
          onClick={() => void loadUsers()}
          disabled={loading}
        >
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      {error && <p className="invoice-error" role="alert">{error}</p>}

      {loading ? (
        <p>Loading registered users...</p>
      ) : data ? (
        <>
          <div className="inventory-metrics">
            <article className="inventory-metric">
              <Users size={20} />
              <span>Total registered users</span>
              <strong>{data.registered_user_profiles.length.toLocaleString()}</strong>
            </article>
          </div>

          <div className="forecast-table-wrap">
            <table className="forecast-table">
               <thead>
                  <tr>
                    <th>User #</th>
                    <th>Email address</th>
                  </tr>
               </thead>
              <tbody>
                {data.registered_user_profiles.map((email, index) => (
                  <tr key={`${email}-${index}`}>
                    <td>{index + 1}</td>
                    <td>{email}</td>
                  </tr>
                ))}
                {data.registered_user_profiles.length === 0 && (
                  <tr>
                    <td colSpan={2}>No registered users found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </section>
  );
}

