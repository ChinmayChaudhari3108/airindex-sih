const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

async function getJSON(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status} for ${path}`);
  return res.json();
}

function routeQuery(routes) {
  return routes.map(r => `route=${encodeURIComponent(r)}`).join('&');
}

export const api = {
  health: () => getJSON('/api/v1/health'),

  trend: (routes, leadTime, windowDays, aggregation) =>
    getJSON(`/api/v1/index/trend?${routeQuery(routes)}&lead_time=${leadTime}&window_days=${windowDays}&aggregation=${aggregation}`),

  heatmap: (routes, windowDays) =>
    getJSON(`/api/v1/index/heatmap?${routeQuery(routes)}&window_days=${windowDays}`),

  elasticity: (routes) =>
    getJSON(`/api/v1/index/elasticity?${routeQuery(routes)}`),

  airlines: (routes, leadTime) =>
    getJSON(`/api/v1/index/airlines?${routeQuery(routes)}&lead_time=${leadTime}`),

  fares: (routes, leadTime, limit = 15) =>
    getJSON(`/api/v1/fares?${routeQuery(routes)}&lead_time=${leadTime}&limit=${limit}`),

  forecast: (route, leadTime = 14, horizonDays = 14) =>
    getJSON(`/api/v1/index/forecast?route=${encodeURIComponent(route)}&lead_time=${leadTime}&horizon_days=${horizonDays}`),

  runScrape: (routes, leadTimes) =>
    fetch(`${BASE_URL}/api/v1/scrape/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ routes, lead_times: leadTimes }),
    }).then(r => r.json()),
};
