import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import {
  AlertCircle, Check, Pencil, Plus, RefreshCw, Search, ShieldCheck, Trash2, UserCheck, Users, X,
} from "lucide-react";
import CountUp from "./CountUp";
import { SkeletonRows } from "./Skeleton";
import {
  ApiRequestError, createAdminUser, deleteAdminUser, getAdminUsers, updateAdminUser,
  type AdminUser, type UserRole,
} from "./lib/api";

interface AdminPanelProps { token: string }

const ROLES: UserRole[] = ["admin", "business_owner", "store_manager", "sales_executive"];
const label = (r: string) => r.replaceAll("_", " ");
const initials = (n: string) => n.split(/\s+/).map((p) => p[0]).slice(0, 2).join("").toUpperCase();

type Draft = { id?: number; name: string; email: string; password: string; role: UserRole };
const EMPTY: Draft = { name: "", email: "", password: "", role: "sales_executive" };

export default function AdminPanel({ token }: AdminPanelProps) {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const [query, setQuery] = useState("");
  const [roleEdits, setRoleEdits] = useState<Record<number, UserRole>>({});
  const [draft, setDraft] = useState<Draft | null>(null);
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);
  const [toDelete, setToDelete] = useState<AdminUser | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try { setUsers((await getAdminUsers(token)).users ?? []); }
    catch (e: unknown) { setError(e instanceof ApiRequestError ? e.message : "Unable to load users."); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { void Promise.resolve().then(() => void load()); }, [load]);
  useEffect(() => {
    if (!toast) return;
    const t = window.setTimeout(() => setToast(""), 3000);
    return () => window.clearTimeout(t);
  }, [toast]);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") { setDraft(null); setToDelete(null); } };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const shown = useMemo(() => {
    const q = query.toLowerCase().trim();
    return users.filter((u) => !q || `${u.name} ${u.email} ${u.role}`.toLowerCase().includes(q));
  }, [users, query]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!draft) return;
    setFormError("");
    const editing = draft.id !== undefined;
    if (draft.name.trim().length < 2) return setFormError("Name must be at least 2 characters.");
    if (!/^\S+@\S+\.\S+$/.test(draft.email)) return setFormError("Enter a valid email address.");
    if (!editing && draft.password.length < 4) return setFormError("Password must be at least 4 characters.");
    if (editing && draft.password && draft.password.length < 4) return setFormError("New password must be at least 4 characters.");
    setSaving(true);
    try {
      if (editing) {
        await updateAdminUser(draft.id!, {
          name: draft.name.trim(), email: draft.email.trim(), role: draft.role,
          ...(draft.password ? { password: draft.password } : {}),
        }, token);
        setToast("User updated");
      } else {
        await createAdminUser({ name: draft.name.trim(), email: draft.email.trim(), password: draft.password, role: draft.role }, token);
        setToast("User created");
      }
      setDraft(null);
      await load();
    } catch (err: unknown) {
      setFormError(err instanceof ApiRequestError ? err.message : "Unable to save user.");
    } finally { setSaving(false); }
  }

  async function quickUpdate(u: AdminUser, patch: { role?: UserRole; is_active?: boolean }, msg: string) {
    setBusyId(u.id); setError("");
    try {
      await updateAdminUser(u.id, patch, token);
      setRoleEdits((r) => { const n = { ...r }; delete n[u.id]; return n; });
      setToast(msg); await load();
    } catch (err: unknown) {
      setError(err instanceof ApiRequestError ? err.message : "Update failed.");
    } finally { setBusyId(null); }
  }

  async function confirmDelete() {
    if (!toDelete) return;
    setBusyId(toDelete.id); setError("");
    try { await deleteAdminUser(toDelete.id, token); setToast(`${toDelete.name} deleted`); setToDelete(null); await load(); }
    catch (err: unknown) { setError(err instanceof ApiRequestError ? err.message : "Delete failed."); setToDelete(null); }
    finally { setBusyId(null); }
  }

  const active = users.filter((u) => u.is_active).length;
  const admins = users.filter((u) => u.role === "admin").length;

  return (
    <section className="admin-panel lx-page">
      <div className="section-heading">
        <div>
          <p className="eyebrow">ACCESS CONTROL</p>
          <h2><ShieldCheck size={22} /> Administration</h2>
          <p>Create, edit, re-assign and remove platform accounts.</p>
        </div>
        <div className="inventory-actions">
          <button type="button" className="button button-secondary" onClick={() => void load()} disabled={loading}>
            <RefreshCw size={16} className={loading ? "lx-spin" : ""} /> Refresh
          </button>
          <button type="button" className="button button-primary" onClick={() => { setFormError(""); setDraft({ ...EMPTY }); }}>
            <Plus size={16} /> Add user
          </button>
        </div>
      </div>

      {error && <p className="invoice-error" role="alert"><AlertCircle size={17} /> {error} <button type="button" className="lx-retry" onClick={() => void load()}>Retry</button></p>}

      <div className="lx-stats">
        {[[Users, "Total users", users.length], [UserCheck, "Active", active], [ShieldCheck, "Admins", admins]].map(([Icon, text, n], i) => {
          const I = Icon as typeof Users;
          return <article key={String(text)} className="lx-stat" style={{ animationDelay: `${i * 80}ms` }}><I size={20} /><span>{String(text)}</span><strong><CountUp value={Number(n)} /></strong></article>;
        })}
      </div>

      <div className="lx-toolbar">
        <label className="lx-search"><Search size={16} />
          <input placeholder="Search name, email or role…" value={query} onChange={(e) => setQuery(e.target.value)} />
        </label>
      </div>

      <div className="forecast-table-wrap">
        <table className="forecast-table lx-table">
          <thead><tr><th>User</th><th>Email</th><th>Role</th><th>Status</th><th className="lx-right">Actions</th></tr></thead>
          <tbody>
            {loading && users.length === 0 && <SkeletonRows cols={5} />}
            {shown.map((u, i) => {
              const pending = roleEdits[u.id] ?? u.role;
              const changed = pending !== u.role;
              return (
                <tr key={u.id} className="lx-row" style={{ animationDelay: `${i * 45}ms` }}>
                  <td><span className="lx-user"><span className="lx-avatar">{initials(u.name)}</span><b>{u.name}</b></span></td>
                  <td>{u.email}</td>
                  <td>
                    <select className="lx-select" value={pending} onChange={(e) => setRoleEdits((r) => ({ ...r, [u.id]: e.target.value as UserRole }))}>
                      {ROLES.map((r) => <option key={r} value={r}>{label(r)}</option>)}
                    </select>
                  </td>
                  <td>
                    <button type="button" className={`lx-pill ${u.is_active ? "on" : "off"}`} disabled={busyId === u.id}
                      onClick={() => void quickUpdate(u, { is_active: !u.is_active }, u.is_active ? "Account deactivated" : "Account activated")}>
                      <i /> {u.is_active ? "Active" : "Inactive"}
                    </button>
                  </td>
                  <td>
                    <div className="lx-actions">
                      <button type="button" className="lx-btn" onClick={() => { setFormError(""); setDraft({ id: u.id, name: u.name, email: u.email, password: "", role: u.role }); }}><Pencil size={14} /> Edit</button>
                      <button type="button" className="lx-btn gold" disabled={!changed || busyId === u.id}
                        onClick={() => void quickUpdate(u, { role: pending }, "Role updated")}><Check size={14} /> Update</button>
                      <button type="button" className="lx-btn danger" onClick={() => setToDelete(u)}><Trash2 size={14} /> Delete</button>
                    </div>
                  </td>
                </tr>
              );
            })}
            {!loading && shown.length === 0 && <tr><td colSpan={5}>No users match your search.</td></tr>}
          </tbody>
        </table>
      </div>
      <p className="disclaimer">Passwords are stored as one-way bcrypt hashes and can never be displayed. Editing a user lets you set a new one.</p>

      {draft && (
        <div className="lx-overlay" onClick={() => setDraft(null)}>
          <form className="lx-modal" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
            <div className="lx-modal-head"><h3>{draft.id !== undefined ? "Edit user" : "Add user"}</h3>
              <button type="button" className="lx-x" onClick={() => setDraft(null)} aria-label="Close"><X size={18} /></button></div>
            <label>Full name<input autoFocus value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} /></label>
            <label>Email<input type="email" value={draft.email} onChange={(e) => setDraft({ ...draft, email: e.target.value })} /></label>
            <label>{draft.id !== undefined ? "New password (optional)" : "Password"}
              <input type="password" autoComplete="new-password" value={draft.password} onChange={(e) => setDraft({ ...draft, password: e.target.value })} /></label>
            <label>Role<select value={draft.role} onChange={(e) => setDraft({ ...draft, role: e.target.value as UserRole })}>
              {ROLES.map((r) => <option key={r} value={r}>{label(r)}</option>)}</select></label>
            {formError && <p className="lx-form-error"><AlertCircle size={15} /> {formError}</p>}
            <div className="lx-modal-foot">
              <button type="button" className="button button-secondary" onClick={() => setDraft(null)}>Cancel</button>
              <button type="submit" className="button button-primary" disabled={saving}>{saving ? "Saving…" : "Save"}</button>
            </div>
          </form>
        </div>
      )}

      {toDelete && (
        <div className="lx-overlay" onClick={() => setToDelete(null)}>
          <div className="lx-modal" onClick={(e) => e.stopPropagation()}>
            <div className="lx-modal-head"><h3>Delete user?</h3></div>
            <p>This permanently removes <b>{toDelete.name}</b> ({toDelete.email}). This cannot be undone.</p>
            <div className="lx-modal-foot">
              <button type="button" className="button button-secondary" onClick={() => setToDelete(null)}>Cancel</button>
              <button type="button" className="button lx-danger-solid" onClick={() => void confirmDelete()} disabled={busyId === toDelete.id}>Delete</button>
            </div>
          </div>
        </div>
      )}

      {toast && <div className="lx-toast" role="status"><Check size={16} /> {toast}</div>}
    </section>
  );
}
