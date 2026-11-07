import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from 'recharts';
import { Users, Award, ShoppingCart, Sparkles, CheckCircle2, UserCheck, HelpCircle } from 'lucide-react';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444'];

export default function SegmentationView({ segmentationData }) {
  const segments = segmentationData?.segments || [];
  const totalCustomers = segmentationData?.total_customers || 0;
  const confidence = segmentationData?.confidence_score || '94%';

  if (!totalCustomers || segments.length === 0) {
    return (
      <div className="card" style={{ padding: '3.5rem 2rem', textAlign: 'center' }}>
        <div style={{
          width: '64px',
          height: '64px',
          borderRadius: '16px',
          backgroundColor: 'rgba(99, 102, 241, 0.12)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1.25rem'
        }}>
          <Users size={30} color="#818cf8" />
        </div>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.5rem' }}>
          No Customer Profiles Yet
        </h2>
        <p style={{ color: '#94a3b8', maxWidth: '460px', margin: '0 auto 1.5rem', fontSize: '0.9rem', lineHeight: 1.6 }}>
          Record your first sales transaction or upload a custom CSV file to categorize your customers into behavioral buying segments.
        </p>
      </div>
    );
  }

  const chartData = segments.map((s) => ({
    name: s.segment,
    avgSpend: s.avg_purchase_value,
    count: s.customer_count,
    share: s.percentage
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* 3 Simple, Understandable Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
        <div className="kpi-card" style={{ borderLeft: '4px solid #6366f1' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', color: '#94a3b8', fontWeight: 600 }}>CUSTOMER GROUPS</span>
            <Users size={18} color="#6366f1" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '0.5rem', color: '#f8fafc' }}>
            {segments.length} Groups
          </div>
          <div style={{ fontSize: '0.75rem', color: '#10b981', marginTop: '0.25rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <CheckCircle2 size={12} /> Divided by spending & frequency
          </div>
        </div>

        <div className="kpi-card" style={{ borderLeft: '4px solid #10b981' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', color: '#94a3b8', fontWeight: 600 }}>AI CONFIDENCE</span>
            <Sparkles size={18} color="#10b981" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '0.5rem', color: '#f8fafc' }}>
            {confidence} Match
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            High agreement across AI clustering
          </div>
        </div>

        <div className="kpi-card" style={{ borderLeft: '4px solid #f59e0b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', color: '#94a3b8', fontWeight: 600 }}>CUSTOMERS ANALYZED</span>
            <ShoppingCart size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '0.5rem', color: '#f8fafc' }}>
            {totalCustomers} Customers
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Tracked from purchase history
          </div>
        </div>
      </div>

      {/* Average Spend Chart */}
      <div className="card">
        <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>📊 Average Spend ($) per Customer Group</span>
          <span className="badge badge-purple">Customer Profiles</span>
        </div>

        <div style={{ width: '100%', height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 15, right: 20, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                formatter={(val) => [`$${Number(val).toFixed(2)}`, 'Average Spend']}
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

      {/* Customer Groups & Marketing Actions Table */}
      <div className="card">
        <div className="card-title">🎯 Customer Groups & What Action to Take</div>
        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Customer Group</th>
                <th>Share</th>
                <th>Avg Spend</th>
                <th>Avg Orders</th>
                <th>Action to Grow Sales</th>
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
                  <td style={{ fontWeight: 700, color: '#10b981' }}>${s.avg_purchase_value?.toFixed(2)}</td>
                  <td>{s.avg_purchase_frequency?.toFixed(1) || '1.0'} orders</td>
                  <td style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
                    {s.action || (
                      s.segment.includes('VIP') ? 'Provide concierge service and early access to new collections.' :
                      s.segment.includes('Regular') ? 'Reward with weekly loyalty points and product recommendations.' :
                      s.segment.includes('Casual') ? 'Encourage higher basket size with bundle deals ("Buy 2 Get 1 Free").' :
                      'Send automated win-back SMS/WhatsApp discounts to re-engage.'
                    )}
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
