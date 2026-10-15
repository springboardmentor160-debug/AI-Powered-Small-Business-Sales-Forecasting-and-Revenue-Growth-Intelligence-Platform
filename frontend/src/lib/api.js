export const API_URL =
  import.meta.env.VITE_API_URL ||
  "https://marketmind-ai-deployment-1.onrender.com";

function formatDetail(detail, status) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return "Please check the value you entered and try again.";
  return `Request failed (${status})`;
}

/**
 * Single fetch wrapper used by every screen.
 * Throws Error objects with a friendly `message` and (for HTTP errors) `status`.
 */
export async function apiRequest(endpoint, accessToken, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        ...options.headers,
      },
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      const err = new Error(formatDetail(body.detail, response.status));
      err.status = response.status;
      throw err;
    }
    return body;
  } catch (error) {
    if (error.name === "AbortError")
      throw new Error("The server took too long to respond. Please try again.");
    if (error instanceof TypeError)
      throw new Error(
        "Couldn't reach the server. Check that the backend is running.",
      );
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}
