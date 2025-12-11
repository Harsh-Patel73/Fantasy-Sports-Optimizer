const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function fetchHealth() {
  return fetchJSON(`${API_BASE}/health`);
}

export async function fetchLines(filters = {}) {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      params.append(key, value);
    }
  });

  const queryString = params.toString();
  const url = queryString ? `${API_BASE}/lines?${queryString}` : `${API_BASE}/lines`;

  return fetchJSON(url);
}

export async function fetchLineById(id) {
  return fetchJSON(`${API_BASE}/lines/${id}`);
}

export async function fetchDiscrepancies(filters = {}) {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      params.append(key, value);
    }
  });

  const queryString = params.toString();
  const url = queryString ? `${API_BASE}/discrepancies?${queryString}` : `${API_BASE}/discrepancies`;

  return fetchJSON(url);
}

export async function fetchTeams() {
  const result = await fetchJSON(`${API_BASE}/filters/teams`);
  return result.data;
}

export async function fetchPlayers() {
  const result = await fetchJSON(`${API_BASE}/filters/players`);
  return result.data;
}

export async function fetchStatTypes() {
  const result = await fetchJSON(`${API_BASE}/filters/stat-types`);
  return result.data;
}

export async function fetchBooks() {
  const result = await fetchJSON(`${API_BASE}/books`);
  return result.data;
}

// Line Comparison API
export async function fetchLineComparison(params = {}) {
  const urlParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      urlParams.append(key, value);
    }
  });
  return fetchJSON(`${API_BASE}/compare?${urlParams}`);
}

// Parlay Builder API
export async function fetchEVLines(params = {}) {
  const urlParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      urlParams.append(key, value);
    }
  });
  return fetchJSON(`${API_BASE}/parlay/ev-lines?${urlParams}`);
}

export async function validateParlay(body) {
  return fetchJSON(`${API_BASE}/parlay/validate`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function fetchParlayLines(params = {}) {
  const urlParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      urlParams.append(key, value);
    }
  });
  return fetchJSON(`${API_BASE}/parlay/lines?${urlParams}`);
}

export async function fetchParlayTypes() {
  return fetchJSON(`${API_BASE}/parlay/types`);
}

// Calculator API
export async function calculateDevig(body) {
  return fetchJSON(`${API_BASE}/calculators/devig`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function calculateParlayOdds(body) {
  return fetchJSON(`${API_BASE}/calculators/parlay-odds`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function fetchCalculatorParlayTypes() {
  return fetchJSON(`${API_BASE}/calculators/parlay-types`);
}
