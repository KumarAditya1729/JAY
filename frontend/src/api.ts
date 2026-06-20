const API_BASE = 'http://localhost:8002';

export async function fetchAPI(endpoint: string, options?: RequestInit) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer dev_key_only_change_in_prod',
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

// Ingestion
export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const url = `${API_BASE}/ingestion/upload`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer dev_key_only_change_in_prod'
    },
    body: formData
  });
  if (!res.ok) throw new Error(`Upload Error: ${res.status}`);
  return res.json();
};
export const getIngestionStatus = () => fetchAPI('/ingestion/status');
export const getPendingReviews = () => fetchAPI('/ingestion/pending-reviews');
export const getIngestionAccuracy = () => fetchAPI('/ingestion/accuracy');
export const getConnectorAudits = () => fetchAPI('/ingestion/connectors/audit');
export const approveReview = (id: string) => fetchAPI(`/ingestion/reviews/${id}/approve`, { method: 'POST' });
export const rejectReview = (id: string) => fetchAPI(`/ingestion/reviews/${id}/reject`, { method: 'POST' });
export const editReview = (id: string, data: any) => fetchAPI(`/ingestion/reviews/${id}/edit`, { 
  method: 'PUT',
  body: JSON.stringify(data)
});
export const syncGithub = (repoName: string) => fetchAPI('/ingestion/github/sync', {
  method: 'POST',
  body: JSON.stringify({ repo_name: repoName })
});

// Outcomes & Executions
export const getOutcomeMetrics = () => fetchAPI('/outcomes/metrics');
export const getPendingOutcomes = () => fetchAPI('/outcomes/pending');
export const logOutcome = (data: any) => fetchAPI('/outcomes/log', {
  method: 'POST',
  body: JSON.stringify(data)
});
export const getRecommendationAudit = (id: string) => fetchAPI(`/trust/recommendations/${id}/audit`);
export const getInferredOutcomes = () => fetchAPI('/outcomes/inferred');
export const confirmOutcome = (outcomeId: string, status: string) => fetchAPI('/outcomes/confirm', {
  method: 'POST',
  body: JSON.stringify({ outcome_id: outcomeId, status })
});

// Observation OS & Attention OS
export const getActiveSession = () => fetchAPI('/observation/session');
export const getAttentionAudit = () => fetchAPI('/attention/audit');
