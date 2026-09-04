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
  // DASHBOARD STATES
  // ---------------------------------------------------

  const [revenue, setRevenue] = useState(0);
  const [margin, setMargin] = useState(0);
  const [lowStock, setLowStock] = useState(0);

  const [citySales, setCitySales] = useState({});
  const [categorySales, setCategorySales] = useState({});

  // ---------------------------------------------------
  // GET CURRENT USER PROFILE
  // ---------------------------------------------------

  const loadProfile = async (token) => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/profile",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

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
  // LOAD DASHBOARD DATA
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
      // Load profile and get current role
      let activeRole = userRole;

      if (!activeRole) {
        activeRole = await loadProfile(token);
      }

      // -----------------------------------------------
      // BUSINESS OWNER AND ADMINISTRATOR
      // Revenue and Margin access
      // -----------------------------------------------

      if (
        activeRole === "Business Owner" ||
        activeRole === "Administrator"
      ) {
        fetch(
          "http://127.0.0.1:8000/total-revenue",
          {
            headers: headers,
          }
        )
          .then((response) => response.json())
          .then((data) => {
            if (data.total_revenue !== undefined) {
              setRevenue(data.total_revenue);
            }
          })
          .catch((error) => console.error(error));

        fetch(
          "http://127.0.0.1:8000/total-margin",
          {
            headers: headers,
          }
        )
          .then((response) => response.json())
          .then((data) => {
            if (data.total_margin !== undefined) {
              setMargin(data.total_margin);
            }
          })
          .catch((error) => console.error(error));
      }

      // -----------------------------------------------
      // BUSINESS OWNER
      // STORE MANAGER
      // ADMINISTRATOR
      // Low Stock access
      // -----------------------------------------------

      if (
        activeRole === "Business Owner" ||
        activeRole === "Store Manager" ||
        activeRole === "Administrator"
      ) {
        fetch(
          "http://127.0.0.1:8000/low-stock",
          {
            headers: headers,
          }
        )
          .then((response) => response.json())
          .then((data) => {
            if (data.low_stock_records !== undefined) {
              setLowStock(data.low_stock_records);
            }
          })
          .catch((error) => console.error(error));
      }

      // -----------------------------------------------
      // ALL FOUR ROLES
      // City Sales access
      // -----------------------------------------------

      fetch(
        "http://127.0.0.1:8000/sales-by-city",
        {
          headers: headers,
        }
      )
        .then((response) => response.json())
        .then((data) => {
          if (!data.detail) {
            setCitySales(data);
          }
        })
        .catch((error) => console.error(error));

      // -----------------------------------------------
      // ALL FOUR ROLES
      // Category Sales access
      // -----------------------------------------------

      fetch(
        "http://127.0.0.1:8000/sales-by-category",
        {
          headers: headers,
        }
      )
        .then((response) => response.json())
        .then((data) => {
          if (!data.detail) {
            setCategorySales(data);
          }
        })
        .catch((error) => console.error(error));
    };

    loadDashboard();

  }, [isLoggedIn]);

  // ---------------------------------------------------
  // REGISTER FUNCTION
  // ---------------------------------------------------

  const handleRegister = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/register",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            username: username,
            password: password,
            role: role,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage(
          "Registration successful! Please login."
        );

        setPassword("");

        setIsLogin(true);

      } else {
        setMessage(
          data.detail || "Registration failed"
        );
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
      const response = await fetch(
        "http://127.0.0.1:8000/login",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            username: username,
            password: password,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        // Save JWT token
        localStorage.setItem(
          "token",
          data.access_token
        );

        // Get user profile and role
        await loadProfile(data.access_token);

        // Clear form
        setUsername("");
        setPassword("");
        setMessage("");

        // Open dashboard
        setIsLoggedIn(true);

      } else {
        setMessage(
          data.detail || "Login failed"
        );
      }

    } catch (error) {
      setMessage("Backend connection failed");
    }
  };

  // ---------------------------------------------------
  // LOGOUT FUNCTION
  // ---------------------------------------------------

  const handleLogout = () => {
    // Remove all stored user data
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("username");

    // Clear states
    setUserRole("");
    setCurrentUsername("");

    setRevenue(0);
    setMargin(0);
    setLowStock(0);

    setCitySales({});
    setCategorySales({});

    // Show login page
    setIsLoggedIn(false);

    setUsername("");
    setPassword("");
    setMessage("");
  };

  // ---------------------------------------------------
  // ROLE ACCESS CHECKS
  // ---------------------------------------------------

  const canViewRevenue =
    userRole === "Business Owner" ||
    userRole === "Administrator";

  const canViewMargin =
    userRole === "Business Owner" ||
    userRole === "Administrator";

  const canViewLowStock =
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

          <h2>
            {isLogin ? "Login" : "Register"}
          </h2>

          <form
            onSubmit={
              isLogin
                ? handleLogin
                : handleRegister
            }
          >

            {/* Username Input */}
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) =>
                setUsername(e.target.value)
              }
              required
            />

            {/* Password Input */}
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              required
            />

            {/* Role Selection */}
            {!isLogin && (
              <select
                value={role}
                onChange={(e) =>
                  setRole(e.target.value)
                }
              >

                <option value="Business Owner">
                  Business Owner
                </option>

                <option value="Store Manager">
                  Store Manager
                </option>

                <option value="Sales Executive">
                  Sales Executive
                </option>

                <option value="Administrator">
                  Administrator
                </option>

              </select>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              className="auth-button"
            >
              {isLogin ? "Login" : "Register"}
            </button>

          </form>

          {/* Message */}
          {message && (
            <p className="error-message">
              {message}
            </p>
          )}

          {/* Switch Login/Register */}
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
  // DASHBOARD PAGE
  // ---------------------------------------------------

  return (
    <div className="dashboard">

      {/* Dashboard Header */}
      <div className="dashboard-header">

        <div>

          <h1>MarketMind AI Dashboard</h1>

          <p className="user-info">
            Welcome, {currentUsername}
            {userRole && ` (${userRole})`}
          </p>

        </div>

        <button
          className="logout-button"
          onClick={handleLogout}
        >
          Logout
        </button>

      </div>

      {/* Summary Cards */}
      <div className="cards">

        {/* Total Revenue */}
        {canViewRevenue && (
          <div className="card">

            <h2>Total Revenue</h2>

            <p>
              ₹{Number(revenue).toLocaleString()}
            </p>

            <span>
              Total money earned from sales
            </span>

          </div>
        )}

        {/* Total Margin */}
        {canViewMargin && (
          <div className="card">

            <h2>Total Margin</h2>

            <p>
              ₹{Number(margin).toLocaleString()}
            </p>

            <span>
              Total profit earned
            </span>

          </div>
        )}

        {/* Low Stock */}
        {canViewLowStock && (
          <div className="card">

            <h2>Low Stock</h2>

            <p>
              {Number(lowStock).toLocaleString()}
            </p>

            <span>
              Products that need restocking
            </span>

          </div>
        )}

      </div>

      {/* City-wise Sales Section */}
      <div className="city-section">

        <h2>Sales by City</h2>

        <div className="city-grid">

          {Object.entries(citySales).map(
            ([city, sales]) => (

              <div
                className="city-card"
                key={city}
              >

                <h3>{city}</h3>

                <p>
                  ₹{Number(sales).toLocaleString()}
                </p>

              </div>

            )
          )}

        </div>

      </div>

      {/* Category-wise Sales Section */}
      <div className="category-section">

        <h2>Sales by Category</h2>

        <div className="category-grid">

          {Object.entries(categorySales).map(
            ([category, sales]) => (

              <div
                className="category-card"
                key={category}
              >

                <h3>{category}</h3>

                <p>
                  ₹{Number(sales).toLocaleString()}
                </p>

              </div>

            )
          )}

        </div>

      </div>

    </div>
  );
}

export default App;