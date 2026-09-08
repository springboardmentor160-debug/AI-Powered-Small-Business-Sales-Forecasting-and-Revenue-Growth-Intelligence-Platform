import React from "react";
import { Receipt } from "lucide-react";

export default function OrdersTable({ orders }) {
  return (
    <div className="panel" style={{ gridColumn: "1 / -1" }}>
      <h3><Receipt size={17} color="#06D6A0" /> Recent Orders</h3>
      <div style={{ overflowX: "auto" }}>
        <table>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Time</th>
              <th>Item</th>
              <th>Category</th>
              <th>Qty</th>
              <th>Amount</th>
              <th>Outlet</th>
              <th>Payment</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.order_id}>
                <td>{o.order_id}</td>
                <td>{o.order_time}</td>
                <td>{o.item_name}</td>
                <td><span className="category-chip">{o.category}</span></td>
                <td>{o.quantity}</td>
                <td>₹{o.total_amount.toLocaleString("en-IN")}</td>
                <td>{o.outlet_id}</td>
                <td>{o.payment_mode}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
