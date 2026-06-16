export default function AnomalyFeed({ anomalies, selectedId, onSelect }) {
  const severityColor = { high: '#e74c3c', medium: '#f39c12', low: '#27ae60' };

  return (
    <div className="anomaly-feed">
      {anomalies.map((a) => (
        <div
          key={a.id}
          className={`anomaly-card ${selectedId === a.id ? 'selected' : ''}`}
          onClick={() => onSelect(a)}
        >
          <div className="anomaly-header">
            <span
              className="severity-badge"
              style={{ background: severityColor[a.severity] || '#999' }}
            >
              {a.severity?.toUpperCase()}
            </span>
            <span className="facility-id">{a.facility_id}</span>
          </div>
          <h4 className="anomaly-title">{a.work_order?.title}</h4>
          <div className="anomaly-meta">
            <span className="cost-impact">
              £{a.work_order?.cost_impact_gbp_per_day?.toLocaleString()}/day
            </span>
            <span className="co2-impact">
              {a.work_order?.co2_impact_kg_per_day} kg CO₂/day
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
