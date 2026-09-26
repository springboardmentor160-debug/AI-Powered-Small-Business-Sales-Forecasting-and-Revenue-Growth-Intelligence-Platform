import React from 'react';

export default function PlannedFeaturesNotice({ features = [] }) {
  const defaultFeatures = [
    'Milestone 3: AI Product Recommendation Engine (/recommendations)',
    'Milestone 3: Customer Churn Risk & Retention Intelligence',
    'Milestone 3: Automated Supplier Purchase Order Optimization',
  ];

  const displayList = features.length > 0 ? features : defaultFeatures;

  return (
    <div className="roadmap-banner">
      <div className="roadmap-icon">🚀</div>
      <div className="roadmap-text">
        <h4>Milestone 2 AI Roadmap Active</h4>
        <p>
          Milestone 1 foundation is operational. Advanced predictive AI and machine learning models are scheduled for deployment in Milestone 2:
        </p>
        <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {displayList.map((feat, idx) => (
            <span
              key={idx}
              style={{
                fontSize: '0.72rem',
                background: 'rgba(99, 102, 241, 0.14)',
                border: '1px solid rgba(99, 102, 241, 0.28)',
                color: '#c7d2fe',
                padding: '3px 8px',
                borderRadius: 'var(--radius-sm)',
                fontWeight: 600,
              }}
            >
              🔒 {feat}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
