import { useEffect, useState } from 'react';
import { getFounderProfile, getFounderConsistency, getBriefing } from '../api';

export default function Dashboard() {
  const [profile, setProfile] = useState<any>(null);
  const [consistency, setConsistency] = useState<any>(null);
  const [briefing, setBriefing] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [prof, cons, brief] = await Promise.all([
          getFounderProfile(),
          getFounderConsistency(),
          getBriefing('morning').catch(() => null)
        ]);
        setProfile(prof);
        setConsistency(cons);
        setBriefing(brief);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <header className="page-header">
        <h1 className="page-title">Home Dashboard</h1>
        <p className="page-subtitle">Mission Control Overview</p>
      </header>

      <div className="grid-cols-3">
        <div className="card">
          <div className="metric-label">Consistency Score</div>
          <div className="metric-value" style={{ color: 'var(--success)' }}>
            {consistency?.consistency_score?.toFixed(1) || '0.0'} / 100
          </div>
        </div>
        <div className="card">
          <div className="metric-label">Top Priority</div>
          <div className="metric-value" style={{ fontSize: '1.25rem', marginTop: '1rem' }}>
            {briefing?.top_priorities?.[0] || 'No current priorities'}
          </div>
        </div>
        <div className="card">
          <div className="metric-label">Founder Goals</div>
          <div className="metric-value">
            {profile?.goals?.length || 0} active
          </div>
        </div>
      </div>
      
      <div className="grid-cols-2" style={{ marginTop: '1.5rem' }}>
         <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Critical Risks</h3>
            {briefing?.critical_risks?.length ? (
               <ul style={{ paddingLeft: '1.2rem', color: 'var(--warning)' }}>
                  {briefing.critical_risks.map((risk: string, i: number) => (
                     <li key={i}>{risk}</li>
                  ))}
               </ul>
            ) : (
               <p style={{ color: 'var(--text-secondary)' }}>No critical risks detected.</p>
            )}
         </div>
         <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Recent Decisions</h3>
            {briefing?.recent_decisions?.length ? (
               <ul style={{ paddingLeft: '1.2rem' }}>
                  {briefing.recent_decisions.map((dec: string, i: number) => (
                     <li key={i}>{dec}</li>
                  ))}
               </ul>
            ) : (
               <p style={{ color: 'var(--text-secondary)' }}>No recent decisions.</p>
            )}
         </div>
      </div>
    </div>
  );
}
