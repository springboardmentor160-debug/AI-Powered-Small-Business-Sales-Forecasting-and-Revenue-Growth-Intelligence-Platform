import React, { useState, useEffect } from 'react';
import { getRecommendations, getRecommendationsCollaborative, getRecommendationsAssociation } from '../api';

export default function ProductRecommendations() {
  const [selectedCustomer, setSelectedCustomer] = useState('C001');
  const [methodMode, setMethodMode] = useState('combined'); // 'combined', 'collaborative', 'association'
  const [topN, setTopN] = useState(3);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const customerList = ['C001', 'C002', 'C003', 'C004', 'C005'];

  useEffect(() => {
    async function fetchRecs() {
      try {
        setLoading(true);
        setError(null);
        let result;
        if (methodMode === 'collaborative') {
          result = await getRecommendationsCollaborative(selectedCustomer, topN);
        } else if (methodMode === 'association') {
          result = await getRecommendationsAssociation(selectedCustomer, topN);
        } else {
          result = await getRecommendations(selectedCustomer, topN);
        }
        setData(result);
      } catch (err) {
        setError(err.message || 'Failed to load recommendations.');
      } finally {
        setLoading(false);
      }
    }
    fetchRecs();
  }, [selectedCustomer, methodMode, topN]);

  const getMethodBadge = (method) => {
    switch (method) {
      case 'both':
        return { label: '⭐ Recommended by Both (Hybrid Synergy)', class: 'badge-purple' };
      case 'collaborative_filtering':
        return { label: '👥 Similar Customers Bought This', class: 'badge-blue' };
      case 'association_rules':
        return { label: '🛒 Frequently Bought Together', class: 'badge-amber' };
      default:
        return { label: '🤖 AI Recommended', class: 'badge-blue' };
    }
  };

  return (
    <div className="glass-card" style={{ marginBottom: '32px' }}>
      <div className="card-header" style={{ flexWrap: 'wrap', gap: '12px' }}>
        <div className="card-title">
          <span>🛍️</span>
          <div>
            <span style={{ fontSize: '1.05rem', fontWeight: 700 }}>AI Personalized Product Recommendations</span>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Collaborative Filtering (Cosine Similarity) & Market Basket Association Rules
            </div>
          </div>
        </div>

        {/* Controls: Customer Selector & Method Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Target Customer:</label>
            <select
              value={selectedCustomer}
              onChange={(e) => setSelectedCustomer(e.target.value)}
              className="custom-select"
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '4px 10px',
                fontSize: '0.82rem',
                fontWeight: 600,
              }}
            >
              {customerList.map((cid) => (
                <option key={cid} value={cid} style={{ background: '#0f172a' }}>
                  Customer {cid}
                </option>
              ))}
            </select>
          </div>

          <div className="tab-group" style={{ display: 'flex', gap: '4px', background: 'rgba(0,0,0,0.2)', padding: '3px', borderRadius: 'var(--radius-sm)' }}>
            <button
              onClick={() => setMethodMode('combined')}
              className={`pill-btn ${methodMode === 'combined' ? 'pill-active' : ''}`}
              style={{ fontSize: '0.74rem', padding: '4px 10px' }}
            >
              Combined Hybrid
            </button>
            <button
              onClick={() => setMethodMode('collaborative')}
              className={`pill-btn ${methodMode === 'collaborative' ? 'pill-active' : ''}`}
              style={{ fontSize: '0.74rem', padding: '4px 10px' }}
            >
              Collaborative Filtering
            </button>
            <button
              onClick={() => setMethodMode('association')}
              className={`pill-btn ${methodMode === 'association' ? 'pill-active' : ''}`}
              style={{ fontSize: '0.74rem', padding: '4px 10px' }}
            >
              Association Rules
            </button>
          </div>
        </div>
      </div>

      <div className="card-body">
        {loading ? (
          <div className="loading-spinner" style={{ padding: '24px' }}>
            <div className="spinner"></div>
            <span>Computing personalized recommendations...</span>
          </div>
        ) : error ? (
          <div className="msg-banner msg-error">
            <span>⚠️ {error}</span>
          </div>
        ) : (
          <div>
            {/* Customer Purchase History Banner */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '8px',
                padding: '10px 14px',
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '18px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Customer Purchase History:</span>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {(data?.purchased_products || []).map((item, idx) => (
                    <span
                      key={idx}
                      style={{
                        background: 'rgba(56, 189, 248, 0.12)',
                        border: '1px solid rgba(56, 189, 248, 0.3)',
                        color: '#38bdf8',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '0.76rem',
                        fontWeight: 600,
                      }}
                    >
                      ✓ {item} (Already Purchased)
                    </span>
                  ))}
                </div>
              </div>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>
                * Already-purchased items are strictly excluded from recommendations.
              </span>
            </div>

            {/* Recommendations Display */}
            {data?.recommendations && data.recommendations.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
                {data.recommendations.map((rec, idx) => {
                  const badgeInfo = getMethodBadge(rec.recommendation_method);
                  return (
                    <div
                      key={idx}
                      style={{
                        background: 'rgba(255, 255, 255, 0.03)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        padding: '16px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        gap: '12px',
                        position: 'relative',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span
                              style={{
                                width: '22px',
                                height: '22px',
                                borderRadius: '50%',
                                background: 'rgba(99, 102, 241, 0.25)',
                                color: '#a5b4fc',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '0.75rem',
                                fontWeight: 700,
                              }}
                            >
                              #{idx + 1}
                            </span>
                            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                              {rec.product_name}
                            </h4>
                          </div>
                          <span
                            className={badgeInfo.class}
                            style={{
                              display: 'inline-block',
                              marginTop: '8px',
                              fontSize: '0.72rem',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              fontWeight: 600,
                            }}
                          >
                            {badgeInfo.label}
                          </span>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Score</span>
                          <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#10b981' }}>
                            {rec.recommendation_score}
                          </div>
                        </div>
                      </div>

                      {/* Supporting Details */}
                      <div
                        style={{
                          fontSize: '0.76rem',
                          color: 'var(--text-dim)',
                          borderTop: '1px solid rgba(255, 255, 255, 0.06)',
                          paddingTop: '8px',
                        }}
                      >
                        {rec.supporting_peers && (
                          <div>
                            Similar Buyers: <strong>{rec.supporting_peers.join(', ')}</strong> ({rec.supporting_quantity} units)
                          </div>
                        )}
                        {rec.association_confidence && (
                          <div>
                            Rule Confidence: <strong>{(rec.association_confidence * 100).toFixed(0)}%</strong> (Lift: {rec.association_lift}x)
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div
                style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px dashed var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '24px',
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🔍</div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                  No New Unseen Recommendations Available
                </h4>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', maxWidth: '580px', margin: '0 auto' }}>
                  {data?.message || 'Current customer has purchased distinct products or similar peers have no additional unseen items.'}
                </p>
                <div style={{ marginTop: '12px', fontSize: '0.74rem', color: 'var(--text-dim)' }}>
                  💡 <em>Note: Collaborative filtering exclusively recommends unseen items from peers with positive cosine similarity, and association rules require multi-item transaction baskets.</em>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
