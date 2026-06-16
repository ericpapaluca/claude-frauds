export default function ImpactProjection({ impact }) {
  if (!impact) return null;

  const proj = impact.projection_100_facilities;

  return (
    <div className="impact-projection">
      <div className="impact-proj-inner">
        <div className="impact-proj-icon">🌍</div>
        <div className="impact-proj-text">
          <div className="impact-proj-headline">
            If 100 facilities ran WattWatch for a year
          </div>
          <div className="impact-proj-stats">
            {proj?.co2_tons_per_year != null && (
              <span className="proj-stat">
                <strong>{Math.round(proj.co2_tons_per_year).toLocaleString()} tonnes</strong> CO₂ saved
              </span>
            )}
            {proj?.cost_gbp_per_year != null && (
              <span className="proj-stat">
                <strong>£{Math.round(proj.cost_gbp_per_year / 1000).toLocaleString()}k</strong> energy costs recovered
              </span>
            )}
          </div>
        </div>
        <div className="impact-proj-cta">
          <div className="pitch-tag">"Waze for industrial energy waste"</div>
        </div>
      </div>
    </div>
  );
}
