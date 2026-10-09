import { useCallback, useEffect, useState } from "react";

import "./App.css";

// COMPONENTS

import Sidebar from "./components/Sidebar";

import Header from "./components/Header";

// PAGES

import DashboardOverviewPage from "./pages/DashboardOverviewPage";

import SalesPage from "./pages/SalesPage";

import InventoryPage from "./pages/InventoryPage";

import CustomersPage from "./pages/CustomersPage";

import InvoicesPage from "./pages/InvoicesPage";

import ForecastingPage from "./pages/ForecastingPage";

import SegmentationPage from "./pages/SegmentationPage";

import ChurnPage from "./pages/ChurnPage";

import RecommendationsPage from "./pages/RecommendationsPage";

import AnomalyPage from "./pages/AnomalyPage";

import ReportsPage from "./pages/ReportsPage";

import SettingsPage from "./pages/SettingsPage";

import DataUploadPage from "./pages/DataUploadPage";

import LandingPage from "./pages/LandingPage";

const journeyPaths = {
  landing: "/",
  login: "/login",
  register: "/register",
};

function getInitialJourneyStep() {
  const path = window.location.pathname;
  if (path === journeyPaths.register) return "register";
  if (path === journeyPaths.login) return "login";
  if (localStorage.getItem("token")) return "dashboard";
  return "landing";
}

function App() {
  // ---------------------------------------------------

  // ROUTING / ACTIVE PAGE STATE

  // ---------------------------------------------------

  const [activePage, setActivePage] = useState("dashboard");

  const [journeyStep, setJourneyStep] = useState(getInitialJourneyStep);

  // ---------------------------------------------------

  // AUTHENTICATION STATES

  // ---------------------------------------------------

  const [isLoggedIn, setIsLoggedIn] = useState(

    !!localStorage.getItem("token")

  );

  const [isLogin, setIsLogin] = useState(
    window.location.pathname !== journeyPaths.register
  );
  const [username, setUsername] = useState("");

  const [password, setPassword] = useState("");

  const [role, setRole] = useState("Business Owner");

  const [message, setMessage] = useState("");

  // ---------------------------------------------------

  // CURRENT USER STATES

  // ---------------------------------------------------

  const [userRole, setUserRole] = useState(

    localStorage.getItem("role") || ""

  );

  const [currentUsername, setCurrentUsername] = useState(

    localStorage.getItem("username") || ""

  );

  const [activeDatasetId, setActiveDatasetId] = useState(null);
  const [activeDatasetFilename, setActiveDatasetFilename] = useState("");

  // ---------------------------------------------------

  // MILESTONE 1 DASHBOARD STATES

  // ---------------------------------------------------

  const [revenue, setRevenue] = useState(0);

  const [margin, setMargin] = useState(0);

  const [lowStock, setLowStock] = useState(0);

  const [citySales, setCitySales] = useState({});

  const [categorySales, setCategorySales] = useState({});

  // ---------------------------------------------------

  // MILESTONE 2 FILTER & ANALYTICS STATES

  // ---------------------------------------------------

  const [filters, setFilters] = useState({

    city: "All",

    category: "All",

    storeFormat: "All",

    channel: "All",

    paymentMode: "All",

  });

  const [filterOptions, setFilterOptions] = useState({

    cities: [],

    categories: [],

    store_formats: [],

    channels: [],

    payment_modes: [],

  });

  const [salesTrends, setSalesTrends] = useState([]);

  const [trendGranularity, setTrendGranularity] = useState("monthly");

  const [brandChannelData, setBrandChannelData] = useState({

    by_brand: [],

    by_channel: [],

  });

  const [inventoryIntel, setInventoryIntel] = useState({

    total_low_stock_count: 0,

    by_category: {},

    critical_items: [],

  });

  const [demographicIntel, setDemographicIntel] = useState({

    by_age_group: [],

    by_gender: [],

    by_loyalty: [],

  });

  const [segmentationMethod, setSegmentationMethod] = useState("kmeans");

  const [segmentationData, setSegmentationData] = useState({

    kmeans_profiles: [],

    hierarchical_profiles: [],

    limitation_note: "",

  });

  const [churnData, setChurnData] = useState(null);

  const [anomalyData, setAnomalyData] = useState(null);

  const [dashboardDataStatus, setDashboardDataStatus] = useState({});

  const [forecastHorizon, setForecastHorizon] = useState(30);

  const [forecastModel, setForecastModel] = useState("prophet");

  const [isDownloadingReport, setIsDownloadingReport] = useState(false);

  const [forecastData, setForecastData] = useState({

    model_used: "",

    forecast_horizon_days: 30,

    historical_data: [],

    forecast_data: [],

    summary_metrics: {

      historical_avg_daily_revenue: 0,

      projected_period_total_revenue: 0,

      projected_growth_pct: 0,

    },

  });

  const updateDashboardStatus = useCallback((key, status, requestKey) => {

    setDashboardDataStatus((current) => ({

      ...current,

      [key]: { status, requestKey },

    }));

  }, []);

  const dashboardRequestKey = JSON.stringify({

    filters,

    trendGranularity,

    forecastHorizon,

    forecastModel,

    role: userRole,

  });

  // ---------------------------------------------------

  // MILESTONE 3: RECOMMENDATION ENGINE STATES

  // ---------------------------------------------------

  const [recBrand, setRecBrand] = useState("Amul");

  const [recCategory, setRecCategory] = useState("Dairy");

  const [recTopN, setRecTopN] = useState(5);

  const [recTab, setRecTab] = useState("collaborative");

  const [recLoading, setRecLoading] = useState(false);

  const [recError, setRecError] = useState("");

  const [recData, setRecData] = useState(null);

  const navigateJourney = (step) => {
    const nextPath = journeyPaths[step] || journeyPaths.landing;
    if (window.location.pathname !== nextPath) {
      window.history.pushState({ journeyStep: step }, "", nextPath);
    }
    setJourneyStep(step);
    if (step === "login") setIsLogin(true);
    if (step === "register") setIsLogin(false);
  };

  useEffect(() => {
    const onPopState = () => {
      const path = window.location.pathname;
      if (path === journeyPaths.login || path === journeyPaths.register) {
        setIsLogin(path !== journeyPaths.register);
        setJourneyStep(path === journeyPaths.register ? "register" : "login");
      } else {
        setJourneyStep(isLoggedIn ? "dashboard" : "landing");
      }
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, [isLoggedIn]);

  // ---------------------------------------------------
  // GET CURRENT USER PROFILE
  // ---------------------------------------------------

  const loadProfile = async (token) => {

    try {

      const response = await fetch("/api/profile", {

        headers: {

          Authorization: `Bearer ${token}`,

        },

      });

      const data = await response.json();

      if (response.ok) {

        setUserRole(data.role);

        setCurrentUsername(data.username);

        localStorage.setItem("role", data.role);

        localStorage.setItem("username", data.username);

        return data.role;

      }

      return "";

    } catch (error) {

      console.error(error);

      return "";

    }

  };

  // ---------------------------------------------------

  // HELPER: BUILD FILTER QUERY STRING

  // ---------------------------------------------------

  const buildQueryString = (params) => {

    const query = new URLSearchParams();

    if (params.city && params.city !== "All") query.append("city", params.city);

    if (params.category && params.category !== "All")

      query.append("category", params.category);

    if (params.storeFormat && params.storeFormat !== "All")

      query.append("store_format", params.storeFormat);

    if (params.channel && params.channel !== "All")

      query.append("channel", params.channel);

    if (params.paymentMode && params.paymentMode !== "All")

      query.append("payment_mode", params.paymentMode);

    const str = query.toString();

    return str ? `?${str}` : "";

  };

  // ---------------------------------------------------

  // LOAD DASHBOARD DATA & FILTERS

  // ---------------------------------------------------

  useEffect(() => {

    let isCurrentRequest = true;

    if (!isLoggedIn) {
      return;

    }

    const token = localStorage.getItem("token");

    if (!token) {

      return;

    }

    const headers = {

      Authorization: `Bearer ${token}`,

    };

    const loadDashboard = async () => {

      let activeRole = userRole;

      if (!activeRole) {

        activeRole = await loadProfile(token);

      }

      const queryString = buildQueryString(filters);

      const canViewFinancials =

        activeRole === "Business Owner" || activeRole === "Administrator";

      const canViewStock =

        canViewFinancials || activeRole === "Store Manager";

      const canViewForecastActive =

        canViewStock;

      const requestKey = JSON.stringify({

        filters,

        trendGranularity,

        forecastHorizon,

        forecastModel,

        role: activeRole,

      });

      const fetchDashboardData = (url, statusKey, consume) => {

        fetch(url, { headers })

          .then(async (response) => {

            const data = await response.json();

            if (!response.ok || data?.detail) {

              const error = new Error(

                data?.detail || `Request failed with status ${response.status}`

              );

              error.isRestricted =

                response.status === 403 ||

                /access denied|permission|restricted|forbidden|not authorized|not permitted/i.test(

                  String(data?.detail || "")

                );

              throw error;

            }

            return data;

          })

          .then((data) => {

            if (isCurrentRequest) consume(data);

          })

          .catch((error) => {

            if (!isCurrentRequest) return;

            console.error(`Dashboard ${statusKey} request error:`, error);

            updateDashboardStatus(

              statusKey,

              error.isRestricted ? "restricted" : "error",

              requestKey

            );

          });

      };

      // 1. Fetch Filter Options

      fetch("/api/filter-options", { headers })

        .then((res) => res.json())

        .then((data) => {

          if (!data.detail) {

            setFilterOptions(data);

          }

        })

        .catch((err) => console.error(err));

      // 2. Revenue and Margin (Business Owner & Admin)

      if (canViewFinancials) {

        fetchDashboardData(`/api/total-revenue${queryString}`, "revenue", (data) => {

          if (!Number.isFinite(data.total_revenue)) {

            throw new Error("Revenue response did not include total_revenue");

          }

          setRevenue(data.total_revenue);

          updateDashboardStatus("revenue", "ready", requestKey);

        });

        fetchDashboardData(`/api/total-margin${queryString}`, "margin", (data) => {

          if (!Number.isFinite(data.total_margin)) {

            throw new Error("Margin response did not include total_margin");

          }

          setMargin(data.total_margin);

          updateDashboardStatus("margin", "ready", requestKey);

        });

      }

      // 3. Low Stock (Business Owner, Store Manager, Admin)

      if (canViewStock) {

        fetchDashboardData(`/api/low-stock${queryString}`, "stock", (data) => {

          if (!Number.isFinite(data.low_stock_records)) {

            throw new Error("Low-stock response did not include low_stock_records");

          }

          setLowStock(data.low_stock_records);

          updateDashboardStatus("stock", "ready", requestKey);

        });

        // Inventory Intelligence endpoint

        fetch(`/api/inventory-intelligence${queryString}`, {

          headers,

        })

          .then((res) => res.json())

          .then((data) => {

            if (!data.detail) {

              setInventoryIntel(data);

            }

          })

          .catch((err) => console.error(err));

      }

      // 4. Sales by City & Category (All 4 roles)

      fetch(`/api/sales-by-city${queryString}`, { headers })

        .then((res) => res.json())

        .then((data) => {

          if (!data.detail) {

            setCitySales(data);

          }

        })

        .catch((err) => console.error(err));

      fetch(`/api/sales-by-category${queryString}`, {

        headers,

      })

        .then((res) => res.json())

        .then((data) => {

          if (!data.detail) {

            setCategorySales(data);

          }

        })

        .catch((err) => console.error(err));

      // 5. Sales Trends (All 4 roles)

      const trendQuery = queryString

        ? `${queryString}&granularity=${trendGranularity}`

        : `?granularity=${trendGranularity}`;

      fetch(`/api/sales-trends${trendQuery}`, { headers })

        .then((res) => {

          if (!res.ok) {

            const error = new Error(`Sales trends request failed (${res.status})`);

            error.status = res.status;

            throw error;

          }

          return res.json();

        })

        .then((data) => {

          if (!isCurrentRequest) return;

          if (Array.isArray(data)) {

            setSalesTrends(data);

            updateDashboardStatus(

              "trends",

              data.length ? "ready" : "empty",

              requestKey

            );

          } else if (data?.detail) {

            const isRestricted =

              /access denied|permission|restricted|forbidden|not authorized|not permitted/i.test(

                String(data.detail)

              );

            updateDashboardStatus(

              "trends",

              isRestricted ? "restricted" : "error",

              requestKey

            );

          } else {

            updateDashboardStatus("trends", "error", requestKey);

          }

        })

        .catch((err) => {

          if (!isCurrentRequest) return;

          console.error("Dashboard trends request error:", err);

          updateDashboardStatus(

            "trends",

            err.status === 403 ? "restricted" : "error",

            requestKey

          );

        });

      // 6. Brand & Channel Analytics (All 4 roles)

      fetch(`/api/brand-channel-analytics${queryString}`, {

        headers,

      })

        .then((res) => res.json())

        .then((data) => {

          if (!data.detail) {

            setBrandChannelData(data);

          }

        })

        .catch((err) => console.error(err));

      // 7. Demographic Analytics (All 4 roles)

      fetch(`/api/demographic-analytics${queryString}`, {

        headers,

      })

        .then((res) => res.json())

        .then((data) => {

          if (!data.detail) {

            setDemographicIntel(data);

          }

        })

        .catch((err) => console.error(err));

      // 8. Customer Segmentation & Clustering (All 4 roles)

      fetchDashboardData(

        `/api/customer-segmentation${queryString}`,

        "segmentation",

        (data) => {

          if (

            !Array.isArray(data.kmeans_profiles) ||

            !Array.isArray(data.hierarchical_profiles)

          ) {

            throw new Error("Customer segmentation response did not include profiles");

          }

          setSegmentationData(data);

          const hasSegments =

            data.kmeans_profiles.length > 0 ||

            data.hierarchical_profiles.length > 0;

          updateDashboardStatus(

            "segmentation",

            hasSegments ? "ready" : "empty",

            requestKey

          );

        }

      );

      // 9. Sales Forecasting

      if (canViewForecastActive) {

        const forecastQuery = queryString

          ? `${queryString}&horizon=${forecastHorizon}&model_type=${forecastModel}`

          : `?horizon=${forecastHorizon}&model_type=${forecastModel}`;

        fetchDashboardData(

          `/api/sales-forecast${forecastQuery}`,

          "forecast",

          (data) => {

            if (

              !Array.isArray(data.historical_data) ||

              !Array.isArray(data.forecast_data)

            ) {

              throw new Error("Sales forecast response did not include series data");

            }

            setForecastData(data);

            updateDashboardStatus(

              "forecast",

              data.historical_data.length || data.forecast_data.length

                ? "ready"

                : "empty",

              requestKey

            );

          }

        );

      }

      // 10. Churn Prediction & Risk Intelligence

      fetchDashboardData(`/api/churn-prediction${queryString}`, "churn", (data) => {

        setChurnData(data);

        const hasChurnData =

          (data.sample_high_risk_invoices || []).length > 0 ||

          (data.churn_risk_by_segment_cohort || []).length > 0 ||

          Object.keys(data.risk_distribution || {}).length > 0;

        updateDashboardStatus(

          "churn",

          hasChurnData ? "ready" : "empty",

          requestKey

        );

      });

      // 11. Anomaly Detection & Fraud Intelligence

      fetchDashboardData(`/api/anomalies${queryString}`, "anomalies", (data) => {

        if (data.total_anomalies_detected === undefined) {

          throw new Error("Anomaly response did not include total_anomalies_detected");

        }

        setAnomalyData(data);

        updateDashboardStatus("anomalies", "ready", requestKey);

      });

    };

    loadDashboard();

    return () => {

      isCurrentRequest = false;

    };

  }, [

    isLoggedIn,

    filters,

    trendGranularity,

    forecastHorizon,

    forecastModel,

    updateDashboardStatus,

  ]);

  // ---------------------------------------------------

  // FETCH AI PRODUCT RECOMMENDATIONS

  // ---------------------------------------------------

  const fetchRecommendations = async (

    brand = recBrand,

    category = recCategory,

    topN = recTopN

  ) => {

    setRecLoading(true);

    setRecError("");

    const token = localStorage.getItem("token");

    try {

      const response = await fetch(

        `/api/recommendations?brand=${encodeURIComponent(

          brand

        )}&category=${encodeURIComponent(category)}&top_n=${topN}`,

        {

          headers: {

            Authorization: `Bearer ${token}`,

          },

        }

      );

      const data = await response.json();

      if (response.ok) {

        setRecData(data);

      } else {

        setRecError(data.detail || "Failed to fetch recommendations");

      }

    } catch (err) {

      console.error(err);

      setRecError("Error connecting to recommendation service");

    } finally {

      setRecLoading(false);

    }

  };

  useEffect(() => {

    if (isLoggedIn) {
      fetchRecommendations(recBrand, recCategory, recTopN);

    }

  }, [isLoggedIn, recBrand, recCategory, recTopN]);

  // ---------------------------------------------------

  // SVG TREND CHART HELPER

  // ---------------------------------------------------

  const canViewMargin =

    userRole === "Business Owner" || userRole === "Administrator";

  const renderTrendChart = () => {

    if (!salesTrends || salesTrends.length === 0) {

      return (

        <p style={{ color: "#94a3b8", padding: "20px", textAlign: "center" }}>

          No trend data available for current filters.

        </p>

      );

    }

    const width = 800;

    const height = 240;

    const padding = 40;

    const maxVal = Math.max(

      ...salesTrends.map((d) => Math.max(d.revenue || 0, d.margin || 0))

    );

    const stepX = (width - padding * 2) / Math.max(salesTrends.length - 1, 1);

    const revPoints = salesTrends

      .map((d, i) => {

        const x = padding + i * stepX;

        const y = height - padding - (d.revenue / (maxVal || 1)) * (height - padding * 2);

        return `${x},${y}`;

      })

      .join(" ");

    const marginPoints = canViewMargin

      ? salesTrends

          .map((d, i) => {

            const x = padding + i * stepX;

            const y = height - padding - ((d.margin || 0) / (maxVal || 1)) * (height - padding * 2);

            return `${x},${y}`;

          })

          .join(" ")

      : "";

    return (

      <div className="chart-wrapper">

        <svg className="svg-chart" viewBox={`0 0 ${width} ${height}`}>

          {[0, 0.25, 0.5, 0.75, 1].map((pct, idx) => {

            const y = height - padding - pct * (height - padding * 2);

            return (

              <g key={idx}>

                <line

                  x1={padding}

                  y1={y}

                  x2={width - padding}

                  y2={y}

                  stroke="#334155"

                  strokeDasharray="4"

                />

                <text

                  x={padding - 8}

                  y={y + 4}

                  fill="#94a3b8"

                  fontSize="10"

                  textAnchor="end"

                >

                  ₹{Math.round((maxVal * pct) / 1000)}k

                </text>

              </g>

            );

          })}

          <polyline

            fill="none"

            stroke="#61dafb"

            strokeWidth="3"

            points={revPoints}

          />

          {canViewMargin && (

            <polyline

              fill="none"

              stroke="#38ef7d"

              strokeWidth="3"

              points={marginPoints}

            />

          )}

          {salesTrends.map((d, i) => {

            const x = padding + i * stepX;

            const yRev = height - padding - (d.revenue / (maxVal || 1)) * (height - padding * 2);

            const yMar = canViewMargin

              ? height - padding - ((d.margin || 0) / (maxVal || 1)) * (height - padding * 2)

              : 0;

            return (

              <g key={i}>

                <circle cx={x} cy={yRev} r="4" fill="#61dafb" />

                {canViewMargin && <circle cx={x} cy={yMar} r="4" fill="#38ef7d" />}

                <text

                  x={x}

                  y={height - 12}

                  fill="#94a3b8"

                  fontSize="10"

                  textAnchor="middle"

                >

                  {d.period}

                </text>

              </g>

            );

          })}

        </svg>

        <div className="chart-legend">

          <div className="legend-item">

            <div className="legend-color" style={{ backgroundColor: "#61dafb" }} />

            <span>Revenue</span>

          </div>

          {canViewMargin && (

            <div className="legend-item">

              <div className="legend-color" style={{ backgroundColor: "#38ef7d" }} />

              <span>Total Margin</span>

            </div>

          )}

        </div>

      </div>

    );

  };

  // ---------------------------------------------------

  // SVG FORECAST CHART HELPER

  // ---------------------------------------------------

  const renderForecastChart = () => {

    const historical = forecastData.historical_data || [];

    const forecast = forecastData.forecast_data || [];

    if (historical.length === 0 && forecast.length === 0) {

      return (

        <div style={{ padding: "40px", textAlign: "center", color: "#94a3b8" }}>

          No forecast data available for selected filters.

        </div>

      );

    }

    const recentHistorical = historical.slice(-60);

    const combinedPoints = [

      ...recentHistorical.map((h) => ({ date: h.ds, val: h.y, type: "hist" })),

      ...forecast.map((f) => ({

        date: f.ds,

        val: f.yhat,

        lower: f.yhat_lower,

        upper: f.yhat_upper,

        type: "fcst",

      })),

    ];

    if (combinedPoints.length === 0) return null;

    const width = 850;

    const height = 280;

    const paddingLeft = 65;

    const paddingRight = 30;

    const paddingTop = 20;

    const paddingBottom = 40;

    const chartWidth = width - paddingLeft - paddingRight;

    const chartHeight = height - paddingTop - paddingBottom;

    const allYValues = [

      ...recentHistorical.map((h) => h.y),

      ...forecast.map((f) => f.yhat),

      ...forecast.map((f) => f.yhat_lower),

      ...forecast.map((f) => f.yhat_upper),

    ];

    const minY = Math.max(0, Math.min(...allYValues) * 0.9);

    const maxY = Math.max(...allYValues) * 1.1 || 100;

    const getX = (idx) => {

      if (combinedPoints.length <= 1) return paddingLeft;

      return paddingLeft + (idx / (combinedPoints.length - 1)) * chartWidth;

    };

    const getY = (val) => {

      if (maxY === minY) return paddingTop + chartHeight / 2;

      return (

        height - paddingBottom - ((val - minY) / (maxY - minY)) * chartHeight

      );

    };

    const histPoints = recentHistorical.map((h, idx) => ({

      x: getX(idx),

      y: getY(h.y),

    }));

    const histPathD = histPoints.reduce(

      (acc, p, idx) => `${acc} ${idx === 0 ? "M" : "L"} ${p.x} ${p.y}`,

      ""

    );

    const lastHistIdx = recentHistorical.length - 1;

    const lastHistX = getX(lastHistIdx);

    const lastHistY = histPoints[lastHistIdx] ? histPoints[lastHistIdx].y : getY(0);

    const fcstPoints = forecast.map((f, idx) => {

      const overallIdx = recentHistorical.length + idx;

      return {

        x: getX(overallIdx),

        y: getY(f.yhat),

        lowerY: getY(f.yhat_lower),

        upperY: getY(f.yhat_upper),

      };

    });

    const fcstPathD = fcstPoints.reduce(

      (acc, p, idx) =>

        `${acc} ${idx === 0 ? `M ${lastHistX} ${lastHistY} L` : "L"} ${p.x} ${

          p.y

        }`,

      ""

    );

    let areaPathD = "";

    if (fcstPoints.length > 0) {

      const upperPath = fcstPoints.map((p) => `${p.x},${p.upperY}`).join(" L ");

      const lowerPath = [...fcstPoints]

        .reverse()

        .map((p) => `${p.x},${p.lowerY}`)

        .join(" L ");

      areaPathD = `M ${lastHistX},${lastHistY} L ${upperPath} L ${lowerPath} Z`;

    }

    const yTicks = [0, 0.33, 0.66, 1].map((ratio) => {

      const val = minY + ratio * (maxY - minY);

      return { val, y: getY(val) };

    });

    const firstDate = combinedPoints[0]?.date || "";

    const splitIdx = recentHistorical.length;

    const midDate = combinedPoints[splitIdx]?.date || "";

    const lastDate = combinedPoints[combinedPoints.length - 1]?.date || "";

    return (

      <div className="chart-wrapper">

        <svg viewBox={`0 0 ${width} ${height}`} className="svg-chart">

          {yTicks.map((tick, idx) => (

            <g key={idx}>

              <line

                x1={paddingLeft}

                y1={tick.y}

                x2={width - paddingRight}

                y2={tick.y}

                stroke="#334155"

                strokeDasharray="3,3"

                strokeWidth="1"

              />

              <text

                x={paddingLeft - 10}

                y={tick.y + 4}

                fill="#94a3b8"

                fontSize="11"

                textAnchor="end"

              >

                ₹{Math.round(tick.val / 1000)}k

              </text>

            </g>

          ))}

          {recentHistorical.length > 0 && forecast.length > 0 && (

            <line

              x1={lastHistX}

              y1={paddingTop}

              x2={lastHistX}

              y2={height - paddingBottom}

              stroke="#ffb86c"

              strokeDasharray="4,4"

              strokeWidth="1.5"

            />

          )}

          {areaPathD && <path d={areaPathD} fill="rgba(56, 239, 125, 0.18)" />}

          {histPathD && (

            <path

              d={histPathD}

              fill="none"

              stroke="#61dafb"

              strokeWidth="2.5"

            />

          )}

          {fcstPathD && (

            <path

              d={fcstPathD}

              fill="none"

              stroke="#38ef7d"

              strokeWidth="2.5"

              strokeDasharray="6,4"

            />

          )}

          <line

            x1={paddingLeft}

            y1={height - paddingBottom}

            x2={width - paddingRight}

            y2={height - paddingBottom}

            stroke="#334155"

            strokeWidth="1.5"

          />

          <text

            x={paddingLeft}

            y={height - 12}

            fill="#94a3b8"

            fontSize="11"

            textAnchor="start"

          >

            {firstDate}

          </text>

          <text

            x={lastHistX}

            y={height - 12}

            fill="#ffb86c"

            fontSize="11"

            textAnchor="middle"

            fontWeight="bold"

          >

            Forecast Start: {midDate}

          </text>

          <text

            x={width - paddingRight}

            y={height - 12}

            fill="#38ef7d"

            fontSize="11"

            textAnchor="end"

          >

            {lastDate}

          </text>

        </svg>

        <div className="chart-legend">

          <div className="legend-item">

            <span

              className="legend-color"

              style={{ backgroundColor: "#61dafb" }}

            />

            <span>Historical Daily Revenue (Recent 60 Days)</span>

          </div>

          <div className="legend-item">

            <span

              className="legend-color"

              style={{

                border: "2px dashed #38ef7d",

                backgroundColor: "transparent",

              }}

            />

            <span>Predicted Revenue ({forecastHorizon}-Day Horizon)</span>

          </div>

          <div className="legend-item">

            <span

              className="legend-color"

              style={{ backgroundColor: "rgba(56, 239, 125, 0.3)" }}

            />

            <span>90% Confidence Uncertainty Interval</span>

          </div>

        </div>

      </div>

    );

  };

  // ---------------------------------------------------

  // REGISTER & LOGIN HANDLERS

  // ---------------------------------------------------

  const handleRegister = async (e) => {

    e.preventDefault();

    try {

      const response = await fetch("/api/register", {

        method: "POST",

        headers: { "Content-Type": "application/json" },

        body: JSON.stringify({ username, password, role }),

      });

      const data = await response.json();

      if (response.ok) {

        setMessage("Registration successful! Please login.");

        setPassword("");

        setIsLogin(true);

        navigateJourney("login");
      } else {

        setMessage(data.detail || "Registration failed");

      }

    } catch (error) {

      setMessage("Backend connection failed");

    }

  };

  const handleLogin = async (e) => {

    e.preventDefault();

    try {

      const response = await fetch("/api/login", {

        method: "POST",

        headers: { "Content-Type": "application/json" },

        body: JSON.stringify({ username, password }),

      });

      const data = await response.json();

      if (response.ok) {

        localStorage.setItem("token", data.access_token);

        await loadProfile(data.access_token);
        setUsername("");
        setPassword("");
        setMessage("");
        setIsLoggedIn(true);
        setActivePage("dashboard");
        setJourneyStep("dashboard");
      } else {

        setMessage(data.detail || "Login failed");

      }

    } catch (error) {

      setMessage("Backend connection failed");

    }

  };

  const handleLogout = () => {

    localStorage.removeItem("token");

    localStorage.removeItem("role");

    localStorage.removeItem("username");

    setUserRole("");

    setCurrentUsername("");

    setActiveDatasetId(null);

    setActiveDatasetFilename("");

    setRevenue(0);

    setMargin(0);

    setLowStock(0);

    setCitySales({});

    setCategorySales({});

    setFilters({

      city: "All",

      category: "All",

      storeFormat: "All",

      channel: "All",

      paymentMode: "All",

    });

    setIsLoggedIn(false);

    setUsername("");

    setPassword("");

    setMessage("");

    navigateJourney("landing");
  };

  const handleActivateDataset = (datasetId, datasetFilename = "") => {
    setActiveDatasetId(datasetId);
    setActiveDatasetFilename(datasetFilename || "");
  };

  // ---------------------------------------------------

  // DOWNLOAD BUSINESS REPORT

  // ---------------------------------------------------

  const handleDownloadReport = async () => {

    const token = localStorage.getItem("token");

    if (!token) return;

    setIsDownloadingReport(true);

    try {

      const queryString = buildQueryString(filters);

      const reportQuery = queryString

        ? `${queryString}&horizon=${forecastHorizon}`

        : `?horizon=${forecastHorizon}`;

      const response = await fetch(`/api/export-report${reportQuery}`, {

        headers: { Authorization: `Bearer ${token}` },

      });

      if (!response.ok) {

        throw new Error("Report download failed");

      }

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");

      a.href = url;

      a.download = "MarketMind_AI_Business_Report.xlsx";

      document.body.appendChild(a);

      a.click();

      a.remove();

      window.URL.revokeObjectURL(url);

    } catch (err) {

      console.error("Report download error:", err);

      alert("Failed to download business report. Please try again.");

    } finally {

      setIsDownloadingReport(false);

    }

  };

  const resetFilters = () => {

    setFilters({

      city: "All",

      category: "All",

      storeFormat: "All",

      channel: "All",

      paymentMode: "All",

    });

  };

  const canViewRevenue =

    userRole === "Business Owner" || userRole === "Administrator";

  const canViewLowStock =

    userRole === "Business Owner" ||

    userRole === "Store Manager" ||

    userRole === "Administrator";

  const canViewForecast =

    userRole === "Business Owner" ||

    userRole === "Store Manager" ||

    userRole === "Administrator";

  // ---------------------------------------------------

  // LOGIN / REGISTER RENDER

  // ---------------------------------------------------

  if (!isLoggedIn) {

    if (journeyStep === "landing") {
      return (

        <LandingPage

          onLogin={() => {

            setIsLogin(true);

            setMessage("");

            navigateJourney("login");
          }}

          onGetStarted={() => {

            setIsLogin(false);

            setMessage("");

            navigateJourney("register");
          }}

          onUploadData={() => {
            setIsLogin(true);

            setMessage("");

            navigateJourney("login");
          }}

        />

      );

    }

    return (

      <div className="auth-container">

        <div className="auth-form">

          <h1>MarketMind AI</h1>

          <h2>{isLogin ? "Login to Workspace" : "Create Account"}</h2>

          <button

            type="button"

            className="landing-auth-home-button"

            onClick={() => {

              setMessage("");
              navigateJourney("landing");
            }}

          >

            ← Back to home

          </button>

          <form onSubmit={isLogin ? handleLogin : handleRegister}>

            <input

              type="text"

              placeholder="Username"

              value={username}

              onChange={(e) => setUsername(e.target.value)}

              required

            />

            <input

              type="password"

              placeholder="Password"

              value={password}

              onChange={(e) => setPassword(e.target.value)}

              required

            />

            {!isLogin && (

              <select

                value={role}

                onChange={(e) => setRole(e.target.value)}

              >

                <option value="Business Owner">Business Owner</option>

                <option value="Store Manager">Store Manager</option>

                <option value="Sales Executive">Sales Executive</option>

                <option value="Administrator">Administrator</option>

              </select>

            )}

            <button type="submit" className="auth-button">

              {isLogin ? "Login" : "Register"}

            </button>

          </form>

          {message && <p className="error-message">{message}</p>}

          <p className="auth-link">

            {isLogin ? "Don't have an account?" : "Already have an account?"}

            <button

              type="button"

              className="switch-button"

              onClick={() => {

                const nextStep = isLogin ? "register" : "login";
                setIsLogin(!isLogin);
                setMessage("");
                navigateJourney(nextStep);
              }}
            >

              {isLogin ? " Register" : " Login"}

            </button>

          </p>

        </div>

      </div>

    );

  }

  // ---------------------------------------------------
  // MAIN SAAS DASHBOARD SHELL RENDER

  // ---------------------------------------------------

  return (

    <div className={`app-container ${activePage === "dashboard" ? "dashboard-shell" : ""}`}>

      {/* DARK NAVY SIDEBAR */}

      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
      />

      {/* MAIN CONTENT AREA */}

      <div className="app-main-wrapper">

        {/* HEADER */}

        <Header

          activePage={activePage}

          currentUsername={currentUsername}

          userRole={userRole}

          handleLogout={handleLogout}

          canViewForecast={canViewForecast}

          handleDownloadReport={handleDownloadReport}

          isDownloadingReport={isDownloadingReport}

          activeDatasetId={activeDatasetId}

          activeDatasetFilename={activeDatasetFilename}

        />

        {/* ACTIVE PAGE CONTENT ROUTER */}

        <main className="app-main-content">

          {activePage === "dashboard" && (

            <DashboardOverviewPage

              revenue={revenue}

              margin={margin}

              lowStock={lowStock}

              canViewRevenue={canViewRevenue}

              canViewMargin={canViewMargin}

              canViewLowStock={canViewLowStock}

              canViewForecast={canViewForecast}

              filters={filters}

              setFilters={setFilters}

              filterOptions={filterOptions}

              resetFilters={resetFilters}

              salesTrends={salesTrends}

              renderTrendChart={renderTrendChart}

              trendGranularity={trendGranularity}

              setTrendGranularity={setTrendGranularity}

              forecastData={forecastData}

              segmentationData={segmentationData}

              segmentationMethod={segmentationMethod}

              churnData={churnData}

              dashboardDataStatus={dashboardDataStatus}

              dashboardRequestKey={dashboardRequestKey}

              anomalyData={anomalyData}
              setActivePage={setActivePage}

            />

          )}

          {activePage === "sales" && (

            <SalesPage

              filters={filters}

              setFilters={setFilters}

              filterOptions={filterOptions}

              resetFilters={resetFilters}

              salesTrends={salesTrends}

              renderTrendChart={renderTrendChart}

              trendGranularity={trendGranularity}

              setTrendGranularity={setTrendGranularity}

              brandChannelData={brandChannelData}

              citySales={citySales}

              categorySales={categorySales}

              canViewMargin={canViewMargin}

            />

          )}

          {activePage === "inventory" && (

            <InventoryPage

              filters={filters}

              setFilters={setFilters}

              filterOptions={filterOptions}

              resetFilters={resetFilters}

              inventoryIntel={inventoryIntel}

              canViewLowStock={canViewLowStock}

            />

          )}

          {activePage === "customers" && (

            <CustomersPage

              filters={filters}

              setFilters={setFilters}

              filterOptions={filterOptions}

              resetFilters={resetFilters}

              demographicIntel={demographicIntel}

              segmentationData={segmentationData}

              segmentationMethod={segmentationMethod}

              setActivePage={setActivePage}

            />

          )}

          {activePage === "invoices" && (

            <InvoicesPage

              filters={filters}

              setFilters={setFilters}

              filterOptions={filterOptions}

              resetFilters={resetFilters}

              inventoryIntel={inventoryIntel}

              anomalyData={anomalyData}

              churnData={churnData}

            />

          )}

          {activePage === "forecasting" && (

            <ForecastingPage

              filters={filters}

              setFilters={setFilters}

              filterOptions={filterOptions}

              resetFilters={resetFilters}

              canViewForecast={canViewForecast}

              forecastData={forecastData}

              forecastHorizon={forecastHorizon}

              setForecastHorizon={setForecastHorizon}

              forecastModel={forecastModel}

              setForecastModel={setForecastModel}

              renderForecastChart={renderForecastChart}

            />

          )}

          {activePage === "segmentation" && (

            <SegmentationPage

              filters={filters}

              setFilters={setFilters}

              filterOptions={filterOptions}

              resetFilters={resetFilters}

              segmentationData={segmentationData}

              segmentationMethod={segmentationMethod}

              setSegmentationMethod={setSegmentationMethod}

            />

          )}

          {activePage === "churn" && (

            <ChurnPage

              filters={filters}

              setFilters={setFilters}

              filterOptions={filterOptions}

              resetFilters={resetFilters}

              churnData={churnData}

            />

          )}

          {activePage === "recommendations" && (

            <RecommendationsPage

              filters={filters}

              setFilters={setFilters}

              filterOptions={filterOptions}

              resetFilters={resetFilters}

              recBrand={recBrand}

              setRecBrand={setRecBrand}

              recCategory={recCategory}

              setRecCategory={setRecCategory}

              recTopN={recTopN}

              setRecTopN={setRecTopN}

              recTab={recTab}

              setRecTab={setRecTab}

              recLoading={recLoading}

              recError={recError}

              recData={recData}

              fetchRecommendations={fetchRecommendations}

            />

          )}

          {activePage === "anomalies" && (

            <AnomalyPage

              filters={filters}

              setFilters={setFilters}

              filterOptions={filterOptions}

              resetFilters={resetFilters}

              anomalyData={anomalyData}

            />

          )}

          {activePage === "data-upload" && (

            <DataUploadPage

              activeDatasetId={activeDatasetId}

              activeDatasetFilename={activeDatasetFilename}

              onActivateDataset={handleActivateDataset}

              setActivePage={setActivePage}

            />

          )}

          {activePage === "reports" && (

            <ReportsPage

              filters={filters}

              setFilters={setFilters}

              filterOptions={filterOptions}

              resetFilters={resetFilters}

              handleDownloadReport={handleDownloadReport}

              isDownloadingReport={isDownloadingReport}

              forecastHorizon={forecastHorizon}

              setForecastHorizon={setForecastHorizon}

              canViewForecast={canViewForecast}

            />

          )}

          {activePage === "settings" && (

            <SettingsPage

              currentUsername={currentUsername}

              userRole={userRole}

              canViewRevenue={canViewRevenue}

              canViewMargin={canViewMargin}

              canViewLowStock={canViewLowStock}

              canViewForecast={canViewForecast}

              activeDatasetId={activeDatasetId}
              activeDatasetFilename={activeDatasetFilename}
            />
          )}

        </main>

      </div>

    </div>

  );

}

export default App;
