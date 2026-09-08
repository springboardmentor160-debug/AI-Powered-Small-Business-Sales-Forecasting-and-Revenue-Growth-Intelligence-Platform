import React from "react";
import { Flame } from "lucide-react";

const MEDALS = ["🥇", "🥈", "🥉", "4", "5"];

export default function TopItemsPanel({ items }) {
  return (
    <div className="panel">
      <h3><Flame size={17} color="#FF6B6B" /> Top Selling Items</h3>
      {items.map((item, i) => (
        <div
          key={item.item_name}
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "10px 0",
            borderBottom: i < items.length - 1 ? "1px solid #ECE9F7" : "none",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: "1rem" }}>{MEDALS[i] || i + 1}</span>
            <div>
              <div style={{ fontWeight: 600, fontSize: "0.88rem" }}>{item.item_name}</div>
              <span className="category-chip">{item.category}</span>
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontWeight: 700, fontSize: "0.88rem" }}>₹{item.revenue.toLocaleString("en-IN")}</div>
            <div style={{ fontSize: "0.75rem", color: "#5B5478" }}>{item.units_sold} sold</div>
          </div>
        </div>
      ))}
    </div>
  );
}
