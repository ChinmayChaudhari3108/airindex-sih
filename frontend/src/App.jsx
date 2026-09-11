import React, { useEffect, useState, useCallback } from 'react';
import { api } from './api';
import ControlsPanel from './components/ControlsPanel.jsx';
import IndexTrendChart from './components/IndexTrendChart.jsx';
import RouteHeatmap from './components/RouteHeatmap.jsx';
import AirlineChart from './components/AirlineChart.jsx';
import ElasticityChart from './components/ElasticityChart.jsx';
import RawFeedTable from './components/RawFeedTable.jsx';
import ForecastChart from './components/ForecastChart.jsx';

const ALL_ROUTES = ['DEL-BOM', 'DEL-BLR', 'BOM-BLR', 'DEL-CCU', 'BLR-HYD', 'MAA-DEL'];
const LEAD_TIMES = [1, 3, 7, 14, 21, 30, 45];

function formatTime(d) {
  if (!d) return null;
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export default function App() {
  const [routes, setRoutes] = useState(ALL_ROUTES);
  const [leadTime, setLeadTime] = useState(14);
  const [aggregation, setAggregation] = useState('daily');
  const [windowDays, setWindowDays] = useState(45);

  const [trend, setTrend] = useState(null);
  const [heatmap, setHeatmap] = useState(null);
  const [elasticity, setElasticity] = useState(null);
  const [airlines, setAirlines] = useState(null);
  const [fares, setFares] = useState(null);

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const refresh = useCallback(async () => {
    if (routes.length === 0) return;
    setLoading(true);
    try {
      const [t, h, e, a, f] = await Promise.all([
        api.trend(routes, leadTime, windowDays, aggregation),
        api.heatmap(routes, windowDays),
        api.elasticity(routes),
        api.airlines(routes, leadTime),
        api.fares(routes, leadTime, 20),
      ]);
      setTrend(t);
      setHeatmap(h);
      setElasticity(e);
      setAirlines(a);
      setFares(f);
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [routes, leadTime, windowDays, aggregation]);

  // Seed mock data then refresh charts
  const handleSeedData = async () => {
    setScraping(true);
    setError(null);
    try {
      await api.runScrape(null, null);
      await refresh();
    } catch (err) {
      setError('Scrape failed: ' + err.message);
    } finally {
      setScraping(false);
    }
  };

  useEffect(() => { refresh(); }, [refresh]);

  const toggleRoute = (code) => {
    setRoutes((prev) => {
      if (prev.includes(code)) {
        return prev.length > 1 ? prev.filter((r) => r !== code) : prev;
      }
      return [...prev, code];
    });
  };

  const latestIndex = trend?.points?.[trend.points.length - 1]?.index_value;
  const prevIndex   = trend?.points?.[trend.points.length - 2]?.index_value;
  const change      = latestIndex != null && prevIndex != null ? latestIndex - prevIndex : null;
  const hasData     = trend?.points?.length > 0;

  return (
    <div className="page">
      {/* ── Header ── */}
      <header className="board">
        <div className="board-top">
          <div className="brand">
            <span className="mark">CYBERCRYPT · SIH26056</span>
            <h1>AIRINDEX</h1>
            <p>Real-Time Airfare Price Intelligence Platform — India domestic routes, powered by FastAPI + SQLite/PostgreSQL.</p>
          </div>

          <div className="ticker">
            <div className="stat">
              <div className="label">Airfare Index</div>
              <div className="value">{latestIndex != null ? latestIndex.toFixed(1) : '—'}</div>
              {change != null && (
                <div className={`delta ${change >= 0 ? 'up' : 'down'}`}>
                  {change >= 0 ? '▲' : '▼'} {Math.abs(change).toFixed(2)} pts
                </div>
              )}
            </div>
            <div className="stat">
              <div className="label">Routes Tracked</div>
              <div className="value">{routes.length}<span style={{fontSize:'14px',opacity:.5}}>/{ALL_ROUTES.length}</span></div>
            </div>
            <div className="stat">
              <div className="label">Lead Time Ref</div>
              <div className="value">T+{leadTime}</div>
            </div>
          </div>
        </div>
      </header>

      <main>
        {/* ── Error Banner ── */}
        {error && (
          <div className="error-banner">
            <span style={{fontSize:'18px'}}>⚠</span>
            <span>
              <strong>API Error:</strong> {error}<br/>
              <span style={{fontSize:'12px',opacity:.7}}>Make sure the FastAPI backend is running: <code>uvicorn app.main:app --reload</code> in the <code>backend/</code> directory.</span>
            </span>
          </div>
        )}

        {/* ── Seed Data Row ── */}
        <div className="scrape-row">
          <div className="scrape-info">
            <strong>📡 Mock Data Engine</strong> — Click "Seed Data" to generate synthetic fare quotes across all routes and lead times. Run it once to populate the dashboard, then again to refresh with new mock prices.
          </div>
          <button
            className="btn btn-primary"
            onClick={handleSeedData}
            disabled={scraping || loading}
            id="btn-seed-data"
          >
            {scraping ? <><span className="spinner" style={{width:14,height:14}}/>Seeding…</> : '⚡ Seed Data'}
          </button>
          <button
            className="btn btn-ghost"
            onClick={refresh}
            disabled={loading}
            id="btn-refresh"
          >
            {loading ? <><span className="spinner" style={{width:14,height:14}}/>Loading…</> : '↻ Refresh'}
          </button>
          {lastUpdated && (
            <span className="last-updated">Updated {formatTime(lastUpdated)}</span>
          )}
        </div>

        {/* ── Controls ── */}
        <ControlsPanel
          allRoutes={ALL_ROUTES}
          selectedRoutes={routes}
          onToggleRoute={toggleRoute}
          leadTimes={LEAD_TIMES}
          leadTime={leadTime}
          onLeadTimeChange={setLeadTime}
          aggregation={aggregation}
          onAggregationChange={setAggregation}
          windowDays={windowDays}
          onWindowDaysChange={setWindowDays}
        />

        {/* ── Index Trend ── */}
        <section>
          <div className="section-header">
            <h2>Airfare Price Index</h2>
            <span className="section-badge">Base-100</span>
          </div>
          <IndexTrendChart trend={trend} loading={loading} />
        </section>

        {/* ── AI Price Index Forecast ── */}
        <section>
          <ForecastChart currentRoute={routes[0] || 'DEL-BOM'} leadTime={leadTime} />
        </section>

        {/* ── Heatmap + Airline ── */}
        <section className="grid-2">
          <div>
            <div className="section-header">
              <h2>Route × Lead-Time Heatmap</h2>
              <span className="section-badge">% change</span>
            </div>
            <RouteHeatmap heatmap={heatmap} routes={routes} leadTimes={LEAD_TIMES} loading={loading} />
          </div>
          <div>
            <div className="section-header">
              <h2>Airline Comparison</h2>
              <span className="section-badge">avg fare</span>
            </div>
            <AirlineChart airlines={airlines} loading={loading} />
          </div>
        </section>

        {/* ── Elasticity ── */}
        <section>
          <div className="section-header">
            <h2>Lead-Time Elasticity Curve</h2>
            <span className="section-badge">fare vs booking horizon</span>
          </div>
          <ElasticityChart elasticity={elasticity} loading={loading} />
        </section>

        {/* ── Raw Feed ── */}
        <section>
          <div className="section-header">
            <h2>Raw Fare Feed</h2>
            <span className="section-badge">latest observations</span>
          </div>
          <RawFeedTable fares={fares} loading={loading} />
        </section>
      </main>

      <footer>
        AIRINDEX · SIH26056 · Team CyberCrypt — FastAPI + SQLAlchemy + React + Plotly.js
      </footer>
    </div>
  );
}
