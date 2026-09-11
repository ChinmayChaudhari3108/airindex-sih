import React from 'react';

function fmtMoney(n) {
  return '₹' + Math.round(n).toLocaleString('en-IN');
}

export default function RawFeedTable({ fares, loading }) {
  if (loading || !fares) {
    return (
      <div className="card empty">
        {loading ? <><span className="spinner" />Loading raw feed…</> : 'No data — click ⚡ Seed Data to populate.'}
      </div>
    );
  }

  if (fares.length === 0) {
    return <div className="card empty">No fare observations yet. Click ⚡ Seed Data above.</div>;
  }

  return (
    <div className="card feed-wrapper">
      <table className="feed">
        <thead>
          <tr>
            <th>Date</th>
            <th>Route</th>
            <th>Airline</th>
            <th>Lead Time</th>
            <th>Base Fare</th>
            <th>Tax (18%)</th>
            <th>Total</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {fares.map((f, i) => (
            <tr key={i}>
              <td style={{ color: 'var(--text-muted)' }}>{f.observed_date}</td>
              <td style={{ color: 'var(--amber)', fontWeight: 600 }}>{f.route_code}</td>
              <td>{f.airline}</td>
              <td style={{ color: 'var(--indigo, #6C7FD8)' }}>T+{f.lead_time_days}d</td>
              <td>{fmtMoney(f.base_fare)}</td>
              <td style={{ color: 'var(--text-muted)' }}>{fmtMoney(f.tax)}</td>
              <td style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{fmtMoney(f.total_fare)}</td>
              <td>
                {f.available
                  ? <span className="tag ok">✓ available</span>
                  : <span className="tag low">✗ sold out</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
