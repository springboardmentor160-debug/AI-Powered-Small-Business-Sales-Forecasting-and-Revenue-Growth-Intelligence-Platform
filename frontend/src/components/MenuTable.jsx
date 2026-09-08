import React from "react";
import { Soup } from "lucide-react";

export default function MenuTable({ items }) {
  return (
    <div className="panel" style={{ gridColumn: "1 / -1" }}>
      <h3><Soup size={17} color="#FFA53E" /> Menu & Stock Levels</h3>
      <div style={{ overflowX: "auto" }}>
        <table>
          <thead>
            <tr>
              <th>Item</th>
              <th>Category</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Reorder Level</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.item_id}>
                <td>{item.item_name}</td>
                <td><span className="category-chip">{item.category}</span></td>
                <td>₹{item.unit_price.toLocaleString("en-IN")}</td>
                <td>{item.stock_units}</td>
                <td>{item.reorder_level}</td>
                <td>
                  <span className={`badge ${item.needs_restock ? "low" : "ok"}`}>
                    {item.needs_restock ? "Restock Needed" : "In Stock"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
