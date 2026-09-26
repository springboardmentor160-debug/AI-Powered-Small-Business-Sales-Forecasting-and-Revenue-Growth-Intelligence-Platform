// API Client for MarketMind AI backend

const API_BASE = ""; // Relative path leverages Vite dev server proxy

export const getStoredToken = () => {
  return localStorage.getItem("marketmind_token");
};

export const setStoredToken = (token) => {
  if (token) {
    localStorage.setItem("marketmind_token", token);
  } else {
    localStorage.removeItem("marketmind_token");
  }
};

export const getStoredUser = () => {
  const user = localStorage.getItem("marketmind_user");
  return user ? JSON.parse(user) : null;
};

export const setStoredUser = (user) => {
  if (user) {
    localStorage.setItem("marketmind_user", JSON.stringify(user));
  } else {
    localStorage.removeItem("marketmind_user");
  }
};

export const clearSession = () => {
  localStorage.removeItem("marketmind_token");
  localStorage.removeItem("marketmind_user");
};

async function apiRequest(endpoint, options = {}) {
  const token = getStoredToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // If unauthorized, clear invalid token
    clearSession();
    if (window.location.pathname !== "/") {
      window.dispatchEvent(new Event("auth-expired"));
    }
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const errorMsg = data?.detail || `API request failed with status ${response.status}`;
    throw new Error(errorMsg);
  }

  return data;
}

// Authentication
export async function login(username, password) {
  const data = await apiRequest("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  if (data.access_token) {
    setStoredToken(data.access_token);
    setStoredUser(data.user);
  }
  return data;
}

export async function getCurrentUser() {
  return await apiRequest("/api/v1/auth/me");
}

// Sales
export async function getSales() {
  return await apiRequest("/api/v1/sales");
}

export async function getSalesSummary() {
  return await apiRequest("/api/v1/sales/summary");
}

// Inventory
export async function getInventory() {
  return await apiRequest("/api/v1/inventory");
}

export async function getInventoryAlerts() {
  return await apiRequest("/api/v1/inventory/alerts");
}

// Analytics
export async function getAnalyticsSummary() {
  return await apiRequest("/api/v1/analytics/summary");
}

// Users (Admin only)
export async function getUsers() {
  return await apiRequest("/api/v1/users");
}

// Milestone 2 (Days 1–10): Segmentation, Multi-Model Forecasting & Reports
export async function getSegmentationSummary() {
  return await apiRequest("/api/v1/segmentation/summary");
}

export async function getSegmentationCustomers() {
  return await apiRequest("/api/v1/segmentation/customers");
}

export async function getSegments() {
  return await apiRequest("/segments");
}

export async function getForecastingSummary() {
  return await apiRequest("/api/v1/forecasting/summary");
}

export async function getForecastRevenue() {
  return await apiRequest("/forecast/revenue");
}

export async function getForecastModels() {
  return await apiRequest("/forecast/models");
}

export async function downloadBusinessReport() {
  const token = getStoredToken();
  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const response = await fetch("/api/v1/forecasting/report", { headers });
  if (!response.ok) {
    throw new Error("Failed to download business report.");
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "business_report.xlsx";
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

