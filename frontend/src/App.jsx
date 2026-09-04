import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [showRegister, setShowRegister] = useState(false);

  const [registerData, setRegisterData] = useState({
    username: "",
    full_name: "",
    email: "",
    password: "",
    role: "Store Manager",
  });
  useEffect(() => {
  const token = localStorage.getItem("access_token");

  if (token) {
    loadDashboard(token).catch(() => {
      localStorage.removeItem("access_token");
      setDashboard(null);
    });
  }
}, []);

  // =========================
  // REGISTER
  // =========================
  const handleRegister = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/auth/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(registerData),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Registration failed"
        );
      }

      alert("Registration successful! Please login.");

      setShowRegister(false);

      setEmail(registerData.email);
      setPassword("");

      setRegisterData({
        username: "",
        full_name: "",
        email: "",
        password: "",
        role: "Store Manager",
      });
    } catch (error) {
      console.error(error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // LOGIN
  // =========================
  const handleLogin = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const formData = new URLSearchParams();

      formData.append("username", email);
      formData.append("password", password);

      const response = await fetch(
        "http://127.0.0.1:8000/api/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Login failed"
        );
      }

      // Store JWT token
      localStorage.setItem(
        "access_token",
        data.access_token
      );

      // Load dashboard
      await loadDashboard(data.access_token);
    } catch (error) {
      console.error(error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // LOAD DASHBOARD
  // =========================
  const loadDashboard = async (token) => {
    const response = await fetch(
      "http://127.0.0.1:8000/api/dashboard",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to load dashboard"
      );
    }

    setDashboard(data);
  };

  // =========================
  // LOGOUT
  // =========================
  const handleLogout = () => {
    // Remove JWT
    localStorage.removeItem("access_token");

    // Clear dashboard
    setDashboard(null);

    // Clear login fields
    setEmail("");
    setPassword("");

    // Clear errors
    setError("");

    // Show login page
    setShowRegister(false);
  };

  // =========================
  // REGISTER PAGE
  // =========================
  if (!dashboard && showRegister) {
    return (
      <div className="login-container">
        <div className="login-card">

          <h1>MarketMind AI</h1>

          <p className="login-subtitle">
            Create your account
          </p>

          <form onSubmit={handleRegister}>

            <label>Username</label>

            <input
              type="text"
              value={registerData.username}
              onChange={(event) =>
                setRegisterData({
                  ...registerData,
                  username: event.target.value,
                })
              }
              placeholder="Enter username"
              required
            />

            <label>Full Name</label>

            <input
              type="text"
              value={registerData.full_name}
              onChange={(event) =>
                setRegisterData({
                  ...registerData,
                  full_name: event.target.value,
                })
              }
              placeholder="Enter full name"
              required
            />

            <label>Email</label>

            <input
              type="email"
              value={registerData.email}
              onChange={(event) =>
                setRegisterData({
                  ...registerData,
                  email: event.target.value,
                })
              }
              placeholder="Enter email"
              required
            />

            <label>Password</label>

            <input
              type="password"
              value={registerData.password}
              onChange={(event) =>
                setRegisterData({
                  ...registerData,
                  password: event.target.value,
                })
              }
              placeholder="Minimum 8 characters"
              required
            />

            <label>Role</label>

            <select
              value={registerData.role}
              onChange={(event) =>
                setRegisterData({
                  ...registerData,
                  role: event.target.value,
                })
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

            {error && (
              <p className="error-message">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Registering..."
                : "Register"}
            </button>

          </form>

          <p className="switch-text">
            Already have an account?{" "}

            <button
              type="button"
              className="link-button"
              onClick={() => {
                setShowRegister(false);
                setError("");
              }}
            >
              Login
            </button>
          </p>

        </div>
      </div>
    );
  }

  // =========================
  // LOGIN PAGE
  // =========================
  if (!dashboard) {
    return (
      <div className="login-container">
        <div className="login-card">

          <h1>MarketMind AI</h1>

          <p className="login-subtitle">
            Sign in to your account
          </p>

          <form onSubmit={handleLogin}>

            <label>Email</label>

            <input
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="Enter your email"
              required
            />

            <label>Password</label>

            <input
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Enter your password"
              required
            />

            {error && (
              <p className="error-message">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Logging in..."
                : "Login"}
            </button>

          </form>

          <p className="switch-text">
            Don't have an account?{" "}

            <button
              type="button"
              className="link-button"
              onClick={() => {
                setShowRegister(true);
                setError("");
              }}
            >
              Register
            </button>
          </p>

        </div>
      </div>
    );
  }

  // =========================
  // DASHBOARD
  // =========================
  return (
    <div className="dashboard">

      <div className="dashboard-header">

        <div>
          <h1>MarketMind AI</h1>

          <p className="subtitle">
            {dashboard.message}
          </p>
        </div>

        <button
          className="logout-button"
          onClick={handleLogout}
        >
          Logout
        </button>

      </div>

      <p>
        <strong>Role:</strong>{" "}
        {dashboard.role}
      </p>

      <div className="cards">

        {dashboard.total_sales !== undefined && (
          <div className="card">
            <h3>Total Sales</h3>

            <p>
              ₹{dashboard.total_sales.toLocaleString()}
            </p>
          </div>
        )}

        {dashboard.total_orders !== undefined && (
          <div className="card">
            <h3>Total Orders</h3>

            <p>
              {dashboard.total_orders.toLocaleString()}
            </p>
          </div>
        )}

        {dashboard.total_customers !== undefined && (
          <div className="card">
            <h3>Total Customers</h3>

            <p>
              {dashboard.total_customers.toLocaleString()}
            </p>
          </div>
        )}

        {dashboard.total_products !== undefined && (
          <div className="card">
            <h3>Total Products</h3>

            <p>
              {dashboard.total_products.toLocaleString()}
            </p>
          </div>
        )}

        {dashboard.system_status !== undefined && (
          <div className="card">
            <h3>System Status</h3>

            <p>
              {dashboard.system_status}
            </p>
          </div>
        )}

        {dashboard.total_users !== undefined && (
          <div className="card">
            <h3>Total Users</h3>

            <p>
              {dashboard.total_users.toLocaleString()}
            </p>
          </div>
        )}

      </div>

    </div>
  );
}

export default App;