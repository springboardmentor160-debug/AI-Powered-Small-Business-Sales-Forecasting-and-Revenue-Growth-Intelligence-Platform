import React from 'react';
import { AlertTriangle, ArrowRight } from 'lucide-react';

export default function LowStockAlert({ count, onReorderClick }) {
  if (count <= 0) return null;

  return (
    <div className="alert-banner">
      <div className="alert-info">
        <AlertTriangle size={20} color="#ef4444" />
        <div>
          <strong>Inventory Alert:</strong> {count} item(s) are at or below reorder threshold levels.
        </div>
      </div>
      <button className="btn btn-secondary" onClick={onReorderClick} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        Review Stock <ArrowRight size={14} />
      </button>
    </div>
  );
}
