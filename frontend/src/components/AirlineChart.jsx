import React from 'react';
import Plot from 'react-plotly.js';

const PLOT_BASE = {
  autosize: true,
  paper_bgcolor: 'transparent',
  plot_bgcolor:  'transparent',
  font: { family: 'IBM Plex Mono, monospace', size: 11, color: '#8B95A8' },
  hoverlabel: {
    bgcolor: '#101927',
    bordercolor: 'rgba(216,154,52,0.4)',
    font: { family: 'IBM Plex Mono, monospace', size: 12, color: '#EEF0F5' },
  },
};

export default function AirlineChart({ airlines, loading }) {
  if (loading || !airlines || airlines.length === 0) {
    return (
      <div className="card empty">
        {loading ? <><span className="spinner" />Loading airline data…</> : 'No data — click ⚡ Seed Data to populate.'}
      </div>
    );
  }

  const PALETTE = ['#D89A34', '#2DDAB4', '#6C7FD8', '#FF6B6B'];

  return (
    <div className="card" style={{ padding: '10px 10px 0' }}>
      <Plot
        data={[{
          x: airlines.map((a) => a.airline),
          y: airlines.map((a) => a.avg_fare),
          type: 'bar',
          marker: {
            color: PALETTE.slice(0, airlines.length),
            opacity: 0.85,
            line: { color: 'rgba(255,255,255,0.1)', width: 1 },
          },
          hovertemplate: '<b>%{x}</b><br>Avg Fare: ₹%{y:,.0f}<extra></extra>',
        }]}
        layout={{
          ...PLOT_BASE,
          height: 300,
          margin: { l: 60, r: 16, t: 10, b: 44 },
          yaxis: {
            title: { text: '₹ Avg Fare', font: { size: 11, color: '#50596A' } },
            gridcolor: 'rgba(255,255,255,0.05)',
            tickfont: { color: '#8B95A8', size: 10 },
            tickformat: ',.0f',
          },
          xaxis: { tickfont: { color: '#8B95A8', size: 11 } },
          bargap: 0.3,
        }}
        useResizeHandler
        style={{ width: '100%' }}
        config={{ displayModeBar: false, responsive: true }}
      />
    </div>
  );
}
