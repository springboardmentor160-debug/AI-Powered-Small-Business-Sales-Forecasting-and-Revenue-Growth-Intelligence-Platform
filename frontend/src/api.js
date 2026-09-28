const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function fetchSummary(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
}

export function fetchDashboardData() {
  return Promise.all([
    fetchSummary("/sales/summary"),
    fetchSummary("/inventory/summary"),
    fetchSummary("/customers/summary"),
  ]).then(([sales, inventory, customers]) => ({ sales, inventory, customers }));
}
