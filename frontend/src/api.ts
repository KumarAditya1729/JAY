const API_BASE = 'http://localhost:8001';

export async function fetchAPI(endpoint: string, options?: RequestInit) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {})
      }
    });
    if (!res.ok) {
      throw new Error(`API Error: ${res.status} ${res.statusText}`);
    }
    return res.json();
  } catch (err) {
    console.error(`Error fetching ${endpoint}:`, err);
    throw err;
  }
}

// Memory
export const searchMemory = (query: string, limit = 10) => fetchAPI(`/memory/search?q=${encodeURIComponent(query)}&limit=${limit}`);
export const getMemoryTimeline = (limit = 50) => fetchAPI(`/memory/timeline?limit=${limit}`);

// Briefing
export const getBriefing = (type: 'morning' | 'evening' | 'weekly' | 'monthly') => fetchAPI(`/briefing/${type}`);

// Intent
export const getIntent = () => fetchAPI('/intent');

// Trust
export const getTrustLedger = (limit = 50) => fetchAPI(`/trust/ledger?limit=${limit}`);
export const getTrustAnalytics = () => fetchAPI('/trust/analytics');

// Leverage
export const getLeverageAnalysis = () => fetchAPI('/leverage/analysis');

// Decisions
export const getDecisionsTimeline = () => fetchAPI('/decisions/timeline');
export const getDecisionAnalytics = () => fetchAPI('/decisions/analytics');

// Founder
export const getFounderProfile = () => fetchAPI('/founder/profile');
export const getFounderConsistency = () => fetchAPI('/founder/consistency');
export const getFounderDecisionStyle = () => fetchAPI('/founder/decision-style');

// Command Center
export const getCommandCenter = () => fetchAPI('/chief-of-staff/command-center');
