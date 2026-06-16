export default function StatsBar({ stats, impact, loading }) {
  if (loading) {
    return (
      <div className="stats-bar">
        {[0, 1, 2, 3].map(i => (
          <div key={i} className="stat-card skeleton">
            <div className="stat-value">—</div>
            <div className="stat-label">Loading...</div>
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    {
      value: stats?.facilities_total ?? '—',
      label: 'Facilities Monitored',
      icon: '🏭',
      color: 'default',
    },
    {
      value: stats?.anomalies_active ?? '—',
      label: 'Active Anomalies',
      icon: '⚠️',
      color: (stats?.anomalies_active || 0) > 0 ? 'red' : 'green',
    },
    {
      value: impact?.total_co2_kg_per_day != null
        ? `${Math.round(impact.total_co2_kg_per_day).toLocaleString()} kg`
        : '—',
      label: 'Daily CO₂ Waste',
      icon: '☁️',
      color: 'amber',
    },
    {
      value: impact?.total_cost_gbp_per_day != null
        ? `£${Math.round(impact.total_cost_gbp_per_day).toLocaleString()}`
        : '—',
      label: 'Daily £ Waste',
      icon: '💷',
      color: 'red',
    },
  ];

  return (
    <div className="stats-bar">
      {cards.map((card, i) => (
        <div key={i} className={`stat-card stat-card-${card.color}`}>
          <div className="stat-icon">{card.icon}</div>
          <div className="stat-value">{card.value}</div>
          <div className="stat-label">{card.label}</div>
        </div>
      ))}
    </div>
  );
}
