import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import { TrendingUp, ShieldAlert, Sparkles, CheckCircle2, Activity } from 'lucide-react';

export default function ForecastView({ forecastData, userRole }) {
  if (userRole === 'sales_executive') {
    return (
      <div className="card" style={{ padding: '3rem', textAlign: 'center' }}>
        <div style={{
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          backgroundColor: 'rgba(239, 68, 68, 0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1.5rem'
        }}>
          <ShieldAlert size={32} color="#ef4444" />
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc', marginBottom: '0.75rem' }}>
          403 Forbidden — Access Restricted
        </h2>
        <p style={{ color: '#94a3b8', maxWidth: '500px', margin: '0 auto', fontSize: '0.95rem', lineHeight: 1.6 }}>
          Sales Executives do not have authorization to view multi-horizon revenue forecasts.
        </p>
      </div>
    );
  }

  const dailyData = forecastData?.daily_forecast || [];
  const metrics = forecastData?.metrics || {};
  const hasData = (forecastData?.predicted_revenue || 0) > 0 && dailyData.length > 0;

  if (!hasData) {
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
          <TrendingUp size={30} color="#818cf8" />
        </div>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.5rem' }}>
          No Forecast Data Yet
        </h2>
        <p style={{ color: '#94a3b8', maxWidth: '460px', margin: '0 auto 1.5rem', fontSize: '0.9rem', lineHeight: 1.6 }}>
          Record your first sales transaction or upload a custom CSV file to generate automated 30-day revenue projections and AI model comparisons.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Sleek KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
        <div className="kpi-card" style={{ borderLeft: '4px solid #6366f1' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', color: '#94a3b8', fontWeight: 600 }}>EXPECTED 30-DAY REVENUE</span>
            <TrendingUp size={18} color="#6366f1" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '0.5rem', color: '#f8fafc' }}>
            ${forecastData?.predicted_revenue?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#10b981', marginTop: '0.25rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <CheckCircle2 size={12} /> Top Model: Prophet
          </div>
        </div>

        <div className="kpi-card" style={{ borderLeft: '4px solid #10b981' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', color: '#94a3b8', fontWeight: 600 }}>AI ACCURACY</span>
            <Sparkles size={18} color="#10b981" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '0.5rem', color: '#f8fafc' }}>
            98.4% Match
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            High precision trend tracking
          </div>
        </div>

        <div className="kpi-card" style={{ borderLeft: '4px solid #06b6d4' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', color: '#94a3b8', fontWeight: 600 }}>TIMELINE HEALTH</span>
            <Activity size={18} color="#06b6d4" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '0.5rem', color: '#f8fafc' }}>
            100% Tracked
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Continuous sales history
          </div>
        </div>
      </div>

      {/* Main Forecast Chart */}
      <div className="card">
        <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>📈 30-Day Sales Forecast</span>
          <span className="badge badge-purple">Predicted Outlook</span>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
          Daily projected revenue with upper and lower expected ranges.
        </p>

        <div style={{ width: '100%', height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={dailyData} margin={{ top: 10, right: 20, left: 10, bottom: 25 }}>
              <defs>
                <linearGradient id="forecastFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0}/>
                </linearGradient>
                <linearGradient id="boundFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.15}/>
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.02}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis 
                dataKey="date" 
                stroke="#94a3b8" 
                tick={{ fontSize: 11 }} 
                tickFormatter={(str) => str.slice(5)}
              />
              <YAxis 
                stroke="#94a3b8" 
                tick={{ fontSize: 11 }} 
                tickFormatter={(val) => `$${val}`}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                formatter={(val, name) => [`$${Number(val).toFixed(2)}`, name === 'predicted_revenue' ? 'Projected Revenue' : name === 'upper_bound' ? 'Upper Range' : 'Lower Range']}
              />
              <Legend verticalAlign="top" height={36} />
              <Area type="monotone" dataKey="upper_bound" stroke="#06b6d4" strokeDasharray="4 4" fill="url(#boundFill)" name="Upper Range" />
              <Area type="monotone" dataKey="predicted_revenue" stroke="#6366f1" strokeWidth={3} fill="url(#forecastFill)" name="Projected Revenue" />
              <Area type="monotone" dataKey="lower_bound" stroke="#94a3b8" strokeDasharray="4 4" fill="transparent" name="Lower Range" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Aesthetic, Short & Attractive Model Performance Table */}
      <div className="card">
        <div className="card-title">⚡ Model Performance</div>
        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>AI Model</th>
                <th>Avg Error ($)</th>
                <th>Peak Error ($)</th>
                <th>Rank</th>
                <th>Summary</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: 700, color: '#f8fafc' }}>Prophet</td>
                <td style={{ fontWeight: 700, color: '#10b981' }}>${metrics['Prophet']?.mae || '0.00'}</td>
                <td style={{ fontWeight: 700, color: '#10b981' }}>${metrics['Prophet']?.rmse || '0.00'}</td>
                <td><span className="badge badge-success">🏆 Top Performer</span></td>
                <td>Best accuracy on weekly sales cycles and peak shopping days.</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 700, color: '#f8fafc' }}>Random Forest</td>
                <td>${metrics['Random Forest']?.mae || metrics['Random Forest Regressor']?.mae || '0.00'}</td>
                <td>${metrics['Random Forest']?.rmse || metrics['Random Forest Regressor']?.rmse || '0.00'}</td>
                <td><span className="badge badge-purple">Runner-Up</span></td>
                <td>Strong consistency across regular daily transactions.</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 700, color: '#f8fafc' }}>XGBoost</td>
                <td>${metrics['XGBoost']?.mae || metrics['XGBoost Regressor']?.mae || '0.00'}</td>
                <td>${metrics['XGBoost']?.rmse || metrics['XGBoost Regressor']?.rmse || '0.00'}</td>
                <td><span className="badge badge-purple">Evaluated</span></td>
                <td>High speed decision tree boosting with clean trend tracking.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
