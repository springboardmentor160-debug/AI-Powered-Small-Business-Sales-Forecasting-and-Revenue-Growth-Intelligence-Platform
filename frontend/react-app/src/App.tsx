import { useEffect, useMemo, useState } from "react";
import InvoicePanel from "./InvoicePanel";
import SegmentationPanel from "./SegmentationPanel";
import RecommendationsPanel from "./RecommendationsPanel";
import ChurnPanel from "./ChurnPanel";
import AnomalyPanel from "./AnomalyPanel";
import InventoryPanel from "./InventoryPanel";
import AdminPanel from "./AdminPanel";
import ExecutiveSummary from "./ExecutiveSummary";
import ForecastPanel from "./ForecastPanel";
import ErrorBoundary from "./ErrorBoundary";
import LiveFx from "./LiveFx";
import LoginScreen from "./LoginScreen";
import NavTabs from "./NavTabs";
import DashboardOverview from "./DashboardOverview";
import {
  Activity, BarChart3, Boxes, FileText, LayoutDashboard, Network, Settings, ShieldAlert, ShieldCheck, ShoppingBag, UserMinus, Users,
} from "lucide-react";
import type { LoginResponse, UserRole } from "./lib/api";
import "./App.css";

type Session = { token: string; role: UserRole; name: string; email: string };

const SESSION_STORAGE_KEY = "marketmindai_session";
const ROLES: UserRole[] = ["business_owner", "store_manager", "sales_executive", "admin"];

const nameFromEmail = (email: string) =>
  (email.split("@")[0] || "User").replace(/[._-]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

function readStoredSession(): Session | null {
  try {
    const stored = sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!stored) return null;
    const p = JSON.parse(stored) as Partial<Session>;
    if (typeof p.token === "string" && p.token && typeof p.role === "string" && ROLES.includes(p.role as UserRole)) {
      const email = typeof p.email === "string" ? p.email : "";
      return { token: p.token, role: p.role as UserRole, email, name: typeof p.name === "string" && p.name ? p.name : nameFromEmail(email) };
    }
    sessionStorage.removeItem(SESSION_STORAGE_KEY);
    return null;
  } catch {
    return null;
  }
}

function App() {
  const [session, setSession] = useState<Session | null>(() => readStoredSession());
  const [message, setMessage] = useState("");
  const [activePage, setActivePage] = useState("dashboard");

  function handleLoggedIn(result: LoginResponse, email: string) {
    const next: Session = {
      token: result.access_token,
      role: result.role,
      email,
      name: result.username?.trim() || nameFromEmail(email),
    };
    sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(next));
    setMessage("");
    setActivePage("dashboard");
    setSession(next);
  }

  function handleLogout() {
    sessionStorage.removeItem(SESSION_STORAGE_KEY);
    setSession(null);
    setMessage("");
  }

  useEffect(() => {
    const expired = () => {
      sessionStorage.removeItem(SESSION_STORAGE_KEY);
      setSession(null);
      setMessage("Your session has expired. Please sign in again.");
    };
    window.addEventListener("mm:unauthorized", expired);
    return () => window.removeEventListener("mm:unauthorized", expired);
  }, []);

  const role = session?.role;
  const navItems = useMemo(
    () =>
      role
        ? [
            { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
            { id: "executive", label: "Executive summary", icon: BarChart3 },
            { id: "segmentation", label: "Customers", icon: Users },
            { id: "recommendations", label: "Recommendations", icon: ShoppingBag },
            ...(role !== "sales_executive"
              ? [
                  { id: "churn", label: "Churn risk", icon: UserMinus },
                  { id: "alerts", label: "Alerts", icon: ShieldAlert },
                ]
              : []),
            { id: "forecasts", label: "Forecasts", icon: Network },
            { id: "invoices", label: "Invoices", icon: FileText },
            { id: "inventory", label: "Inventory", icon: Boxes },
            ...(role === "admin" ? [{ id: "admin", label: "Administration", icon: Settings }] : []),
          ]
        : [],
    [role],
  );
  const pageIds = useMemo(() => navItems.map((n) => n.id), [navItems]);

  if (!session) {
    return <LoginScreen onLoggedIn={handleLoggedIn} initialMessage={message} />;
  }

  const roleLabel = session.role.replaceAll("_", " ");
  const { token } = session;

  return (
    <main className="app-shell">
      <LiveFx items={navItems.map(({ id, label, icon }) => ({ id, label, icon }))} onSelect={setActivePage} />
      <header className="topbar">
        <a className="brand" href="/" aria-label="MarketMindAI home">
          <span className="brand-mark"><Activity size={21} /></span>
          <span><strong>MarketMind</strong><small>AI BUSINESS INTELLIGENCE</small></span>
        </a>
        <div className="topbar-actions">
          <span className="role-chip"><ShieldCheck size={15} />{roleLabel}</span>
          <button className="button button-secondary sign-out" onClick={handleLogout}>Sign out</button>
        </div>
      </header>

      <section className="dashboard">
        <NavTabs items={navItems} active={activePage} onSelect={setActivePage} />

        <ErrorBoundary resetKey={activePage}>
          {activePage === "inventory" ? (
            <InventoryPanel token={token} />
          ) : activePage === "admin" && session.role === "admin" ? (
            <AdminPanel token={token} />
          ) : activePage === "invoices" ? (
            <InvoicePanel token={token} role={session.role} />
          ) : activePage === "executive" ? (
            <ExecutiveSummary token={token} />
          ) : activePage === "segmentation" ? (
            <SegmentationPanel token={token} />
          ) : activePage === "recommendations" ? (
            <RecommendationsPanel token={token} />
          ) : activePage === "churn" && session.role !== "sales_executive" ? (
            <ChurnPanel token={token} />
          ) : activePage === "alerts" && session.role !== "sales_executive" ? (
            <AnomalyPanel token={token} />
          ) : activePage === "forecasts" ? (
            <section className="forecast-page lx-page">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">PREDICTIVE ANALYTICS</p>
                  <h2>Forecasts</h2>
                  <p>Demand forecasting, revenue forecasting, and model comparison.</p>
                </div>
              </div>
              <ForecastPanel token={token} />
            </section>
          ) : (
            <DashboardOverview
              token={token}
              role={session.role}
              name={session.name}
              email={session.email}
              pages={pageIds}
              onNavigate={setActivePage}
              onSignOut={handleLogout}
            />
          )}
        </ErrorBoundary>
      </section>
    </main>
  );
}

export default App;
