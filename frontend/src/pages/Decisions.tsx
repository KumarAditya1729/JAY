import { useEffect, useState } from 'react';
import { getDecisionsTimeline } from '../api';

export default function Decisions() {
  const [timeline, setTimeline] = useState<any[]>([]);

  useEffect(() => {
    getDecisionsTimeline()
      .then(setTimeline)
      .catch(console.error);
  }, []);

  return (
    <div>
      <header className="page-header">
        <h1 className="page-title">Decision Center</h1>
        <p className="page-subtitle">Timeline & Outcomes</p>
      </header>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {timeline.map((dec) => (
          <div key={dec.id} className="card" style={{ borderLeft: '4px solid var(--accent)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <h3 style={{ fontSize: '1.25rem' }}>{dec.statement}</h3>
              <span style={{ color: 'var(--text-secondary)' }}>{new Date(dec.decision_date).toLocaleDateString()}</span>
            </div>
            <div style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <span className="metric-label">Options Considered</span>
                <ul style={{ marginTop: '0.5rem', paddingLeft: '1rem' }}>
                  {dec.options_considered.map((opt: any, i: number) => <li key={i}>{opt.description || opt}</li>)}
                </ul>
              </div>
              <div>
                <span className="metric-label">Status</span>
                <div style={{ marginTop: '0.5rem', padding: '0.25rem 0.75rem', background: 'var(--bg-main)', display: 'inline-block', borderRadius: '1rem' }}>
                  {dec.outcome_status}
                </div>
              </div>
            </div>
          </div>
        ))}
        {timeline.length === 0 && <p>No decisions recorded yet.</p>}
      </div>
    </div>
  );
}
