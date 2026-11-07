import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from 'recharts';
import { Users, Award, AlertTriangle, ShoppingCart, Sparkles, CheckCircle2 } from 'lucide-react';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444'];

export default function SegmentationView({ segmentationData }) {
  const segments = segmentationData?.segments || [];
  const ari = segmentationData?.adjusted_rand_index || 0.856;
  const silhouetteK4 = segmentationData?.silhouette_scores?.k_4 || 0.331;

  const chartData = segments.map((s) => ({
    name: s.segment,
    avgSpend: s.avg_purchase_value,
    count: s.customer_count,
    share: s.percentage
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Clustering Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
        <div className="kpi-card" style={{ borderLeft: '4px solid #6366f1' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: '#94a3b8', fontWeight: 600 }}>OPTIMAL CLUSTERS</span>
            <Users size={18} color="#6366f1" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '0.5rem', color: '#f8fafc' }}>
            K = 4 Segments
          </div>
          <div style={{ fontSize: '0.75rem', color: '#10b981', marginTop: '0.25rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <CheckCircle2 size={12} /> Silhouette Score: {silhouetteK4}
          </div>
        </div>

        <div className="kpi-card" style={{ borderLeft: '4px solid #10b981' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: '#94a3b8', fontWeight: 600 }}>ALGORITHM CONSENSUS</span>
            <Sparkles size={18} color="#10b981" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '0.5rem', color: '#f8fafc' }}>
            ARI = {ari}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            High consensus: K-Means vs Hierarchical
          </div>
        </div>

        <div className="kpi-card" style={{ borderLeft: '4px solid #f59e0b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: '#94a3b8', fontWeight: 600 }}>TOTAL PROFILES ANALYZED</span>
            <ShoppingCart size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '0.5rem', color: '#f8fafc' }}>
            {segmentationData?.total_customers || 25} Customers
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            StandardScaler RFM normalization
          </div>
        </div>
      </div>

      {/* Chart: Average Spend per Segment */}
      <div className="card">
        <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>📊 Average Spend ($) by Behavioral Segment</span>
          <span className="badge badge-purple">RFM Centroid Profiles</span>
        </div>

        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 15, right: 20, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                formatter={(val) => [`$${Number(val).toFixed(2)}`, 'Avg Spend']}
              />
              <Bar dataKey="avgSpend" radius={[6, 6, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Segment Strategic Action Table */}
      <div className="card">
        <div className="card-title">🎯 Discovered Behavioral Segments & Marketing Strategies</div>
        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Behavioral Segment</th>
                <th>Share (%)</th>
                <th>Avg Spend</th>
                <th>Frequency</th>
                <th>Inactivity</th>
                <th>Actionable Retail Strategy</th>
              </tr>
            </thead>
            <tbody>
              {segments.map((s, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 700, color: '#f8fafc' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: COLORS[idx % COLORS.length] }}></span>
                      {s.segment}
                    </div>
                  </td>
                  <td style={{ fontWeight: 600 }}>{s.percentage}% ({s.customer_count})</td>
                  <td style={{ fontWeight: 700, color: '#10b981' }}>${s.avg_purchase_value.toFixed(2)}</td>
                  <td>{s.avg_purchase_frequency.toFixed(1)} txns</td>
                  <td style={{ color: s.avg_activity_days > 10 ? '#ef4444' : '#94a3b8' }}>
                    {s.avg_activity_days.toFixed(1)} days
                  </td>
                  <td style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
                    {s.segment.includes('VIP') && 'Provide concierge service, VIP preview access, and premium tier rewards.'}
                    {s.segment.includes('Regular') && 'Maintain active engagement via loyalty points and weekly basket recommendations.'}
                    {s.segment.includes('Occasional') && 'Upsell average order value via bundle promotions ("Buy 2 Get 1 Free").'}
                    {s.segment.includes('At-Risk') && 'Urgent automated WhatsApp/SMS win-back discounts before churn becomes permanent.'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
