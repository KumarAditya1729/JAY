import { useEffect, useState } from 'react';
import { getLeverageAnalysis } from '../api';

export default function Relationships() {
  const [leverage, setLeverage] = useState<any>(null);

  useEffect(() => {
    getLeverageAnalysis()
      .then(setLeverage)
      .catch(console.error);
  }, []);

  return (
    <div>
      <header className="page-header">
        <h1 className="page-title">Relationship Center</h1>
        <p className="page-subtitle">People, Health, and Leverage</p>
      </header>

      {leverage ? (
        <div className="grid-cols-2">
           <div className="card">
              <div className="metric-label">Founder Leverage Ratio</div>
              <div className="metric-value">{leverage.leverage_ratio.toFixed(2)}x</div>
           </div>
           <div className="card">
              <div className="metric-label">High Leverage Projects</div>
              <ul style={{ marginTop: '1rem', paddingLeft: '1rem' }}>
                 {leverage.high_leverage_projects.map((p: any, i: number) => <li key={i}>{p.id} (Impact: {p.impact})</li>)}
              </ul>
           </div>
           <div className="card" style={{ gridColumn: 'span 2' }}>
              <div className="metric-label">Relationship Health</div>
              <div style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                 {leverage.key_relationships.map((rel: any, i: number) => (
                    <div key={i} style={{ padding: '1rem', background: 'var(--bg-main)', borderRadius: '0.5rem', border: '1px solid var(--border)' }}>
                       <div style={{ fontWeight: 600 }}>{rel.person}</div>
                       <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Role: {rel.role}</div>
                       <div style={{ marginTop: '0.5rem', color: 'var(--success)' }}>Trust: {(rel.trust_level * 100).toFixed(0)}%</div>
                    </div>
                 ))}
              </div>
           </div>
        </div>
      ) : (
        <p>Loading leverage analysis...</p>
      )}
    </div>
  );
}
