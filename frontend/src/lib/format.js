import { twMerge } from "tailwind-merge";

/** Joins class names and lets later Tailwind utilities override earlier ones. */
export function cn(...parts) {
  return twMerge(parts.flat(Infinity).filter(Boolean).join(" "));
}

const integerFormat = new Intl.NumberFormat("en-US");
const compactFormat = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumFractionDigits: 1,
});

function safe(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

export function formatNumber(value) {
  return integerFormat.format(safe(value));
}

export function formatCompact(value) {
  return compactFormat.format(safe(value));
}

export function formatCurrency(value, { decimals = 0 } = {}) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(safe(value));
}

export function formatPercent(value, decimals = 1) {
  return `${safe(value).toFixed(decimals)}%`;
}

export function formatDate(value, options) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  // UTC keeps "2024-03-04" from drifting a day in western time zones.
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    ...options,
    timeZone: "UTC",
  });
}

export function riskTone(value) {
  const v = String(value ?? "").toLowerCase();
  if (v.includes("high")) return "high";
  if (v.includes("med")) return "medium";
  if (v.includes("low")) return "low";
  return "neutral";
}

export function prettyRole(role) {
  return String(role ?? "").replace(/_/g, " ");
}

export function initials(name) {
  const parts = String(name ?? "")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  if (parts.length === 0) return "?";
  return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : ""))
    .toUpperCase();
}
