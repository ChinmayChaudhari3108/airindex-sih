import React from 'react';

// Maps % change to a dark-theme-friendly color (red = expensive, teal = cheap)
function heatColor(pct) {
  const clamped = Math.max(-15, Math.min(15, pct));
  if (clamped >= 0) {
    // 0..+15 → teal → amber → red
    const t = clamped / 15;
    const r = Math.round(45  + (220 - 45)  * t);
    const g = Math.round(218 + (80  - 218) * t);
    const b = Math.round(180 + (60  - 180) * t);
    return `rgba(${r},${g},${b},0.75)`;
  }
  // negative → darker teal
  const t = -clamped / 15;
  return `rgba(${Math.round(45 * (1-t))},${Math.round(218 * (1-t) + 100 * t)},${Math.round(180 * (1-t) + 150 * t)},0.55)`;
}

function fmtMoney(n) {
  return '₹' + Math.round(n).toLocaleString('en-IN');
}

export default function RouteHeatmap({ heatmap, routes, leadTimes, loading }) {
  if (loading || !heatmap || !heatmap.cells) {
    return (
      <div className="card empty">
        {loading ? <><span className="spinner" />Loading heatmap…</> : 'No data — click ⚡ Seed Data to populate.'}
      </div>
    );
  }

  const byRoute = {};
  heatmap.cells.forEach((c) => {
    byRoute[c.route_code] = byRoute[c.route_code] || {};
    byRoute[c.route_code][c.lead_time_days] = c;
  });

  return (
    <div className="card heat-wrapper">
      <table className="heat">
        <thead>
          <tr>
            <th style={{ textAlign: 'left', paddingLeft: 12 }}>Route</th>
            {leadTimes.map((lt) => <th key={lt}>T+{lt}</th>)}
          </tr>
        </thead>
        <tbody>
          {routes.map((code) => (
            <tr key={code}>
              <td className="route-name">{code}</td>
              {leadTimes.map((lt) => {
                const cell = byRoute[code]?.[lt];
                if (!cell) return <td key={lt} className="empty-cell">—</td>;
                return (
                  <td
                    key={lt}
                    className="cell"
                    style={{ background: heatColor(cell.pct_change_vs_window_start) }}
                    title={`${code} T+${lt}: ${fmtMoney(cell.avg_fare)} | ${cell.pct_change_vs_window_start >= 0 ? '+' : ''}${cell.pct_change_vs_window_start}% vs window start`}
                  >
                    {fmtMoney(cell.avg_fare)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
