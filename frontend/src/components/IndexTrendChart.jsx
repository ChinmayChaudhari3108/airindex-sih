import React from 'react';
import Plot from 'react-plotly.js';

const PLOT_LAYOUT = {
  autosize: true,
  height: 340,
  margin: { l: 52, r: 20, t: 16, b: 44 },
  paper_bgcolor: 'transparent',
  plot_bgcolor:  'transparent',
  font: { family: 'IBM Plex Mono, monospace', size: 11, color: '#8B95A8' },
  yaxis: {
    title: { text: 'Base-100 Index', font: { size: 11, color: '#50596A' } },
    gridcolor: 'rgba(255,255,255,0.05)',
    zerolinecolor: 'rgba(255,255,255,0.08)',
    tickfont: { color: '#8B95A8', size: 10 },
  },
  xaxis: {
    gridcolor: 'rgba(255,255,255,0.03)',
    tickfont: { color: '#8B95A8', size: 10 },
  },
  hoverlabel: {
    bgcolor: '#101927',
    bordercolor: 'rgba(216,154,52,0.4)',
    font: { family: 'IBM Plex Mono, monospace', size: 12, color: '#EEF0F5' },
  },
};

export default function IndexTrendChart({ trend, loading }) {
  if (loading || !trend || !trend.points || trend.points.length === 0) {
    return (
      <div className="card empty">
        {loading ? <><span className="spinner" />Loading index trend…</> : 'No data — click ⚡ Seed Data to populate.'}
      </div>
    );
  }

  const x = trend.points.map((p) => p.date);
  const y = trend.points.map((p) => p.index_value);

  return (
    <div className="card" style={{ padding: '10px 10px 0' }}>
      <Plot
        data={[{
          x, y,
          type: 'scatter',
          mode: 'lines',
          fill: 'tozeroy',
          line: { color: '#D89A34', width: 2.5, shape: 'spline' },
          fillcolor: 'rgba(216,154,52,0.08)',
          hovertemplate: '<b>%{x}</b><br>Index: %{y:.1f}<extra></extra>',
        }]}
        layout={{
          ...PLOT_LAYOUT,
          shapes: [{
            type: 'line', y0: 100, y1: 100, x0: 0, x1: 1, xref: 'paper',
            line: { color: 'rgba(216,154,52,0.3)', width: 1, dash: 'dot' },
          }],
        }}
        useResizeHandler
        style={{ width: '100%' }}
        config={{ displayModeBar: false, responsive: true }}
      />
    </div>
  );
}
