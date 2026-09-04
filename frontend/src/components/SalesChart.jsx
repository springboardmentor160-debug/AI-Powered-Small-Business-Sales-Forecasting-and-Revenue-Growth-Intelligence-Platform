import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function SalesChart({ data }) {
  if (!data || data.length === 0) {
    return <div style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>No category data available</div>;
  }

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis 
            dataKey="category" 
            stroke="#94a3b8" 
            tick={{ fontSize: 12 }} 
            interval={0}
            angle={-15}
            textAnchor="end"
          />
          <YAxis 
            stroke="#94a3b8" 
            tick={{ fontSize: 12 }} 
            tickFormatter={(val) => `$${val}`}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
            formatter={(value) => [`$${value.toLocaleString()}`, 'Revenue']}
          />
          <Bar dataKey="total_revenue" fill="#6366f1" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
