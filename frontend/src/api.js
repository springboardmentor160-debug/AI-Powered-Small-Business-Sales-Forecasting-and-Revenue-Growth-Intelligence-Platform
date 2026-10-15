import { useEffect, useState } from "react";

export const API = import.meta.env.VITE_API_URL || "/api";
/** Date-range options for the dashboard dropdown [value sent to the API, label]. */
export const RANGES = [["7d", "Last 7 days"], ["30d", "Last 30 days"], ["90d", "Last 90 days"], ["365d", "Last 12 months"], ["all", "All time"]];
export const rangeLabel = (r) => (RANGES.find(([k]) => k === r) || [])[1] || r;
export const money = (n, sym = "") => (n == null || n === "" ? "-" : sym + Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 }));

/** fetch wrapper: timeout, bearer token, friendly messages. Throws Error(message) with .status. */
export async function api(path, { token, method = "GET", body, blob } = {}) {
  let res;
  try {
    res = await fetch(API + path, {
      method,
      headers: { ...(body ? { "Content-Type": "application/json" } : {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(20000),
    });
  } catch (e) {
    throw new Error(e.name === "TimeoutError" ? "The server took too long to respond. Please try again in a moment."
                                              : "Couldn't reach the server. Please check your connection and try again.");
  }
  if (!res.ok) {
    let detail = "";
    try { const j = await res.json(); detail = typeof j.detail === "string" ? j.detail : "Please check your input."; } catch { /* not json */ }
    const err = new Error(detail || (res.status === 403 ? "You don't have permission to view this." : `Something went wrong (${res.status}).`));
    err.status = res.status;
    if (res.status === 401 && token) window.dispatchEvent(new Event("mm-unauthorized"));
    throw err;
  }
  if (res.status === 204) return null;
  return blob ? res.blob() : res.json();
}

/** { data, error, loading } for a GET endpoint; pass null path to skip. */
export function useFetch(path, token) {
  const [s, setS] = useState({ data: null, error: null, loading: !!path });
  useEffect(() => {
    if (!path) return;
    let off = false;
    setS((x) => ({ ...x, loading: true, error: null }));
    api(path, { token })
      .then((data) => !off && setS({ data, error: null, loading: false }))
      .catch((e) => !off && setS({ data: null, error: e.message, loading: false }));
    return () => { off = true; };
  }, [path, token]);
  return s;
}
