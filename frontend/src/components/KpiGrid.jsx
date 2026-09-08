import React from "react";
import { IndianRupee, ShoppingBag, Utensils, AlertTriangle } from "lucide-react";

export default function KpiGrid({ summary }) {
  if (!summary) return null;

  const cards = [
    {
      grad: "grad-1",
      icon: IndianRupee,
      label: "Total Revenue",
      value: `₹${summary.total_revenue.toLocaleString("en-IN")}`,
    },
    {
      grad: "grad-2",
      icon: ShoppingBag,
      label: "Total Orders",
      value: summary.total_orders.toLocaleString("en-IN"),
    },
    {
      grad: "grad-3",
      icon: Utensils,
      label: "Items Sold",
      value: summary.total_items_sold.toLocaleString("en-IN"),
    },
    {
      grad: "grad-4",
      icon: AlertTriangle,
      label: "Low Stock Items",
      value: summary.low_stock_count,
    },
  ];

  return (
    <div className="kpi-grid">
      {cards.map((c) => (
        <div key={c.label} className={`kpi-card ${c.grad}`}>
          <div className="kpi-icon">
            <c.icon size={19} />
          </div>
          <div className="kpi-label">{c.label}</div>
          <div className="kpi-value">{c.value}</div>
        </div>
      ))}
    </div>
  );
}
