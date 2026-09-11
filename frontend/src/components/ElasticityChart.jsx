import React from 'react';
import Plot from 'react-plotly.js';

const PLOT_BASE = {
  autosize: true,
  paper_bgcolor: 'transparent',
  plot_bgcolor:  'transparent',
  font: { family: 'IBM Plex Mono, monospace', size: 11, color: '#8B95A8' },
  hoverlabel: {
    bgcolor: '#101927',
    bordercolor: 'rgba(45,218,180,0.4)',
    font: { family: 'IBM Plex Mono, monospace', size: 12, color: '#EEF0F5' },
  },
};

export default function ElasticityChart({ elasticity, loading }) {
  if (loading || !elasticity || !elasticity.points || elasticity.points.length === 0) {
    return (
      <div className="card empty">
        {loading ? <><span className="spinner" />Loading elasticity curve…</> : 'No data — click ⚡ Seed Data to populate.'}
      </div>
    );
  }

  return (
    <div className="card" style={{ padding: '10px 10px 0' }}>
      <Plot
        data={[{
          x: elasticity.points.map((p) => `T+${p.lead_time_days}`),
          y: elasticity.points.map((p) => p.avg_fare),
          type: 'scatter',
          mode: 'lines+markers',
          fill: 'tozeroy',
          line: { color: '#2DDAB4', width: 2.5, shape: 'spline' },
          marker: { color: '#2DDAB4', size: 7, line: { color: 'rgba(45,218,180,0.3)', width: 4 } },
          fillcolor: 'rgba(45,218,180,0.06)',
          hovertemplate: '<b>%{x}</b><br>Avg Fare: ₹%{y:,.0f}<extra></extra>',
        }]}
        layout={{
          ...PLOT_BASE,
          height: 300,
          margin: { l: 64, r: 20, t: 10, b: 44 },
          yaxis: {
            title: { text: '₹ Avg Fare', font: { size: 11, color: '#50596A' } },
            gridcolor: 'rgba(255,255,255,0.05)',
            tickfont: { color: '#8B95A8', size: 10 },
            tickformat: ',.0f',
          },
          xaxis: {
            title: { text: 'Days before departure', font: { size: 11, color: '#50596A' } },
            tickfont: { color: '#8B95A8', size: 10 },
          },
        }}
        useResizeHandler
        style={{ width: '100%' }}
        config={{ displayModeBar: false, responsive: true }}
      />
    </div>
  );
}
