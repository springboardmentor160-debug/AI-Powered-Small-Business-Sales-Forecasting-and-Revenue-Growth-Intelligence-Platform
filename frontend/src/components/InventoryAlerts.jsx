import React from 'react';

export default function InventoryAlerts({ alerts = [] }) {
  if (!alerts || alerts.length === 0) {
    return (
      <div
        style={{
          padding: '24px',
          textAlign: 'center',
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          borderRadius: 'var(--radius-sm)',
        }}
      >
        <span style={{ fontSize: '1.2rem' }}>✅</span>
        <h4 style={{ color: '#34d399', fontWeight: 700, marginTop: '4px' }}>All Inventory Healthy</h4>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
          No products are currently below their designated reorder threshold.
        </p>
      </div>
    );
  }

  return (
    <div>
      {alerts.map((item) => {
        const deficit = item.reorder_point - item.stock_level;
        return (
          <div key={item.id} className="alert-card">
            <div className="alert-card-info">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div className="pulse-dot"></div>
                <h4>{item.product_name}</h4>
                <span className="status-pill status-alert">Low Stock</span>
              </div>
              <p>
                Current Stock: <strong>{item.stock_level} units</strong> | Reorder Point: <strong>{item.reorder_point} units</strong>
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '0.75rem', color: '#f87171', fontWeight: 700, display: 'block' }}>
                Deficit: -{deficit} units
              </span>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                Replenishment required
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
