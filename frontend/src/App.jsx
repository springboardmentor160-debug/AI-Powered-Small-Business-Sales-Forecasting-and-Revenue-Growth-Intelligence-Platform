import { useEffect, useMemo, useState } from "react";
import { BellRing, LayoutDashboard, RefreshCw, Table2, Users } from "lucide-react";
import AuthScreen from "./components/AuthScreen";
import Topbar from "./components/Topbar";
import Alert from "./components/ui/Alert";
import Button from "./components/ui/Button";
import { Card } from "./components/ui/Card";
import Skeleton from "./components/ui/Skeleton";
import Tabs from "./components/ui/Tabs";
import Tooltip from "./components/ui/Tooltip";
import { useInsights } from "./hooks/useInsights";
import { useTheme } from "./hooks/useTheme";
import { apiRequest } from "./lib/api";
import AlertsView from "./views/AlertsView";
import CustomersView from "./views/CustomersView";
import DataView from "./views/DataView";
import OverviewView from "./views/OverviewView";

const INSIGHT_ROLES = ["owner", "admin", "store_manager"];

const DATA_TAB_LABEL = {
  sales_exec: "My transactions",
  store_manager: "Inventory",
};

function DashboardSkeleton() {
  return (
    <div className="space-y-5" aria-busy="true" aria-label="Loading dashboard">
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }, (_, i) => (
          <Card key={i} className="p-5">
            <div className="flex items-center gap-3">
              <Skeleton className="size-10 rounded-xl" />
              <Skeleton className="h-4 w-28" />
            </div>
            <Skeleton className="mt-5 h-8 w-32" />
            <Skeleton className="mt-3 h-4 w-40" />
          </Card>
        ))}
      </div>
      <div className="grid gap-5 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-2">
          <Skeleton className="h-5 w-44" />
          <Skeleton className="mt-6 h-[260px] w-full rounded-xl" />
        </Card>
        <Skeleton className="min-h-[18rem] rounded-2xl" />
      </div>
    </div>
  );
}

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(null);
  const [salesData, setSalesData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [myTransactions, setMyTransactions] = useState([]);
  const [segments, setSegments] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [loginError, setLoginError] = useState("");
  const [loginNotice, setLoginNotice] = useState("");
  const [loggingIn, setLoggingIn] = useState(false);
  const [dashboardError, setDashboardError] = useState("");
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const { theme, setTheme } = useTheme();

  async function handleLogin(event) {
    event?.preventDefault();
    setLoginError("");
    setLoginNotice("");
    if (!email.trim() || !password) {
      setLoginError("Enter your email and password.");
      return;
    }
    setLoggingIn(true);
    try {
      const data = await apiRequest("/login", null, {
        method: "POST",
        body: JSON.stringify({ email: email.trim(), password }),
      });
      setToken(data.access_token);
      setPassword("");
    } catch (error) {
      setLoginError(error.message || "Sign-in failed. Please try again.");
    } finally {
      setLoggingIn(false);
    }
  }

  function handleLogout() {
    setToken(null);
    setCurrentUser(null);
    setSalesData([]);
    setSummary(null);
    setMyTransactions([]);
    setSegments([]);
    setForecast(null);
    setDashboardError("");
    setLoadingDashboard(false);
    setLastUpdated(null);
    setActiveTab("overview");
  }

  function expireSession() {
    handleLogout();
    setLoginError("");
    setLoginNotice("Your session expired. Please sign in again.");
  }

  useEffect(() => {
    if (!token) return;
    let active = true;

    async function loadDashboard() {
      setLoadingDashboard(true);
      setDashboardError("");
      try {
        const me = await apiRequest("/me", token);
        if (!active) return;
        setCurrentUser(me);

        const results = await Promise.allSettled([
          apiRequest("/sales-transactions", token),
          apiRequest("/sales/summary", token),
          apiRequest("/transactions", token),
          apiRequest("/segments", token),
          apiRequest("/forecast/revenue", token),
        ]);
        if (!active) return;

        const [sales, summaryResult, transactions, segmentResult, forecastResult] = results;
        setSalesData(sales.status === "fulfilled" ? sales.value : []);
        setSummary(summaryResult.status === "fulfilled" ? summaryResult.value : null);
        setMyTransactions(transactions.status === "fulfilled" ? transactions.value : []);
        setSegments(
          segmentResult.status === "fulfilled" && Array.isArray(segmentResult.value)
            ? segmentResult.value
            : [],
        );
        setForecast(forecastResult.status === "fulfilled" ? forecastResult.value : null);

        const rejected = results.filter((result) => result.status === "rejected");
        if (rejected.some((result) => result.reason?.status === 401)) {
          expireSession();
          return;
        }
        const failures = rejected.filter((result) => result.reason?.status !== 403);
        if (failures.length > 0) {
          const reasons = [
            ...new Set(failures.map((f) => f.reason?.message).filter(Boolean)),
          ];
          setDashboardError(`Some dashboard sections couldn't load: ${reasons.join("; ")}`);
        }
      } catch (error) {
        if (active) {
          if (error.status === 401) {
            expireSession();
          } else {
            setDashboardError(
              error.message || "Couldn't load your dashboard. Please sign in again.",
            );
            setCurrentUser(null);
          }
        }
      } finally {
        if (active) {
          setLoadingDashboard(false);
          setLastUpdated(new Date());
        }
      }
    }

    loadDashboard();
    return () => {
      active = false;
    };
    // expireSession only uses state setters, so it is safe to leave out.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, reloadKey]);

  const role = currentUser?.role;
  const { churn, anomalies, loading: loadingInsights } = useInsights({
    token,
    role,
    onSessionExpired: expireSession,
    reloadKey,
  });

  const tabs = useMemo(() => {
    if (!role) return [];
    const list = [
      { id: "overview", label: "Overview", icon: LayoutDashboard },
      { id: "data", label: DATA_TAB_LABEL[role] ?? "Sales", icon: Table2 },
    ];
    if (INSIGHT_ROLES.includes(role)) {
      list.push({ id: "customers", label: "Customers", icon: Users });
      const total = anomalies && !anomalies.error ? Number(anomalies.total_alerts || 0) : null;
      list.push({
        id: "alerts",
        label: "Alerts",
        icon: BellRing,
        count: total,
        countTone: Number(anomalies?.high_severity) > 0 ? "danger" : "neutral",
      });
    }
    return list;
  }, [role, anomalies]);

  const tab = tabs.some((t) => t.id === activeTab) ? activeTab : "overview";

  function renderPanel() {
    switch (tab) {
      case "data":
        return (
          <DataView
            role={role}
            salesData={salesData}
            myTransactions={myTransactions}
            loading={loadingDashboard}
          />
        );
      case "customers":
        return (
          <CustomersView
            role={role}
            token={token}
            churn={churn}
            insightsLoading={loadingInsights}
            onSessionExpired={expireSession}
          />
        );
      case "alerts":
        return <AlertsView anomalies={anomalies} loading={loadingInsights} />;
      default:
        return (
          <OverviewView
            role={role}
            summary={summary}
            salesData={salesData}
            myTransactions={myTransactions}
            segments={segments}
            forecast={forecast}
            churn={churn}
            anomalies={anomalies}
            loading={loadingDashboard}
            insightsLoading={loadingInsights}
            onNavigate={setActiveTab}
          />
        );
    }
  }

  const refreshing = loadingDashboard || loadingInsights;

  return (
    <div className="flex min-h-screen flex-col">
      <Topbar
        user={currentUser}
        signedIn={Boolean(token)}
        loadingUser={loadingDashboard}
        theme={theme}
        onThemeChange={setTheme}
        onSignOut={handleLogout}
      />

      {token ? (
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 pb-12 sm:px-6 lg:px-8">
          {currentUser && (
            <div className="flex flex-wrap items-end justify-between gap-x-4 border-b border-slate-200 dark:border-white/10">
              <Tabs tabs={tabs} value={tab} onChange={setActiveTab} />
              <div className="flex items-center gap-3 pb-2">
                {lastUpdated && !refreshing && (
                  <span className="hidden text-xs text-slate-500 dark:text-slate-400 sm:inline">
                    Updated {lastUpdated.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}
                  </span>
                )}
                <Tooltip content="Reload all data" side="bottom" align="end">
                  <Button
                    variant="secondary"
                    size="sm"
                    loading={refreshing}
                    icon={RefreshCw}
                    onClick={() => setReloadKey((k) => k + 1)}
                  >
                    {refreshing ? "Refreshing" : "Refresh"}
                  </Button>
                </Tooltip>
              </div>
            </div>
          )}

          <div className="mt-6 space-y-5">
            {dashboardError && (
              <Alert
                variant="error"
                title={currentUser ? "Some data is missing" : "Couldn't load your dashboard"}
                action={
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setReloadKey((k) => k + 1)}
                    disabled={loadingDashboard}
                  >
                    Try again
                  </Button>
                }
              >
                {dashboardError}
              </Alert>
            )}

            {currentUser ? (
              <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`}>
                {renderPanel()}
              </div>
            ) : (
              loadingDashboard && <DashboardSkeleton />
            )}
          </div>
        </main>
      ) : (
        <AuthScreen
          email={email}
          password={password}
          onEmailChange={setEmail}
          onPasswordChange={setPassword}
          onSubmit={handleLogin}
          error={loginError}
          notice={loginNotice}
          loading={loggingIn}
        />
      )}
    </div>
  );
}

export default App;
