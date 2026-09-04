import React from 'react';
import { CreditCard, DollarSign, Smartphone } from 'lucide-react';

export default function TransactionsTable({ transactions }) {
  if (!transactions || transactions.length === 0) {
    return <div style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>No recent transactions</div>;
  }

  const getPayIcon = (method) => {
    if (method.includes('Credit') || method.includes('Debit')) return <CreditCard size={14} />;
    if (method.includes('Cash')) return <DollarSign size={14} />;
    return <Smartphone size={14} />;
  };

  return (
    <div className="table-container">
      <table className="custom-table">
        <thead>
          <tr>
            <th>Txn ID</th>
            <th>Date & Time</th>
            <th>Product</th>
            <th>Qty</th>
            <th>Total Amount</th>
            <th>Store</th>
            <th>Payment</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => (
            <tr key={tx.transaction_id}>
              <td style={{ fontFamily: 'monospace', fontWeight: 600, color: '#06b6d4' }}>{tx.transaction_id}</td>
              <td style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{tx.transaction_date}</td>
              <td style={{ fontWeight: 500 }}>{tx.product_name || tx.product_id}</td>
              <td>{tx.quantity}</td>
              <td style={{ fontWeight: 700, color: '#10b981' }}>${tx.total_amount.toFixed(2)}</td>
              <td><span className="badge badge-purple">{tx.store_id}</span></td>
              <td>
                <span className="badge badge-warning" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  {getPayIcon(tx.payment_method)} {tx.payment_method}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
