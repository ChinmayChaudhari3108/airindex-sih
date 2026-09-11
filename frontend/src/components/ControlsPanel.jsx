import React from 'react';

export default function ControlsPanel({
  allRoutes, selectedRoutes, onToggleRoute,
  leadTimes, leadTime, onLeadTimeChange,
  aggregation, onAggregationChange,
  windowDays, onWindowDaysChange,
}) {
  return (
    <div className="controls-panel">
      {/* Route basket */}
      <div className="control-group">
        <label>Route Basket</label>
        <div className="chip-row">
          {allRoutes.map((code) => (
            <div
              key={code}
              id={`chip-route-${code}`}
              className={`chip ${selectedRoutes.includes(code) ? 'active' : ''}`}
              onClick={() => onToggleRoute(code)}
              title={selectedRoutes.includes(code) ? 'Click to deselect' : 'Click to select'}
            >
              {code}
            </div>
          ))}
        </div>
      </div>

      {/* Reference lead time */}
      <div className="control-group">
        <label>Reference Lead Time</label>
        <select
          id="select-lead-time"
          value={leadTime}
          onChange={(e) => onLeadTimeChange(Number(e.target.value))}
        >
          {leadTimes.map((lt) => (
            <option key={lt} value={lt}>T+{lt} days before departure</option>
          ))}
        </select>
      </div>

      {/* Aggregation */}
      <div className="control-group">
        <label>Aggregation</label>
        <div className="chip-row">
          {['daily', 'weekly', 'monthly'].map((agg) => (
            <div
              key={agg}
              id={`chip-agg-${agg}`}
              className={`chip ${aggregation === agg ? 'active' : ''}`}
              onClick={() => onAggregationChange(agg)}
            >
              {agg[0].toUpperCase() + agg.slice(1)}
            </div>
          ))}
        </div>
      </div>

      {/* Window slider */}
      <div className="control-group">
        <label>
          History Window — <span className="range-value">{windowDays} days</span>
        </label>
        <input
          id="range-window-days"
          type="range"
          min={10}
          max={45}
          step={1}
          value={windowDays}
          onChange={(e) => onWindowDaysChange(Number(e.target.value))}
        />
      </div>
    </div>
  );
}
