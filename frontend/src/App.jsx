import { useEffect, useState } from "react";
import "./App.css";

function App() {
  // ---------------------------------------------------
  // AUTHENTICATION STATES
  // ---------------------------------------------------

  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem("token")
  );

  const [isLogin, setIsLogin] = useState(true);

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

  // ---------------------------------------------------
  // GET CURRENT USER PROFILE
  // ---------------------------------------------------

  const loadProfile = async (token) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/profile", {
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

      // 1. Fetch Filter Options
      fetch("http://127.0.0.1:8000/filter-options", { headers })
        .then((res) => res.json())
        .then((data) => {
          if (!data.detail) {
            setFilterOptions(data);
          }
        })
        .catch((err) => console.error(err));

      // 2. Revenue and Margin (Business Owner & Admin)
      if (activeRole === "Business Owner" || activeRole === "Administrator") {
        fetch(`http://127.0.0.1:8000/total-revenue${queryString}`, { headers })
          .then((res) => res.json())
          .then((data) => {
            if (data.total_revenue !== undefined) {
              setRevenue(data.total_revenue);
            }
          })
          .catch((err) => console.error(err));

        fetch(`http://127.0.0.1:8000/total-margin${queryString}`, { headers })
          .then((res) => res.json())
          .then((data) => {
            if (data.total_margin !== undefined) {
              setMargin(data.total_margin);
            }
          })
          .catch((err) => console.error(err));
      }

      // 3. Low Stock (Business Owner, Store Manager, Admin)
      if (
        activeRole === "Business Owner" ||
        activeRole === "Store Manager" ||
        activeRole === "Administrator"
      ) {
        fetch(`http://127.0.0.1:8000/low-stock${queryString}`, { headers })
          .then((res) => res.json())
          .then((data) => {
            if (data.low_stock_records !== undefined) {
              setLowStock(data.low_stock_records);
            }
          })
          .catch((err) => console.error(err));

        // Inventory Intelligence endpoint
        fetch(`http://127.0.0.1:8000/inventory-intelligence${queryString}`, {
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
      fetch(`http://127.0.0.1:8000/sales-by-city${queryString}`, { headers })
        .then((res) => res.json())
        .then((data) => {
          if (!data.detail) {
            setCitySales(data);
          }
        })
        .catch((err) => console.error(err));

      fetch(`http://127.0.0.1:8000/sales-by-category${queryString}`, {
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

      fetch(`http://127.0.0.1:8000/sales-trends${trendQuery}`, { headers })
        .then((res) => res.json())
        .then((data) => {
          if (Array.isArray(data)) {
            setSalesTrends(data);
          }
        })
        .catch((err) => console.error(err));

      // 6. Brand & Channel Analytics (All 4 roles)
      fetch(`http://127.0.0.1:8000/brand-channel-analytics${queryString}`, {
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
      fetch(`http://127.0.0.1:8000/demographic-analytics${queryString}`, {
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
      fetch(`http://127.0.0.1:8000/customer-segmentation${queryString}`, {
        headers,
      })
        .then((res) => res.json())
        .then((data) => {
          if (!data.detail) {
            setSegmentationData(data);
          }
        })
        .catch((err) => console.error(err));


      // 9. Sales Forecasting
      const canViewForecastActive =
        activeRole === "Business Owner" ||
        activeRole === "Store Manager" ||
        activeRole === "Administrator";

      if (canViewForecastActive) {
        const forecastQuery = queryString
          ? `${queryString}&horizon=${forecastHorizon}&model_type=${forecastModel}`
          : `?horizon=${forecastHorizon}&model_type=${forecastModel}`;

        fetch(`http://127.0.0.1:8000/sales-forecast${forecastQuery}`, {
          headers,
        })
          .then((res) => res.json())
          .then((data) => {
            if (!data.detail) {
              setForecastData(data);
            }
          })
          .catch((err) => console.error(err));
      }
    };

    loadDashboard();
  }, [isLoggedIn, filters, trendGranularity, forecastHorizon, forecastModel]);

  // ---------------------------------------------------
  // RENDER SALES FORECAST SVG CHART HELPER
  // ---------------------------------------------------

  const renderForecastChart = () => {
    const historical = forecastData.historical_data || [];
    const forecast = forecastData.forecast_data || [];

    if (historical.length === 0 && forecast.length === 0) {
      return (
        <div style={{ padding: "40px", textAlign: "center", color: "#b0b0c0" }}>
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
                stroke="#3a3a50"
                strokeDasharray="3,3"
                strokeWidth="1"
              />
              <text
                x={paddingLeft - 10}
                y={tick.y + 4}
                fill="#b0b0c0"
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
            stroke="#3a3a50"
            strokeWidth="1.5"
          />

          <text
            x={paddingLeft}
            y={height - 12}
            fill="#b0b0c0"
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
  // REGISTER FUNCTION
  // ---------------------------------------------------

  const handleRegister = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          password: password,
          role: role,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage("Registration successful! Please login.");
        setPassword("");
        setIsLogin(true);
      } else {
        setMessage(data.detail || "Registration failed");
      }
    } catch (error) {
      setMessage("Backend connection failed");
    }
  };

  // ---------------------------------------------------
  // LOGIN FUNCTION
  // ---------------------------------------------------

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("token", data.access_token);
        await loadProfile(data.access_token);

        setUsername("");
        setPassword("");
        setMessage("");
        setIsLoggedIn(true);
      } else {
        setMessage(data.detail || "Login failed");
      }
    } catch (error) {
      setMessage("Backend connection failed");
    }
  };

  // ---------------------------------------------------
  // LOGOUT FUNCTION
  // ---------------------------------------------------

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("username");

    setUserRole("");
    setCurrentUsername("");

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
  };

  // ---------------------------------------------------
  // DOWNLOAD BUSINESS REPORT (DAY 9)
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

      const response = await fetch(`http://127.0.0.1:8000/export-report${reportQuery}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
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

  // ---------------------------------------------------
  // RESET FILTERS
  // ---------------------------------------------------

  const resetFilters = () => {
    setFilters({
      city: "All",
      category: "All",
      storeFormat: "All",
      channel: "All",
      paymentMode: "All",
    });
  };

  // ---------------------------------------------------
  // ROLE ACCESS CHECKS
  // ---------------------------------------------------

  const canViewRevenue =
    userRole === "Business Owner" || userRole === "Administrator";

  const canViewMargin =
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
  // REGISTER / LOGIN PAGE
  // ---------------------------------------------------

  if (!isLoggedIn) {
    return (
      <div className="auth-container">
        <div className="auth-form">
          <h1>MarketMind AI</h1>
          <h2>{isLogin ? "Login" : "Register"}</h2>

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
            {isLogin
              ? "Don't have an account?"
              : "Already have an account?"}

            <button
              type="button"
              className="switch-button"
              onClick={() => {
                setIsLogin(!isLogin);
                setMessage("");
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
  // HELPER FOR SVG LINE CHART (SALES TRENDS)
  // ---------------------------------------------------

  const renderTrendChart = () => {
    if (!salesTrends || salesTrends.length === 0) {
      return <p style={{ color: "#b0b0c0" }}>No trend data available for current filters.</p>;
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
          {/* Horizontal Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct, idx) => {
            const y = height - padding - pct * (height - padding * 2);
            return (
              <g key={idx}>
                <line
                  x1={padding}
                  y1={y}
                  x2={width - padding}
                  y2={y}
                  stroke="#3a3a50"
                  strokeDasharray="4"
                />
                <text
                  x={padding - 8}
                  y={y + 4}
                  fill="#b0b0c0"
                  fontSize="10"
                  textAnchor="end"
                >
                  ₹{Math.round((maxVal * pct) / 1000)}k
                </text>
              </g>
            );
          })}

          {/* Revenue Line */}
          <polyline
            fill="none"
            stroke="#61dafb"
            strokeWidth="3"
            points={revPoints}
          />

          {/* Margin Line */}
          {canViewMargin && (
            <polyline
              fill="none"
              stroke="#38ef7d"
              strokeWidth="3"
              points={marginPoints}
            />
          )}

          {/* Data Points & X Labels */}
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
                  fill="#b0b0c0"
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
  // DASHBOARD PAGE
  // ---------------------------------------------------

  return (
    <div className="dashboard">
      {/* Dashboard Header */}
      <div className="dashboard-header">
        <div className="dashboard-title-group">
          <h1>MarketMind AI Dashboard</h1>
          <p className="user-info">
            Welcome, {currentUsername}
            {userRole && ` (${userRole})`}
          </p>
        </div>

        <div className="header-actions">
          {canViewForecast && (
            <button
              className="report-button"
              onClick={handleDownloadReport}
              disabled={isDownloadingReport}
            >
              {isDownloadingReport ? "⏳ Generating Report..." : "📊 Download Business Report"}
            </button>
          )}

          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      {/* GLOBAL FILTER BAR (MILESTONE 2) */}
      <div className="filter-bar-container">
        <div className="filter-bar-header">
          <h3>🔍 Dynamic Dashboard Filters</h3>
          <button className="reset-filters-btn" onClick={resetFilters}>
            Reset Filters
          </button>
        </div>

        <div className="filter-controls">
          {/* City Filter */}
          <div className="filter-group">
            <label>City</label>
            <select
              value={filters.city}
              onChange={(e) => setFilters({ ...filters, city: e.target.value })}
            >
              <option value="All">All Cities</option>
              {filterOptions.cities.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* Category Filter */}
          <div className="filter-group">
            <label>Category</label>
            <select
              value={filters.category}
              onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            >
              <option value="All">All Categories</option>
              {filterOptions.categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Store Format Filter */}
          <div className="filter-group">
            <label>Store Format</label>
            <select
              value={filters.storeFormat}
              onChange={(e) =>
                setFilters({ ...filters, storeFormat: e.target.value })
              }
            >
              <option value="All">All Formats</option>
              {filterOptions.store_formats.map((sf) => (
                <option key={sf} value={sf}>
                  {sf}
                </option>
              ))}
            </select>
          </div>

          {/* Channel Filter */}
          <div className="filter-group">
            <label>Channel</label>
            <select
              value={filters.channel}
              onChange={(e) => setFilters({ ...filters, channel: e.target.value })}
            >
              <option value="All">All Channels</option>
              {filterOptions.channels.map((ch) => (
                <option key={ch} value={ch}>
                  {ch}
                </option>
              ))}
            </select>
          </div>

          {/* Payment Mode Filter */}
          <div className="filter-group">
            <label>Payment Mode</label>
            <select
              value={filters.paymentMode}
              onChange={(e) =>
                setFilters({ ...filters, paymentMode: e.target.value })
              }
            >
              <option value="All">All Payment Modes</option>
              {filterOptions.payment_modes.map((pm) => (
                <option key={pm} value={pm}>
                  {pm}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="cards">
        {canViewRevenue && (
          <div className="card">
            <h2>Total Revenue</h2>
            <p>₹{Number(revenue).toLocaleString()}</p>
            <span>Filtered Total Earned</span>
          </div>
        )}

        {canViewMargin && (
          <div className="card">
            <h2>Total Margin</h2>
            <p>₹{Number(margin).toLocaleString()}</p>
            <span>Filtered Net Profit</span>
          </div>
        )}

        {canViewLowStock && (
          <div className="card">
            <h2>Low Stock</h2>
            <p>{Number(lowStock).toLocaleString()}</p>
            <span>Items Needing Restock</span>
          </div>
        )}
      </div>

      {/* SALES TRENDS & REVENUE GROWTH SECTION (MILESTONE 2) */}
      <div className="m2-section">
        <div className="m2-section-header">
          <div>
            <h2>📈 Time-Series Sales & Margin Trends</h2>
            <p className="m2-subtitle">
              Revenue & Margin over time based on current filters
            </p>
          </div>

          <div className="toggle-group">
            <button
              className={`toggle-btn ${
                trendGranularity === "monthly" ? "active" : ""
              }`}
              onClick={() => setTrendGranularity("monthly")}
            >
              Monthly
            </button>
            <button
              className={`toggle-btn ${
                trendGranularity === "quarterly" ? "active" : ""
              }`}
              onClick={() => setTrendGranularity("quarterly")}
            >
              Quarterly
            </button>
          </div>
        </div>

        {renderTrendChart()}
      </div>

      {/* BRAND & CHANNEL INTELLIGENCE SECTION (MILESTONE 2) */}
      <div className="m2-section">
        <div className="m2-section-header">
          <div>
            <h2>🏷️ Brand & Sales Channel Performance</h2>
            <p className="m2-subtitle">
              Revenue performance across FMCG brands and fulfillment channels
            </p>
          </div>
        </div>

        <div className="brand-channel-grid">
          {/* Brand Breakdown */}
          <div>
            <h3 style={{ color: "#ffffff", marginTop: 0 }}>Top Brand Revenue</h3>
            <div className="brand-bar-list">
              {brandChannelData.by_brand.map((b) => {
                const maxBrandRev = brandChannelData.by_brand[0]?.revenue || 1;
                const widthPct = Math.round((b.revenue / maxBrandRev) * 100);

                return (
                  <div className="brand-bar-row" key={b.brand}>
                    <div className="brand-row-info">
                      <span>{b.brand}</span>
                      <span>
                        ₹{Number(b.revenue).toLocaleString()} ({b.units} units)
                      </span>
                    </div>
                    <div className="brand-bar-track">
                      <div
                        className="brand-bar-fill"
                        style={{ width: `${widthPct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Channel Breakdown */}
          <div>
            <h3 style={{ color: "#ffffff", marginTop: 0 }}>Fulfillment Channels</h3>
            <div className="channel-card-list">
              {brandChannelData.by_channel.map((ch) => (
                <div className="channel-card" key={ch.channel}>
                  <div>
                    <div className="channel-name">{ch.channel}</div>
                    <div style={{ color: "#b0b0c0", fontSize: "13px" }}>
                      {ch.units.toLocaleString()} units sold
                    </div>
                  </div>
                  <div className="channel-revenue">
                    ₹{Number(ch.revenue).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* INVENTORY INTELLIGENCE & REORDER RISK SECTION (MILESTONE 2) */}
      {canViewLowStock && (
        <div className="m2-section">
          <div className="m2-section-header">
            <div>
              <h2>📦 Inventory Intelligence & Stockout Risk</h2>
              <p className="m2-subtitle">
                Priority items requiring vendor reorder based on Lead Time
              </p>
            </div>
          </div>

          <div className="inventory-summary-cards">
            <div className="inv-summary-card">
              <h4>Total Urgent Reorder Items</h4>
              <p>{inventoryIntel.total_low_stock_count.toLocaleString()}</p>
            </div>

            {Object.entries(inventoryIntel.by_category || {}).map(
              ([cat, count]) => (
                <div className="inv-summary-card" key={cat}>
                  <h4>{cat} Low Stock</h4>
                  <p style={{ color: "#ffb86c" }}>{count.toLocaleString()}</p>
                </div>
              )
            )}
          </div>

          <h3 style={{ color: "#ffffff", marginBottom: "10px" }}>
            Top Urgent Inventory Reorder Alerts
          </h3>
          <div className="inventory-table-container">
            <table className="inventory-table">
              <thead>
                <tr>
                  <th>Invoice ID</th>
                  <th>City</th>
                  <th>Category</th>
                  <th>Brand</th>
                  <th>Stock On Hand</th>
                  <th>Reorder Level</th>
                  <th>Deficit</th>
                  <th>Lead Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {inventoryIntel.critical_items.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.invoice_id}</td>
                    <td>{item.city}</td>
                    <td>{item.category}</td>
                    <td>{item.brand}</td>
                    <td>{item.stock_on_hand}</td>
                    <td>{item.reorder_level}</td>
                    <td style={{ color: "#ff6b6b", fontWeight: "bold" }}>
                      -{item.deficit}
                    </td>
                    <td>{item.lead_time_days} days</td>
                    <td>
                      <span
                        className={
                          item.deficit > 20
                            ? "badge-critical"
                            : "badge-warning"
                        }
                      >
                        {item.deficit > 20 ? "CRITICAL" : "REORDER NEEDED"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* DEMOGRAPHIC & LOYALTY SEGMENT INTELLIGENCE (MILESTONE 2) */}
      <div className="m2-section">
        <div className="m2-section-header">
          <div>
            <h2>👥 Demographic Cohorts & Loyalty Intelligence</h2>
            <p className="m2-subtitle">
              Aggregated spend patterns across Age Brackets, Gender, and Loyalty Tiers
            </p>
          </div>
        </div>

        <div className="demo-grid">
          {/* Age Group Box */}
          <div className="demo-box">
            <h3>Age Bracket Revenue</h3>
            {demographicIntel.by_age_group.map((ag) => (
              <div className="demo-item" key={ag.age_group}>
                <span className="demo-item-label">Age {ag.age_group}</span>
                <span className="demo-item-value">
                  ₹{Number(ag.revenue).toLocaleString()}
                </span>
              </div>
            ))}
          </div>

          {/* Gender Box */}
          <div className="demo-box">
            <h3>Gender Distribution</h3>
            {demographicIntel.by_gender.map((g) => (
              <div className="demo-item" key={g.gender}>
                <span className="demo-item-label">
                  {g.gender === "M"
                    ? "Male"
                    : g.gender === "F"
                    ? "Female"
                    : g.gender === "O"
                    ? "Other"
                    : "Unspecified"}
                </span>
                <span className="demo-item-value">
                  ₹{Number(g.revenue).toLocaleString()}
                </span>
              </div>
            ))}
          </div>

          {/* Loyalty Box */}
          <div className="demo-box">
            <h3>Loyalty Status Segment</h3>
            {demographicIntel.by_loyalty.map((l) => (
              <div className="demo-item" key={l.loyalty_status}>
                <span className="demo-item-label">{l.loyalty_status}</span>
                <span className="demo-item-value">
                  ₹{Number(l.revenue).toLocaleString()} (Avg ₹{l.avg_ticket})
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* SALES FORECASTING & REVENUE PREDICTION INTELLIGENCE (DAY 5 & 6) */}
      {canViewForecast && (
        <div className="m2-section">
          <div className="m2-section-header">
            <div>
              <h2>🔮 Sales Forecasting & Revenue Prediction Intelligence</h2>
              <p className="m2-subtitle">
                Time-Series revenue prediction and predictive trend modelling
              </p>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "15px", flexWrap: "wrap" }}>
              <span className="model-tag">
                Engine: {forecastData.model_used || "Prophet Engine"}
              </span>

              <div className="toggle-group">
                <button
                  className={`toggle-btn ${
                    forecastModel === "prophet" ? "active" : ""
                  }`}
                  onClick={() => setForecastModel("prophet")}
                >
                  Prophet
                </button>
                <button
                  className={`toggle-btn ${
                    forecastModel === "xgboost" ? "active" : ""
                  }`}
                  onClick={() => setForecastModel("xgboost")}
                >
                  XGBoost
                </button>
                <button
                  className={`toggle-btn ${
                    forecastModel === "random_forest" ? "active" : ""
                  }`}
                  onClick={() => setForecastModel("random_forest")}
                >
                  Random Forest
                </button>
              </div>

              <div className="toggle-group">
                <button
                  className={`toggle-btn ${
                    forecastHorizon === 30 ? "active" : ""
                  }`}
                  onClick={() => setForecastHorizon(30)}
                >
                  30 Days
                </button>
                <button
                  className={`toggle-btn ${
                    forecastHorizon === 60 ? "active" : ""
                  }`}
                  onClick={() => setForecastHorizon(60)}
                >
                  60 Days
                </button>
                <button
                  className={`toggle-btn ${
                    forecastHorizon === 90 ? "active" : ""
                  }`}
                  onClick={() => setForecastHorizon(90)}
                >
                  90 Days
                </button>
              </div>
            </div>
          </div>

          {/* Forecast Metric Summary Cards */}
          <div className="forecast-summary-cards">
            <div className="forecast-card">
              <h4>Historical Daily Revenue Avg</h4>
              <p>
                ₹
                {Number(
                  forecastData.summary_metrics?.historical_avg_daily_revenue || 0
                ).toLocaleString()}
              </p>
              <span>Based on 366-day daily transaction logs</span>
            </div>

            <div className="forecast-card">
              <h4>Projected {forecastHorizon}-Day Total Revenue</h4>
              <p style={{ color: "#38ef7d" }}>
                ₹
                {Number(
                  forecastData.summary_metrics?.projected_period_total_revenue || 0
                ).toLocaleString()}
              </p>
              <span>Cumulative forecast for next {forecastHorizon} days</span>
            </div>

            <div className="forecast-card">
              <h4>Projected Growth Rate</h4>
              <p
                style={{
                  color:
                    (forecastData.summary_metrics?.projected_growth_pct || 0) >= 0
                      ? "#38ef7d"
                      : "#ff6b6b",
                }}
              >
                {(forecastData.summary_metrics?.projected_growth_pct || 0) >= 0
                  ? "+"
                  : ""}
                {forecastData.summary_metrics?.projected_growth_pct || 0}%
              </p>
              <span>Expected growth vs historical daily mean</span>
            </div>
          </div>

          {/* SVG Forecast Chart */}
          {renderForecastChart()}
        </div>
      )}

      {/* CUSTOMER SEGMENTATION & CLUSTERING INTELLIGENCE (DAY 3 & 4) */}
      <div className="m2-section">
        <div className="m2-section-header">
          <div>
            <h2>🎯 Customer Segmentation & Clustering Intelligence</h2>
            <p className="m2-subtitle">
              Machine Learning cohort segmentation using K-Means and Hierarchical Clustering
            </p>
          </div>

          <div className="toggle-group">
            <button
              className={`toggle-btn ${
                segmentationMethod === "kmeans" ? "active" : ""
              }`}
              onClick={() => setSegmentationMethod("kmeans")}
            >
              K-Means (k=4)
            </button>
            <button
              className={`toggle-btn ${
                segmentationMethod === "hierarchical" ? "active" : ""
              }`}
              onClick={() => setSegmentationMethod("hierarchical")}
            >
              Hierarchical (n=4)
            </button>
          </div>
        </div>

        {/* 4 Segment Cards */}
        <div className="segmentation-grid">
          {(segmentationMethod === "kmeans"
            ? segmentationData.kmeans_profiles
            : segmentationData.hierarchical_profiles
          ).map((seg) => (
            <div className="segment-card" key={seg.cluster_id}>
              <div>
                <div className="segment-card-header">
                  <h4 className="segment-title">{seg.segment_name}</h4>
                  <span className="segment-badge">Cluster {seg.cluster_id}</span>
                </div>

                <div className="segment-metrics">
                  <div className="segment-metric-row">
                    <span className="segment-metric-label">Mean Purchase Value:</span>
                    <span className="segment-metric-value">₹{seg.mean_purchase_value.toLocaleString()}</span>
                  </div>
                  <div className="segment-metric-row">
                    <span className="segment-metric-label">Mean Purchase Freq:</span>
                    <span className="segment-metric-value">{seg.mean_purchase_frequency} units</span>
                  </div>
                  <div className="segment-metric-row">
                    <span className="segment-metric-label">Mean Activity Recency:</span>
                    <span className="segment-metric-value">{seg.mean_customer_activity_days} days</span>
                  </div>
                  <div className="segment-metric-row">
                    <span className="segment-metric-label">Cohort Records:</span>
                    <span className="segment-metric-value">{seg.record_count.toLocaleString()} ({seg.percentage}%)</span>
                  </div>
                </div>
              </div>

              <div className="segment-share-bar">
                <div
                  className="segment-share-fill"
                  style={{ width: `${Math.min(seg.percentage * 3, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>


      </div>
    </div>
  );
}

export default App;