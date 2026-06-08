import { useEffect, useState } from 'react';
import { getCommandCenter } from '../api';

export default function CommandCenter() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCommandCenter()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch(console.error);
  }, []);

  if (loading) {
    return <div style={{ padding: '2rem' }}>Initializing Command Center...</div>;
  }

  if (!data) {
    return <div style={{ padding: '2rem' }}>Failed to load Command Center.</div>;
  }

  return (
    <div style={{ paddingBottom: '2rem' }}>
      <header className="page-header" style={{ marginBottom: '2rem', borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>
        <h1 className="page-title" style={{ fontSize: '2.5rem', color: 'var(--accent)' }}>MISSION BRIEFING</h1>
        <div style={{ display: 'flex', gap: '2rem', marginTop: '1rem' }}>
          <div>
            <span className="metric-label">ALIGNMENT</span>
            <span className="metric-value">{data.alignment_score}%</span>
          </div>
          <div>
            <span className="metric-label">LEVERAGE</span>
            <span className="metric-value">{data.leverage_score}%</span>
          </div>
        </div>
      </header>

      {/* HIGHEST LEVERAGE ACTION */}
      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '1rem', letterSpacing: '0.05em' }}>
          Highest Leverage Action
        </h2>
        <div style={{ background: 'var(--accent)', color: 'black', padding: '1.5rem', borderRadius: '0.5rem' }}>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
            {data.highest_leverage_action.statement}
          </h3>
          <p style={{ marginBottom: '1rem', opacity: 0.9 }}>{data.highest_leverage_action.reason}</p>
          
          <div style={{ display: 'flex', gap: '2rem', fontSize: '0.875rem' }}>
            <div>
              <strong>Impact:</strong> {data.highest_leverage_action.impact_score}/10
            </div>
            <div>
              <strong>Confidence:</strong> {data.highest_leverage_action.confidence_score}
            </div>
            <div>
              <strong>Leverage:</strong> {data.highest_leverage_action.estimated_leverage}
            </div>
          </div>
        </div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* TOP PRIORITIES */}
        <section className="card">
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Top 3 Priorities</h2>
          {data.top_priorities.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)' }}>No active priorities detected.</p>
          ) : (
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {data.top_priorities.map((p: any, i: number) => (
                <li key={i} style={{ padding: '0.75rem', background: 'var(--bg-main)', borderRadius: '0.25rem' }}>
                  <strong>{p.entity_title}</strong>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>{p.why_it_matters}</p>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* CRITICAL RISKS */}
        <section className="card">
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Critical Risks</h2>
          {data.critical_risks.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)' }}>No critical risks detected.</p>
          ) : (
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {data.critical_risks.map((r: any, i: number) => (
                <li key={i} style={{ padding: '0.75rem', background: '#3a1c1c', borderLeft: '3px solid #ff4444', borderRadius: '0.25rem' }}>
                  <strong>{r.entity_title}</strong> <span style={{ color: '#ffaa99', fontSize: '0.75rem', marginLeft: '0.5rem' }}>{r.risk_type}</span>
                  <p style={{ fontSize: '0.875rem', color: '#ffaaaa', marginTop: '0.25rem' }}>{r.reason}</p>
                  <p style={{ fontSize: '0.75rem', marginTop: '0.5rem', fontWeight: 'bold' }}>Action: {r.recommended_action}</p>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* OPEN COMMITMENTS */}
        <section className="card">
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Open Commitments</h2>
          {data.open_commitments.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)' }}>No active commitments found.</p>
          ) : (
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {data.open_commitments.map((c: any, i: number) => (
                <li key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', borderBottom: '1px solid var(--border)' }}>
                  <span>{c.commitment}</span>
                  <span style={{ color: c.days_overdue > 0 ? '#ff4444' : 'var(--text-secondary)' }}>
                    {c.days_overdue > 0 ? `${c.days_overdue}d overdue` : 'On track'}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* RELATIONSHIPS */}
        <section className="card">
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Relationships Requiring Attention</h2>
          {data.relationship_alerts.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)' }}>No relationships require immediate attention.</p>
          ) : (
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {data.relationship_alerts.map((r: any, i: number) => (
                <li key={i} style={{ padding: '0.75rem', background: 'var(--bg-main)', borderRadius: '0.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <strong>{r.person}</strong>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Score: {r.score}</span>
                  </div>
                  <p style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>Last Contact: {r.last_contact_days_ago} days ago</p>
                  <p style={{ fontSize: '0.875rem', marginTop: '0.25rem', color: 'var(--accent)' }}>{r.recommendation}</p>
                </li>
              ))}
            </ul>
          )}
        </section>
        
        {/* DECISIONS & PROJECTS */}
        <section className="card" style={{ gridColumn: '1 / -1' }}>
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Pending Decisions & Project Health</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            <div>
              <h3 style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Decisions Awaiting Review</h3>
              {data.decision_reviews.length === 0 ? (
                <p style={{ color: 'var(--text-secondary)' }}>No pending decisions.</p>
              ) : (
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {data.decision_reviews.map((d: any, i: number) => (
                    <li key={i} style={{ padding: '0.5rem', background: 'var(--bg-main)', borderRadius: '0.25rem', display: 'flex', justifyContent: 'space-between' }}>
                      <span>{d.decision}</span>
                      <span style={{ color: 'var(--accent)', fontSize: '0.75rem' }}>Review: {d.recommended_review_date}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <h3 style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Project Interventions</h3>
              {data.project_health.length === 0 ? (
                <p style={{ color: 'var(--text-secondary)' }}>No active projects tracked.</p>
              ) : (
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {data.project_health.map((p: any, i: number) => (
                    <li key={i} style={{ padding: '0.5rem', background: 'var(--bg-main)', borderRadius: '0.25rem', display: 'flex', justifyContent: 'space-between' }}>
                      <span>{p.project_id}</span>
                      <span style={{ color: p.status === 'Critical' ? '#ff4444' : p.status === 'Slowing' ? '#ffaa00' : 'var(--accent)' }}>{p.status}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
