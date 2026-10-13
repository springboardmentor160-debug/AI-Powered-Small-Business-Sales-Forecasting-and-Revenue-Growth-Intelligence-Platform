import { useEffect, useState, type FormEvent } from "react";
import InvoicePanel from "./InvoicePanel";
import SegmentationPanel from "./SegmentationPanel";
import InventoryPanel from "./InventoryPanel";
import AdminPanel from "./AdminPanel";
import ExecutiveSummary from "./ExecutiveSummary";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Boxes,
  FileText,
  LayoutDashboard,
  Network,
  Settings,
  Users,
  DollarSign,
  ReceiptText,
  Package,
  RefreshCw
} from "lucide-react";
import {
  ApiRequestError,
  getHealth,
  getSalesSummary,
  login,
  type SalesSummary,
  type UserRole,
} from "./lib/api";
import "./App.css";
import ForecastPanel from "./ForecastPanel";


type Session = {
  token: string;
  role: UserRole;
};

const SESSION_STORAGE_KEY = "marketmindai_session";

function readStoredSession(): Session | null {
  try {
    const stored = sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!stored) return null;

    const parsed: unknown = JSON.parse(stored);
    if (
      typeof parsed === "object" &&
      parsed !== null &&
      "token" in parsed &&
      typeof parsed.token === "string" &&
      parsed.token.length > 0 &&
      "role" in parsed &&
      typeof parsed.role === "string" &&
      [
        "business_owner",
        "store_manager",
        "sales_executive",
        "admin",
      ].includes(parsed.role)
    ) {
      return {
        token: parsed.token,
        role: parsed.role as UserRole,
      };
    }

    sessionStorage.removeItem(SESSION_STORAGE_KEY);
    return null;
  } catch {
    return null;
  }
}

function App() {
  const [salesRefreshKey, setSalesRefreshKey] = useState(0);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
const [session, setSession] = useState<Session | null>(
  () => readStoredSession(),
);  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [backendStatus, setBackendStatus] =
    useState<"checking" | "online" | "offline">("checking");

  const [salesSummary, setSalesSummary] =
    useState<SalesSummary | null>(null);
  const [salesLoading, setSalesLoading] = useState(false);
  const [salesError, setSalesError] = useState("");
  const [activePage, setActivePage] = useState("dashboard");

  useEffect(() => {
    if (!session) return;

    let cancelled = false;

    async function loadSales() {
      setSalesLoading(true);
      setSalesError("");

      try {
const result = await getSalesSummary(session!.token);
        if (!cancelled) {
          setSalesSummary(result);
        }
      } catch (error: unknown) {
        if (!cancelled) {
          setSalesSummary(null);
          setSalesError(
            error instanceof ApiRequestError
              ? error.message
              : "Unable to load the sales summary.",
          );
        }
      } finally {
        if (!cancelled) {
          setSalesLoading(false);
        }
      }
    }

    void Promise.resolve().then(() => {
      if (!cancelled) void loadSales();
    });

    return () => {
      cancelled = true;
    };
}, [session, salesRefreshKey]);
  async function checkBackend() {
    try {
      await getHealth();
      setBackendStatus("online");
    } catch {
      setBackendStatus("offline");
    }
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      const result = await login({
        email: email.trim(),
        password,
      });

      const newSession: Session = {
         token: result.access_token,
         role: result.role,
      };

        sessionStorage.setItem(
        SESSION_STORAGE_KEY,
        JSON.stringify(newSession),
      );
      setSession(newSession);
      setPassword("");
      setBackendStatus("online");
    } catch (error: unknown) {
      setMessage(
        error instanceof ApiRequestError
          ? error.status === 401
            ? "Invalid email or password. Please try again."
            : error.message
          : "Login failed. Please try again.",
      );

      void checkBackend();
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    sessionStorage.removeItem(SESSION_STORAGE_KEY);
    setSalesSummary(null);
    setSalesError("");
    setSalesLoading(false);
    setSession(null);
    setPassword("");
    setMessage("");
    setSalesError("");
  }

  const roleLabel = session?.role.replaceAll("_", " ");

  if (session) {
    return (
      <main className="app-shell">
        <header className="topbar">
          <a className="brand" href="/" aria-label="MarketMindAI home">
            <span className="brand-mark">
              <Activity size={21} />
            </span>
            <span>
              <strong>MarketMind</strong>
              <small>AI BUSINESS INTELLIGENCE</small>
            </span>
          </a>

          <div className="topbar-actions">
            <span className="role-chip">
              <ShieldCheck size={15} />
              {roleLabel}
            </span>
            <button
              className="button button-secondary sign-out"
              onClick={handleLogout}
            >
              Sign out
            </button>
          </div>
        </header>

        <section className="dashboard">
          <nav className="page-navigation" aria-label="Main navigation">
            {[
              { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
              { id: "executive", label: "Executive summary", icon: BarChart3 },
              { id: "segmentation", label: "Customers", icon: Users },
              { id: "forecasts", label: "Forecasts", icon: Network },
              { id: "invoices", label: "Invoices", icon: FileText },
              { id: "inventory", label: "Inventory", icon: Boxes },
              ...(session.role === "admin"
                ? [{ id: "admin", label: "Administration", icon: Settings }]
                : []),
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                type="button"
                className={`nav-item ${activePage === id ? "active" : ""}`}
                onClick={() => setActivePage(id)}
                aria-current={activePage === id ? "page" : undefined}
              >
                <Icon size={17} />
                <span>{label}</span>
              </button>
            ))}
          </nav>

                    {activePage === "inventory" ? (
            <InventoryPanel token={session.token} />
          ) : activePage === "admin" && session.role === "admin" ? (
            <AdminPanel token={session.token} />
          ) : activePage === "invoices" ? (
            <InvoicePanel token={session.token} role={session.role} />
          ) : activePage === "executive" ? (
            <ExecutiveSummary token={session.token} />
          ) : activePage === "segmentation" ? (
            <SegmentationPanel token={session.token} />
          ) : activePage === "forecasts" ? (
            <section className="forecast-page">
                <div className="section-heading">
                    <div>
                        <p className="eyebrow">PREDICTIVE ANALYTICS</p>
                        <h2>Forecasts</h2>
                        <p>Demand forecasting, revenue forecasting, and model comparison.</p>
                    </div>
                </div>
                <ForecastPanel token={session.token} />
             </section>
            ) : activePage === "dashboard" ? (
                    <>
              <div className="welcome-row">
                <div>
                  <p className="eyebrow">YOUR BUSINESS OVERVIEW</p>
                  <h1>Your business, in focus.</h1>
                  <p className="welcome-copy">
                    One clear view of your sales, forecasts, and inventory signals.
                  </p>
                </div>
                <div className={`connection-pill ${backendStatus}`}>
                  <span className="connection-dot" />
                  API {backendStatus}
                </div>
              </div>

              <div className="status-banner">
                <span className="status-icon">
                  <LockKeyhole size={17} />
                </span>
                <div>
                  <strong>Secure session established</strong>
                  <p>
                    You are signed in with the <b>{roleLabel}</b> role. Available
                    information is controlled by backend permissions.
                  </p>
                </div>
              </div>

              <div className="section-heading">
                <div>
                  <p className="eyebrow">MARKETMIND INTELLIGENCE</p>
                  <h2>Analytics overview</h2>
                </div>
                <span className="preview-label">Connected dashboard</span>
              </div>

              <div className="feature-grid">
              <article className="feature-card">
                <span className="feature-icon violet">
                  <TrendingUp size={22} />
                </span>
                <h3>Sales intelligence</h3>

                {salesLoading ? (
                  <p>Loading live sales summary...</p>
                ) : salesError ? (
                  <p className="sales-error" role="alert">{salesError}</p>
                ) : salesSummary ? (
                  <div className="sales-metrics">
                    <div className="sales-metric">
                      <span className="sales-metric-label">
                        <DollarSign size={15} /> Total revenue
                      </span>
                      <strong>
                        {Number(salesSummary.total_revenue).toLocaleString(
                          undefined,
                          { maximumFractionDigits: 2 },
                        )}
                      </strong>
                    </div>
                    <div className="sales-metric">
                      <span className="sales-metric-label">
                        <ReceiptText size={15} /> Total orders
                      </span>
                      <strong>
                        {Number(salesSummary.total_orders).toLocaleString()}
                      </strong>
                    </div>
                    <div className="sales-metric">
                      <span className="sales-metric-label">
                        <Package size={15} /> Top product
                      </span>
                      <strong className="top-product">
                        {salesSummary.top_product || "Not available"}
                      </strong>
                    </div>
                  </div>
                ) : (
                  <p>Sign in to load the sales summary from the API.</p>
                )}

                <button
                  type="button"
                  className="feature-link inventory-link-button"
                  onClick={() => setSalesRefreshKey((key) => key + 1)}
                  disabled={salesLoading}
                >
                  <RefreshCw size={15} />
                  {salesLoading ? "Refreshing..." : "Refresh live sales summary"}
                  <ArrowRight size={15} />
                </button>
              </article>

              <ForecastPanel token={session.token} />

              <article className="feature-card">
                <span className="feature-icon amber">
                  <Boxes size={22} />
                </span>
                <h3>Inventory insights</h3>
                <p>
                  Inventory estimates are distinguished from verified physical
                  stock. Open Inventory for live estimates.
                </p>
                <button
                  type="button"
                  className="feature-link inventory-link-button"
                  onClick={() => setActivePage("inventory")}
                >
                  Inventory overview <ArrowRight size={15} />
                </button>
              </article>
            </div>

            <p className="disclaimer">
              Sales metrics are fetched from the authenticated backend API.
              Inventory values are estimates and must not be interpreted as a
              verified physical stock count.
            </p>
            </>
          ) : (
            <div className="feature-card">
              <h2>Coming next</h2>
              <p>
                This screen is not connected yet. The existing dashboard and
                inventory screen remain available.
              </p>
            </div>
          )}
        </section>
    </main>
    );
  }

  return (
    <main className="login-layout">
      <section className="login-showcase">
        <div className="showcase-top">
          <a className="brand brand-light" href="/" aria-label="MarketMindAI home">
            <span className="brand-mark">
              <Activity size={21} />
            </span>
            <span>
              <strong>MarketMind</strong>
              <small>AI BUSINESS INTELLIGENCE</small>
            </span>
          </a>

          <span className="showcase-badge">
            <Sparkles size={14} /> Built for smarter decisions
          </span>
        </div>

        <div className="showcase-content">
          <p className="eyebrow eyebrow-light">
            SEE THE SIGNAL. ACT WITH CONFIDENCE.
          </p>
          <h1>
            Turn retail data
            <br />
            into <span>clear direction.</span>
          </h1>
          <p className="showcase-copy">
            Bring sales performance, demand forecasting, and inventory signals
            into one focused business intelligence workspace.
          </p>

          <div className="showcase-points">
            <div>
              <span className="point-icon">
                <TrendingUp size={18} />
              </span>
              <span>
                <strong>Sales intelligence</strong>
                <small>Understand performance and product trends.</small>
              </span>
            </div>

            <div>
              <span className="point-icon">
                <BarChart3 size={18} />
              </span>
              <span>
                <strong>Forecast-led planning</strong>
                <small>Bring model outputs into business decisions.</small>
              </span>
            </div>

            <div>
              <span className="point-icon">
                <ShieldCheck size={18} />
              </span>
              <span>
                <strong>Role-aware access</strong>
                <small>Protect business data through API permissions.</small>
              </span>
            </div>
          </div>
        </div>

        <div className="showcase-footer">
          <span>MARKETMIND AI</span>
          <span>Retail intelligence workspace</span>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-form-wrap">
          <div className="mobile-brand">
            <span className="brand-mark">
              <Activity size={21} />
            </span>
            <span>
              <strong>MarketMind</strong>
              <small>AI BUSINESS INTELLIGENCE</small>
            </span>
          </div>

          <div className="login-heading">
            <span className="login-icon">
              <LockKeyhole size={22} />
            </span>
            <p className="eyebrow">WELCOME BACK</p>
            <h2>Sign in to your workspace</h2>
            <p>Use your MarketMindAI account to continue.</p>
          </div>

          <form className="login-form" onSubmit={handleLogin}>
            <label htmlFor="email">Email address</label>
            <div className="input-wrap">
              <Mail size={18} />
              <input
                id="email"
                type="email"
                autoComplete="username"
                placeholder="you@company.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <label htmlFor="password">Password</label>
            <div className="input-wrap">
              <LockKeyhole size={18} />
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
              <button
                className="password-toggle"
                type="button"
                onClick={() => setShowPassword((visible) => !visible)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            {message && (
              <p className="form-message" role="alert">
                {message}
              </p>
            )}

            <button
              className="button button-primary submit-button"
              type="submit"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign in securely"}
              {!loading && <ArrowRight size={17} />}
            </button>
          </form>

          <div className="login-security">
            <ShieldCheck size={17} />
            <span>Access is verified by the MarketMindAI backend.</span>
          </div>

          <div className="backend-note">
            <span className={`connection-dot ${backendStatus}`} />
            Backend status: {backendStatus}
          </div>
        </div>

        <footer className="login-footer">
          <span>© {new Date().getFullYear()} MarketMindAI</span>
          <span>Secure business intelligence</span>
        </footer>
      </section>
    </main>
  );
}

export default App;