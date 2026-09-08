import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";
import { PieChart } from "lucide-react";

const COLORS = ["#FF6B6B", "#7C5CFF", "#06D6A0", "#FFB800", "#4CC9F0"];

export default function CategoryChart({ data }) {
  return (
    <div className="panel">
      <h3><PieChart size={17} color="#7C5CFF" /> Revenue by Category</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ECE9F7" />
          <XAxis dataKey="category" tick={{ fontSize: 11, fill: "#5B5478" }} />
          <YAxis tick={{ fontSize: 11, fill: "#5B5478" }} />
          <Tooltip
            formatter={(value) => [`₹${value.toLocaleString("en-IN")}`, "Revenue"]}
            contentStyle={{ borderRadius: 10, border: "1px solid #ECE9F7" }}
          />
          <Bar dataKey="total_revenue" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={entry.category} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
