import React, { useState } from 'react';

export default function SalesChart({ data = [] }) {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
        No sales trend data available.
      </div>
    );
  }

  const width = 640;
  const height = 240;
  const padding = { top: 20, right: 30, bottom: 40, left: 55 };

  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const maxRevenue = Math.max(...data.map((d) => d.revenue), 100);
  // Round up to nearest 50 for clean scale
  const yMax = Math.ceil(maxRevenue / 50) * 50;

  const points = data.map((d, index) => {
    const x = padding.left + (index / (data.length - 1 || 1)) * chartWidth;
    const y = padding.top + chartHeight - (d.revenue / yMax) * chartHeight;
    return { ...d, x, y };
  });

  const linePath = points.reduce((acc, curr, idx) => {
    return `${acc} ${idx === 0 ? 'M' : 'L'} ${curr.x} ${curr.y}`;
  }, '');

  const areaPath = `${linePath} L ${points[points.length - 1].x} ${padding.top + chartHeight} L ${points[0].x} ${padding.top + chartHeight} Z`;

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: '100%', height: 'auto', display: 'block' }}
      >
        <defs>
          <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#6366f1" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#6366f1" stopOpacity="0.0" />
          </linearGradient>
          <linearGradient id="lineStroke" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="50%" stopColor="#818cf8" />
            <stop offset="100%" stopColor="#a855f7" />
          </linearGradient>
        </defs>

        {/* Y-Axis Gridlines & Ticks */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
          const val = Math.round(yMax * ratio);
          const y = padding.top + chartHeight - ratio * chartHeight;
          return (
            <g key={ratio}>
              <line
                x1={padding.left}
                y1={y}
                x2={width - padding.right}
                y2={y}
                stroke="rgba(255, 255, 255, 0.06)"
                strokeDasharray="4 4"
              />
              <text
                x={padding.left - 10}
                y={y + 4}
                fill="#94a3b8"
                fontSize="11"
                textAnchor="end"
                fontFamily="inherit"
              >
                ${val}
              </text>
            </g>
          );
        })}

        {/* Area Fill */}
        <path d={areaPath} fill="url(#salesGradient)" />

        {/* Line Stroke */}
        <path
          d={linePath}
          fill="none"
          stroke="url(#lineStroke)"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points & X-Axis Labels */}
        {points.map((pt, idx) => {
          const isHovered = hoveredPoint?.date === pt.date;
          return (
            <g key={idx}>
              {/* X-axis tick text */}
              <text
                x={pt.x}
                y={height - 12}
                fill="#94a3b8"
                fontSize="11"
                textAnchor="middle"
                fontFamily="inherit"
              >
                {pt.date.slice(5)}
              </text>

              {/* Point circle */}
              <circle
                cx={pt.x}
                cy={pt.y}
                r={isHovered ? 6 : 4}
                fill="#ffffff"
                stroke="#6366f1"
                strokeWidth={isHovered ? 3 : 2}
                style={{ cursor: 'pointer', transition: 'all 0.2s' }}
                onMouseEnter={() => setHoveredPoint(pt)}
                onMouseLeave={() => setHoveredPoint(null)}
              />
            </g>
          );
        })}
      </svg>

      {/* Dynamic Hover Tooltip Info */}
      <div
        style={{
          marginTop: '8px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '0.8rem',
          color: 'var(--text-muted)',
          padding: '0 8px',
        }}
      >
        {hoveredPoint ? (
          <span>
            📅 <strong>{hoveredPoint.date}</strong>: Revenue{' '}
            <strong style={{ color: '#38bdf8' }}>${hoveredPoint.revenue.toFixed(2)}</strong> ({hoveredPoint.orders_count} orders)
          </span>
        ) : (
          <span>Hover over data points to inspect daily revenue figures</span>
        )}
        <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Daily Aggregation</span>
      </div>
    </div>
  );
}
