const API_BASE = import.meta.env.VITE_API_BASE_URL?.trim() || 'http://localhost:8000';

export interface RecommendRequest {
  crop: string;
  variety: string;
  grade: string;
  state: string;
  district: string;
  market: string;
  harvest_date: string;
  ph: number;
  soil_ec: number;
  phosphorus: number;
  potassium: number;
  urea: number;
  tsp: number;
  mop: number;
  moisture: number;
  temperature: number;
  storage_type: string;
  transit_hours: number;
}

export interface SpoilageRequest {
  crop: string;
  storage_type: string;
  transit_hours: number;
  state: string;
  district: string;
}

export interface TransitResponse {
  success: boolean;
  transit_hours: number;
  distance_km: number;
  source: string;
  route_summary: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      message = body?.detail || body?.message || message;
    } catch {
      // no-op
    }
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

export async function fetchRecommendation(data: RecommendRequest) {
  return request('/api/recommend', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function fetchSpoilage(data: SpoilageRequest) {
  return request('/api/spoilage', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function fetchCrops() {
  return request('/api/crops');
}

export async function fetchPrice(params: {
  crop: string;
  state: string;
  district: string;
  market: string;
  date: string;
  variety?: string;
  grade?: string;
}) {
  const query = new URLSearchParams({
    crop: params.crop,
    state: params.state,
    district: params.district,
    market: params.market,
    date: params.date,
    variety: params.variety || 'Local',
    grade: params.grade || 'Medium',
  });
  return request(`/api/price?${query.toString()}`);
}

export async function fetchTransit(origin: string, state: string, dest: string): Promise<TransitResponse> {
  const query = new URLSearchParams({ origin, state, dest });
  return request<TransitResponse>(`/api/transit?${query.toString()}`);
}
