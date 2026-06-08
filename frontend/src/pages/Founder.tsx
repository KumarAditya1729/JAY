import { useEffect, useState } from 'react';
import { getFounderProfile, getFounderConsistency, getFounderDecisionStyle } from '../api';

export default function Founder() {
  const [profile, setProfile] = useState<any>(null);
  const [consistency, setConsistency] = useState<any>(null);
  const [decisionStyle, setDecisionStyle] = useState<any>(null);

  useEffect(() => {
    getFounderProfile().then(setProfile).catch(console.error);
    getFounderConsistency().then(setConsistency).catch(console.error);
    getFounderDecisionStyle().then(setDecisionStyle).catch(console.error);
  }, []);

  return (
    <div>
      <header className="page-header">
        <h1 className="page-title">Founder Profile</h1>
        <p className="page-subtitle">Style, Priorities, and Consistency for {profile?.name || 'JAY'}</p>
      </header>

      <div className="grid-cols-2">
        <div className="card">
           <h3 style={{ marginBottom: '1.5rem', color: 'var(--accent)' }}>Consistency Profile</h3>
           {consistency ? (
              <div>
                 <div className="metric-label">Consistency Score</div>
                 <div className="metric-value">{consistency.consistency_score.toFixed(2)}</div>
                 <div style={{ marginTop: '1rem' }}>
                    <div className="metric-label">Detected Gaps</div>
                    <ul style={{ paddingLeft: '1rem', marginTop: '0.5rem', color: 'var(--danger)' }}>
                       {consistency.identified_gaps.map((gap: string, i: number) => <li key={i}>{gap}</li>)}
                    </ul>
                 </div>
              </div>
           ) : <p>Loading...</p>}
        </div>

        <div className="card">
           <h3 style={{ marginBottom: '1.5rem', color: 'var(--accent)' }}>Decision Style</h3>
           {decisionStyle ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                 <div>
                    <div className="metric-label">Speed</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>{decisionStyle.speed}</div>
                 </div>
                 <div>
                    <div className="metric-label">Risk Appetite</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>{decisionStyle.risk_appetite}</div>
                 </div>
                 <div>
                    <div className="metric-label">Evidence Required</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>{decisionStyle.evidence_requirement}</div>
                 </div>
                 <div>
                    <div className="metric-label">Reversibility Pref</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>{decisionStyle.reversibility_preference}</div>
                 </div>
              </div>
           ) : <p>Loading...</p>}
        </div>
      </div>
    </div>
  );
}
