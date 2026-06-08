import { useEffect, useState } from 'react';
import { getTrustLedger, getTrustAnalytics } from '../api';

export default function Trust() {
  const [ledger, setLedger] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    getTrustLedger().then(setLedger).catch(console.error);
    getTrustAnalytics().then(setAnalytics).catch(console.error);
  }, []);

  return (
    <div>
      <header className="page-header">
        <h1 className="page-title">Trust Center</h1>
        <p className="page-subtitle">Trust Ledger & Confidence</p>
      </header>

      {analytics && (
        <div className="grid-cols-3" style={{ marginBottom: '2rem' }}>
          <div className="card">
            <div className="metric-label">Avg Confidence</div>
            <div className="metric-value">{(analytics.average_confidence * 100).toFixed(1)}%</div>
          </div>
          <div className="card">
            <div className="metric-label">Avg Risk</div>
            <div className="metric-value">{(analytics.average_risk * 100).toFixed(1)}%</div>
          </div>
          <div className="card">
            <div className="metric-label">Total Validations</div>
            <div className="metric-value">{analytics.total_validations}</div>
          </div>
        </div>
      )}

      <h3 style={{ marginBottom: '1rem' }}>Recent Trust Ledger Validations</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
         {ledger.map((entry) => (
           <div key={entry.id} className="card" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', alignItems: 'center' }}>
              <div>
                 <div style={{ fontWeight: 600 }}>{entry.entity_id}</div>
                 <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Type: {entry.entity_type}</div>
              </div>
              <div style={{ color: 'var(--success)' }}>
                 Confidence: {(entry.confidence_score * 100).toFixed(0)}%
              </div>
              <div style={{ color: 'var(--warning)' }}>
                 Risk: {(entry.risk_score * 100).toFixed(0)}%
              </div>
           </div>
         ))}
      </div>
    </div>
  );
}
