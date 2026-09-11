import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { api } from '../api';

const ROUTES = ['DEL-BOM', 'DEL-BLR', 'BOM-BLR', 'DEL-CCU', 'BLR-HYD', 'MAA-DEL'];
const HORIZONS = [7, 14, 21, 30];

const PLOT_BASE = {
  autosize: true,
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: { family: 'IBM Plex Mono, monospace', size: 11, color: '#8B95A8' },
  hoverlabel: {
    bgcolor: '#101927',
    bordercolor: 'rgba(45,218,180,0.4)',
    font: { family: 'IBM Plex Mono, monospace', size: 12, color: '#EEF0F5' },
  },
};

export default function ForecastChart({ currentRoute = 'DEL-BOM', leadTime = 14 }) {
  const [selectedRoute, setSelectedRoute] = useState(currentRoute);
  const [horizon, setHorizon] = useState(14);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadForecast() {
      setLoading(true);
      try {
        const data = await api.forecast(selectedRoute, leadTime, horizon);
        if (isMounted) {
          setForecastData(data);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadForecast();
    return () => { isMounted = false; };
  }, [selectedRoute, leadTime, horizon]);

  // Construct Plotly Traces
  const plotTraces = [];

  if (forecastData) {
    const histDates = forecastData.historical ? forecastData.historical.map(h => h.date.slice(5)) : [];
    const histVals = forecastData.historical ? forecastData.historical.map(h => h.index_value) : [];

    const fcDates = forecastData.forecast ? forecastData.forecast.map(f => f.date.slice(5)) : [];
    const fcVals = forecastData.forecast ? forecastData.forecast.map(f => f.forecast) : [];
    const fcUpper = forecastData.forecast ? forecastData.forecast.map(f => f.upper_ci) : [];
    const fcLower = forecastData.forecast ? forecastData.forecast.map(f => f.lower_ci) : [];

    // 1. 95% Confidence Interval Upper Bound
    plotTraces.push({
      x: fcDates,
      y: fcUpper,
      type: 'scatter',
      mode: 'lines',
      line: { width: 0 },
      showlegend: false,
      hoverinfo: 'skip'
    });

    // 2. 95% Confidence Interval Fill area to Lower Bound
    plotTraces.push({
      x: fcDates,
      y: fcLower,
      type: 'scatter',
      mode: 'lines',
      fill: 'tonexty',
      fillcolor: 'rgba(6, 182, 212, 0.12)',
      line: { width: 0 },
      name: '95% Confidence Interval',
      hoverinfo: 'skip'
    });

    // 3. Historical Line
    plotTraces.push({
      x: histDates,
      y: histVals,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Historical Index',
      line: { color: '#8B5CF6', width: 2.5 },
      marker: { color: '#8B5CF6', size: 4 },
      hovertemplate: '<b>%{x}</b><br>Historical Index: %{y:.1f}<extra></extra>'
    });

    // 4. Forecast Line
    plotTraces.push({
      x: fcDates,
      y: fcVals,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'AI Forecast Projection',
      line: { color: '#06B6D4', width: 2.5, dash: 'dash' },
      marker: { color: '#06B6D4', size: 5 },
      hovertemplate: '<b>%{x} (Projected)</b><br>Forecast Index: %{y:.1f}<extra></extra>'
    });
  }

  return (
    <div className="card" style={{ padding: '16px', position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '14px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="live-dot" />
            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#EEF0F5' }}>
              🤖 AI Price Index Forecasting (Holt Exponential Engine)
            </h3>
          </div>
          <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#8B95A8' }}>
            Predictive 14-day airfare price index trajectory with 95% confidence bounds & buy/wait guidance.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <select
            className="select-input"
            value={selectedRoute}
            onChange={(e) => setSelectedRoute(e.target.value)}
            style={{ padding: '6px 12px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', color: '#EEF0F5', border: '1px solid rgba(255,255,255,0.12)' }}
          >
            {ROUTES.map((r) => (
              <option key={r} value={r} style={{ background: '#101927' }}>
                Route: {r}
              </option>
            ))}
          </select>

          <select
            className="select-input"
            value={horizon}
            onChange={(e) => setHorizon(Number(e.target.value))}
            style={{ padding: '6px 12px', borderRadius: '6px', background: 'rgba(255,255,255,0.06)', color: '#EEF0F5', border: '1px solid rgba(255,255,255,0.12)' }}
          >
            {HORIZONS.map((h) => (
              <option key={h} value={h} style={{ background: '#101927' }}>
                Horizon: +{h} Days
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Recommendation Banner */}
      {forecastData && (
        <div
          style={{
            margin: '0 0 16px 0',
            padding: '12px 16px',
            borderRadius: '8px',
            background:
              forecastData.badge_type === 'surge'
                ? 'rgba(239, 68, 68, 0.12)'
                : forecastData.badge_type === 'drop'
                ? 'rgba(34, 197, 94, 0.12)'
                : 'rgba(59, 130, 246, 0.12)',
            border:
              forecastData.badge_type === 'surge'
                ? '1px solid rgba(239, 68, 68, 0.3)'
                : forecastData.badge_type === 'drop'
                ? '1px solid rgba(34, 197, 94, 0.3)'
                : '1px solid rgba(59, 130, 246, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 700,
                letterSpacing: '0.5px',
                padding: '5px 10px',
                borderRadius: '4px',
                color: '#fff',
                background:
                  forecastData.badge_type === 'surge'
                    ? '#EF4444'
                    : forecastData.badge_type === 'drop'
                    ? '#22C55E'
                    : '#3B82F6'
              }}
            >
              {forecastData.recommendation}
            </span>
            <span style={{ fontSize: '13px', color: '#EEF0F5' }}>
              {forecastData.recommendation_reason}
            </span>
          </div>

          <div style={{ display: 'flex', gap: '16px', fontSize: '12px', fontFamily: 'IBM Plex Mono, monospace' }}>
            <div>
              <span style={{ opacity: 0.6 }}>Current Index: </span>
              <strong>{forecastData.last_actual_index}</strong>
            </div>
            <div>
              <span style={{ opacity: 0.6 }}>Projected ({horizon}d): </span>
              <strong style={{ color: forecastData.expected_change_pct >= 0 ? '#EF4444' : '#22C55E' }}>
                {forecastData.projected_index_h14} ({forecastData.expected_change_pct >= 0 ? '+' : ''}{forecastData.expected_change_pct}%)
              </strong>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div style={{ height: '280px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8B95A8' }}>
          <span className="spinner" style={{ marginRight: '8px' }} /> Calculating Holt Exponential AI Forecast...
        </div>
      )}

      {!loading && forecastData && (
        <Plot
          data={plotTraces}
          layout={{
            ...PLOT_BASE,
            height: 300,
            margin: { l: 52, r: 20, t: 10, b: 44 },
            yaxis: {
              title: { text: 'Airfare Index', font: { size: 11, color: '#50596A' } },
              gridcolor: 'rgba(255,255,255,0.05)',
              zerolinecolor: 'rgba(255,255,255,0.08)',
              tickfont: { color: '#8B95A8', size: 10 },
            },
            xaxis: {
              gridcolor: 'rgba(255,255,255,0.03)',
              tickfont: { color: '#8B95A8', size: 10 },
            },
            legend: {
              orientation: 'h',
              x: 0,
              y: 1.12,
              font: { color: '#8B95A8', size: 11 }
            }
          }}
          useResizeHandler
          style={{ width: '100%', height: '100%' }}
          config={{ responsive: true, displayModeBar: false }}
        />
      )}
    </div>
  );
}
