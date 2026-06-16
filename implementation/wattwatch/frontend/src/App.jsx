import { useState, useEffect, useCallback } from 'react';
import { getFacilities, getAnomalies, getAnomaly, getStats, getImpact, assignAnomaly } from './api.js';
import StatsBar from './components/StatsBar.jsx';
import AnomalyFeed from './components/AnomalyFeed.jsx';
import WorkOrderPanel from './components/WorkOrderPanel.jsx';
import ImpactProjection from './components/ImpactProjection.jsx';

export default function App() {
  const [anomalies, setAnomalies] = useState([]);
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);
  const [stats, setStats] = useState(null);
  const [impact, setImpact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  const fetchCore = useCallback(async () => {
    try {
      const [anom, st, imp] = await Promise.all([
        getAnomalies(),
        getStats(),
        getImpact(),
      ]);
      const sorted = [...anom].sort(
        (a, b) =>
          (b.work_order?.cost_impact_gbp_per_day || 0) -
          (a.work_order?.cost_impact_gbp_per_day || 0)
      );
      setAnomalies(sorted);
      setStats(st);
      setImpact(imp);
      setLoading(false);
      // Auto-select first anomaly on initial load
      if (!selectedAnomaly && sorted.length > 0) {
        handleSelectAnomaly(sorted[0]);
      }
    } catch (err) {
      console.error('Failed to fetch core data:', err);
      setLoading(false);
    }
  }, []); // eslint-disable-line

  useEffect(() => {
    fetchCore();
    const interval = setInterval(fetchCore, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectAnomaly = async (anomaly) => {
    try {
      // Try to get full detail; fall back to list item if endpoint fails
      const detail = await getAnomaly(anomaly.id).catch(() => anomaly);
      setSelectedAnomaly(detail);
    } catch {
      setSelectedAnomaly(anomaly);
    }
  };

  const handleAssign = async (anomalyId, techName) => {
    try {
      await assignAnomaly(anomalyId, techName);
      showToast(`✅ Assigned to ${techName}`);
    } catch (err) {
      showToast(`❌ Failed to assign: ${err.message}`, 'error');
    }
  };

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <span className="logo">⚡ WattWatch</span>
          <span className="tagline">Energy waste detective for industrial facilities</span>
        </div>
        <div className="header-right">
          <span className="live-badge">● LIVE</span>
        </div>
      </header>

      {/* Toast notification */}
      {toast && (
        <div className={`toast toast-${toast.type}`}>{toast.message}</div>
      )}

      <main className="main-content">
        {/* Stats Bar */}
        <StatsBar stats={stats} impact={impact} loading={loading} />

        {/* Two-column layout */}
        <div className="dashboard-grid">
          {/* LEFT: Anomaly Feed */}
          <div className="feed-column">
            <div className="section-header">
              <h2>Active Anomalies</h2>
              {anomalies.length > 0 && (
                <span className="count-badge">{anomalies.length}</span>
              )}
            </div>
            {loading ? (
              <div className="loading-text">Loading anomalies...</div>
            ) : (
              <AnomalyFeed
                anomalies={anomalies}
                selectedId={selectedAnomaly?.id}
                onSelect={handleSelectAnomaly}
              />
            )}
          </div>

          {/* RIGHT: Work Order Panel */}
          <div className="detail-column">
            {selectedAnomaly ? (
              <WorkOrderPanel
                anomaly={selectedAnomaly}
                onAssign={handleAssign}
              />
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🔍</div>
                <p>Select an anomaly to view the work order</p>
              </div>
            )}
          </div>
        </div>

        {/* Bottom: Impact Projection */}
        {impact && <ImpactProjection impact={impact} />}
      </main>
    </div>
  );
}
