const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
const REQUEST_TIMEOUT_MS = 15000;

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  const { token, ...fetchOptions } = options;
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...fetchOptions,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...fetchOptions.headers,
      },
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The request took too long. Please try again.");
    }
    throw new Error("The MarketMind service is unavailable. Check the backend connection and try again.");
  } finally {
    window.clearTimeout(timeoutId);
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = typeof payload.detail === "string" ? payload.detail : "";
    if (response.status === 401) {
      throw new Error("Your session has expired. Please sign in again.");
    }
    if (response.status === 403) {
      throw new Error("Your role is not permitted to access this data.");
    }
    throw new Error(detail || "The request could not be completed. Please try again.");
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
