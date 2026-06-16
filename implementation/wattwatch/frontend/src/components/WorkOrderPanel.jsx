import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function WorkOrderPanel({ anomaly, onAssign }) {
  const [techName, setTechName] = useState('');
  const wo = anomaly?.work_order;
  const readings = anomaly?.readings || [];

  const urgencyColor = { high: '#e74c3c', medium: '#f39c12', low: '#27ae60' };

  return (
    <div className="work-order-panel">
      <div className="panel-header">
        <h2>Work Order</h2>
        <span
          className="urgency-badge"
          style={{ background: urgencyColor[wo?.urgency] || '#999' }}
        >
          {wo?.urgency?.toUpperCase()}
        </span>
      </div>

      <h3 className="wo-title">{wo?.title}</h3>

      <div className="wo-section">
        <label>Likely Cause</label>
        <p>{wo?.likely_cause}</p>
      </div>

      <div className="wo-section">
        <label>Recommended Action</label>
        <p>{wo?.action}</p>
      </div>

      <div className="wo-impacts">
        <div className="impact-card">
          <span className="impact-value">£{wo?.cost_impact_gbp_per_day?.toLocaleString()}</span>
          <span className="impact-label">Cost / day</span>
        </div>
        <div className="impact-card">
          <span className="impact-value">{wo?.co2_impact_kg_per_day} kg</span>
          <span className="impact-label">CO₂ / day</span>
        </div>
      </div>

      {readings.length > 0 && (
        <div className="chart-section">
          <label>Power Readings (kW)</label>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={readings.slice(-50)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(t) => new Date(t).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                fontSize={11}
              />
              <YAxis fontSize={11} />
              <Tooltip
                labelFormatter={(t) => new Date(t).toLocaleString()}
                formatter={(v) => [`${v} kW`, 'Power']}
              />
              <Line type="monotone" dataKey="power_kw" stroke="#667eea" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="assign-section">
        <input
          type="text"
          placeholder="Technician name..."
          value={techName}
          onChange={(e) => setTechName(e.target.value)}
          className="assign-input"
        />
        <button
          className="assign-btn"
          onClick={() => {
            onAssign(anomaly.id, techName || 'Available Tech');
            setTechName('');
          }}
        >
          Assign to Tech
        </button>
      </div>
    </div>
  );
}
