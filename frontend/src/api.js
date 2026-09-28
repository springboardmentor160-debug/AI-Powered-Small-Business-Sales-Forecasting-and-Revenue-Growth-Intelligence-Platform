const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed with status ${response.status}`);
  }
  return response.json();
}

async function fetchSummary(path, token) {
  return request(path, { token });
}

export function login(email, password) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function fetchCurrentUser(token) {
  return request("/auth/me", { token });
}

export function logout(token) {
  return request("/auth/logout", { method: "POST", token });
}

export function fetchDashboardData(token) {
  return Promise.all([
    fetchSummary("/sales/summary", token),
    fetchSummary("/inventory/summary", token),
    fetchSummary("/customers/summary", token),
  ]).then(([sales, inventory, customers]) => ({
    sales,
    inventory,
    customers,
  }));
}

export function fetchReportingData(token) {
  return Promise.all([
    request("/segments", { token }),
    request("/forecast/revenue", { token }),
  ]).then(([segments, revenueForecast]) => ({
    segments,
    revenueForecast,
  }));
}
