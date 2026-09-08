import React, { useState } from 'react';

export default function SalesTable({ sales = [] }) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredSales = sales.filter((s) => {
    const term = searchTerm.toLowerCase();
    return (
      s.order_id.toString().includes(term) ||
      s.product_name.toLowerCase().includes(term) ||
      s.customer_name.toLowerCase().includes(term) ||
      s.category.toLowerCase().includes(term)
    );
  });

  return (
    <div>
      <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Filter by order, product, or customer..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="form-input"
          style={{ maxWidth: '340px' }}
        />
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Showing {filteredSales.length} of {sales.length} orders
        </span>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Product</th>
              <th>Category</th>
              <th>Customer</th>
              <th>Qty</th>
              <th>Unit Price</th>
              <th>Total Amount</th>
              <th>Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredSales.length > 0 ? (
              filteredSales.map((sale) => (
                <tr key={sale.id}>
                  <td style={{ fontWeight: 700, color: '#38bdf8' }}>#{sale.order_id}</td>
                  <td style={{ fontWeight: 600 }}>{sale.product_name}</td>
                  <td>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                      {sale.category}
                    </span>
                  </td>
                  <td>{sale.customer_name}</td>
                  <td>{sale.quantity}</td>
                  <td>${sale.unit_price.toFixed(2)}</td>
                  <td style={{ fontWeight: 700, color: '#10b981' }}>
                    ${sale.total_amount.toFixed(2)}
                  </td>
                  <td>{sale.sale_date}</td>
                  <td>
                    <span className="status-pill status-paid">
                      {sale.payment_status || 'PAID'}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                  No transactions match your search filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
