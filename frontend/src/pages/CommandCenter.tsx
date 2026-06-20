import { useState, useEffect } from 'react';
import { getCommandCenter, getOutcomeMetrics, getPendingOutcomes, logOutcome, getRecommendationAudit, getInferredOutcomes, confirmOutcome, getActiveSession, getAttentionAudit } from '../api';
import AttentionAuditWidget from '../components/AttentionAuditWidget';

export default function CommandCenter() {
  const [data, setData] = useState<any>(null);
  const [_outcomeMetrics, setOutcomeMetrics] = useState<any>(null);
  const [pendingOutcomes, setPendingOutcomes] = useState<any[]>([]);
  const [inferredOutcomes, setInferredOutcomes] = useState<any[]>([]);
  const [activeSessionData, setActiveSessionData] = useState<any>(null);
  const [attentionAudit, setAttentionAudit] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // Outcome Modal State
  const [showOutcomeModal, setShowOutcomeModal] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState<any>(null);
  const [outcomeForm, setOutcomeForm] = useState({
    status: 'SUCCESS',
    outcome: '',
    domain: 'Execution',
    failure_reason: 'None',
    impact_score: 5,
    hours_saved: 0,
    hours_invested: 0
  });

  // Audit Modal State
  const [showAuditModal, setShowAuditModal] = useState(false);
  const [auditData, setAuditData] = useState<any>(null);

  const fetchData = async () => {
    try {
      const [ccRes, metricsRes, pendingRes, inferredRes, sessionRes, attentionRes] = await Promise.all([
        getCommandCenter(),
        getOutcomeMetrics(),
        getPendingOutcomes(),
        getInferredOutcomes(),
        getActiveSession(),
        getAttentionAudit()
      ]);
      setData(ccRes);
      setOutcomeMetrics(metricsRes);
      setPendingOutcomes(pendingRes);
      setInferredOutcomes(inferredRes);
      setActiveSessionData(sessionRes);
      setAttentionAudit(attentionRes);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openOutcomeModal = (exec: any) => {
    setSelectedExecution(exec);
    setShowOutcomeModal(true);
    setOutcomeForm({
      status: exec.status === 'EXECUTED' ? 'SUCCESS' : 'FAILURE',
      outcome: exec.stdout || '',
      domain: 'Execution',
      failure_reason: 'None',
      impact_score: 5,
      hours_saved: 0,
      hours_invested: 0
    });
  };

  const handleLogOutcome = async () => {
    if (!selectedExecution) return;
    try {
      await logOutcome({
        execution_id: selectedExecution.id,
        recommendation_id: data?.highest_leverage_action?.recommendation_id || null,
        recommendation_text: selectedExecution.command,
        status: outcomeForm.status,
        outcome: outcomeForm.outcome,
        domain: outcomeForm.domain,
        failure_reason: outcomeForm.status !== 'SUCCESS' ? outcomeForm.failure_reason : 'None',
        impact_score: outcomeForm.impact_score,
        hours_saved: outcomeForm.hours_saved,
        hours_invested: outcomeForm.hours_invested
      });
      setShowOutcomeModal(false);
      await fetchData();
    } catch (e) {
      console.error(e);
      alert("Failed to log outcome");
    }
  };

  const handleShowAudit = async () => {
    if (!data?.highest_leverage_action?.recommendation_id) {
      alert("No audit trail available for this recommendation.");
      return;
    }
    try {
      const audit = await getRecommendationAudit(data.highest_leverage_action.recommendation_id);
      setAuditData(audit);
      setShowAuditModal(true);
    } catch (e) {
      console.error(e);
      alert("Failed to fetch audit trace.");
    }
  };

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
            <span className="metric-label">SYSTEM ALIGNMENT</span>
            <span className="metric-value">{data.alignment_score}%</span>
          </div>
        </div>
      </header>

      {/* THE ULTIMATE METRIC (Phase Y) */}
      {data.system_accuracy && data.system_accuracy.founder_vs_jay && (
        <section className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, #020617 0%, #0f172a 100%)', border: '1px solid #1e293b', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '4px', background: 'linear-gradient(90deg, #3b82f6, #a855f7)' }}></div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #1e293b', paddingBottom: '1rem', marginTop: '0.5rem' }}>
            <h2 style={{ fontSize: '1.5rem', textTransform: 'uppercase', color: '#f8fafc', letterSpacing: '0.15em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 20h.01"></path><path d="M7 20v-4"></path><path d="M12 20v-8"></path><path d="M17 20V8"></path><path d="M22 4v16"></path></svg>
              The Ultimate Metric: JAY vs. Kumar
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#a855f7', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 'bold', background: 'rgba(168, 85, 247, 0.1)', padding: '0.25rem 0.75rem', borderRadius: '1rem', border: '1px solid rgba(168, 85, 247, 0.2)' }}>
              Founder Value Alpha
            </div>
          </div>

          <div style={{ display: 'flex', gap: '2rem', marginBottom: '2rem' }}>
            {/* Win Rate */}
            <div style={{ flex: 1, background: '#09090b', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #27272a', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>JAY Win Rate (When Disagreed)</div>
              <div style={{ fontSize: '3rem', fontWeight: 'bold', color: data.system_accuracy.founder_vs_jay.jay_win_rate >= 0.5 ? '#10b981' : '#ef4444' }}>
                {Math.round(data.system_accuracy.founder_vs_jay.jay_win_rate * 100)}%
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>
                {data.system_accuracy.founder_vs_jay.jay_wins} JAY Wins / {data.system_accuracy.founder_vs_jay.founder_wins} Founder Wins / {data.system_accuracy.founder_vs_jay.ties} Ties
              </div>
            </div>

            {/* Log */}
            <div style={{ flex: 2, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Recent Disagreements</h3>
              {data.system_accuracy.founder_vs_jay.log.slice(0, 3).map((log: any, idx: number) => {
                let statusColor = '#64748b';
                if (log.who_was_right === 'JAY') statusColor = '#10b981';
                if (log.who_was_right === 'FOUNDER') statusColor = '#3b82f6';
                if (log.who_was_right === 'TIE') statusColor = '#f59e0b';
                
                return (
                  <div key={idx} style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr auto', gap: '1rem', background: '#0f172a', padding: '0.75rem 1rem', borderRadius: '0.25rem', alignItems: 'center', border: `1px solid ${statusColor}40` }}>
                    <div style={{ fontSize: '0.875rem', color: '#e2e8f0', fontWeight: 'bold' }}>{log.scenario}</div>
                    <div>
                      <div style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase' }}>JAY Rec.</div>
                      <div style={{ fontSize: '0.75rem', color: '#a855f7' }}>{log.jay_recommendation}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase' }}>Founder</div>
                      <div style={{ fontSize: '0.75rem', color: '#38bdf8' }}>{log.founder_decision}</div>
                    </div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 'bold', color: statusColor, padding: '0.25rem 0.5rem', background: `${statusColor}20`, borderRadius: '0.25rem', textTransform: 'uppercase' }}>
                      {log.who_was_right} WON
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      )}

      {/* SYSTEM ACCURACY & TRUST MARKETS (Phase Y) */}
      {data.system_accuracy && (
        <section className="card" style={{ marginBottom: '2rem', background: '#09090b', border: '1px solid #27272a', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '4px', background: 'linear-gradient(90deg, #ef4444, #eab308, #10b981)' }}></div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #27272a', paddingBottom: '1rem', marginTop: '0.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', textTransform: 'uppercase', color: '#f8fafc', letterSpacing: '0.15em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#eab308" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
              Trust Markets (System Accuracy & Calibration)
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#eab308', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 'bold', background: 'rgba(234, 179, 8, 0.1)', padding: '0.25rem 0.75rem', borderRadius: '1rem', border: '1px solid rgba(234, 179, 8, 0.2)' }}>
              Empirical Validation Active
            </div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
            {data.system_accuracy.aggregate_accuracy.map((agg: any, idx: number) => {
              let trustColor = '#ef4444'; // Red LOW
              if (agg.trust_tier === 'MEDIUM') trustColor = '#f59e0b'; // Amber
              if (agg.trust_tier === 'HIGH') trustColor = '#10b981'; // Green
              
              return (
                <div key={idx} style={{ background: '#18181b', padding: '1.25rem', borderRadius: '0.5rem', border: `1px solid ${trustColor}80`, position: 'relative' }}>
                  {agg.is_drifting && (
                    <div style={{ position: 'absolute', top: '-10px', right: '1rem', background: '#ef4444', color: 'white', fontSize: '0.65rem', fontWeight: 'bold', padding: '0.125rem 0.5rem', borderRadius: '1rem', textTransform: 'uppercase', letterSpacing: '0.05em', animation: 'pulse 2s infinite' }}>
                      Drift Detected
                    </div>
                  )}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.75rem', color: '#e4e4e7', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 'bold' }}>{agg.engine}</div>
                    <div style={{ fontSize: '0.65rem', color: trustColor, textTransform: 'uppercase', fontWeight: 'bold', padding: '0.125rem 0.5rem', background: `${trustColor}20`, borderRadius: '0.25rem' }}>{agg.trust_tier} TRUST</div>
                  </div>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <div style={{ fontSize: '0.65rem', color: '#71717a', textTransform: 'uppercase' }}>Accuracy</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white' }}>{Math.round(agg.accuracy * 100)}%</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.65rem', color: '#71717a', textTransform: 'uppercase' }}>Calibration</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white' }}>{Math.round(agg.calibration * 100)}%</div>
                    </div>
                  </div>
                  <div style={{ marginTop: '1rem', paddingTop: '0.5rem', borderTop: '1px solid #27272a', fontSize: '0.75rem', color: '#a1a1aa' }}>
                    Trust Score: <strong style={{ color: trustColor }}>{Math.round(agg.trust_score * 100)}</strong> ({agg.evaluations_count} evals)
                  </div>
                </div>
              );
            })}
          </div>

          <div>
            <h3 style={{ fontSize: '0.75rem', color: '#a1a1aa', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '1rem', borderBottom: '1px solid #27272a', paddingBottom: '0.5rem' }}>Recent Ground Truth Audits</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {data.system_accuracy.recent_validations.map((val: any, idx: number) => (
                <div key={idx} style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 2fr auto auto', gap: '1rem', background: '#18181b', padding: '0.75rem 1rem', borderRadius: '0.25rem', alignItems: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: '#d4d4d8', fontWeight: 'bold' }}>{val.engine}</div>
                  <div>
                    <div style={{ fontSize: '0.65rem', color: '#71717a', textTransform: 'uppercase' }}>Predicted</div>
                    <div style={{ fontSize: '0.875rem', color: '#a1a1aa', fontStyle: 'italic' }}>"{val.prediction}"</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.65rem', color: '#71717a', textTransform: 'uppercase' }}>Reality</div>
                    <div style={{ fontSize: '0.875rem', color: '#e4e4e7' }}>{val.outcome}</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '0.65rem', color: '#71717a', textTransform: 'uppercase' }}>Conf.</div>
                    <div style={{ fontSize: '0.875rem', color: '#94a3b8' }}>{Math.round(val.confidence_score * 100)}%</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.65rem', color: '#71717a', textTransform: 'uppercase' }}>Accuracy</div>
                    <div style={{ fontSize: '1rem', fontWeight: 'bold', color: val.accuracy_score >= 0.8 ? '#10b981' : val.accuracy_score >= 0.5 ? '#f59e0b' : '#ef4444' }}>
                      {Math.round(val.accuracy_score * 100)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* STRATEGIC SIMULATION ENGINE (Phase 21) */}
      {data.strategic_simulations && data.strategic_simulations.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', background: '#000000', border: '1px solid #334155', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '2px', background: 'linear-gradient(90deg, transparent, #38bdf8, transparent)' }}></div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #1e293b', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.25rem', textTransform: 'uppercase', color: '#f8fafc', letterSpacing: '0.15em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
              JAY OMEGA: Strategic Simulation
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', background: '#0f172a', padding: '0.25rem 0.5rem', borderRadius: '0.25rem', border: '1px solid #1e293b' }}>Monte Carlo Matrix Active</div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {data.strategic_simulations.map((sim: any, idx: number) => (
              <div key={idx}>
                <h3 style={{ fontSize: '1rem', color: '#cbd5e1', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.65rem', color: '#0ea5e9', textTransform: 'uppercase', fontWeight: 'bold', border: '1px solid #0ea5e9', padding: '0.125rem 0.375rem', borderRadius: '0.125rem' }}>Scenario</span>
                  {sim.scenario}
                </h3>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                  {/* Best Case */}
                  <div style={{ background: 'linear-gradient(to bottom, #064e3b, #022c22)', borderRadius: '0.5rem', padding: '1.5rem', border: '1px solid #059669' }}>
                    <h4 style={{ fontSize: '0.875rem', color: '#34d399', textTransform: 'uppercase', fontWeight: 'bold', marginBottom: '1rem', borderBottom: '1px solid #047857', paddingBottom: '0.5rem' }}>Best Case</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem', color: '#a7f3d0' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Financial</span><span style={{ fontWeight: 'bold', color: 'white' }}>{sim.best_case.financial}</span></div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Velocity</span><span style={{ fontWeight: 'bold', color: 'white' }}>{sim.best_case.velocity}</span></div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Risk</span><span style={{ fontWeight: 'bold', color: 'white' }}>{sim.best_case.risk}</span></div>
                      <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#6ee7b7', fontStyle: 'italic', borderTop: '1px solid #065f46', paddingTop: '0.5rem' }}>"{sim.best_case.summary}"</div>
                    </div>
                  </div>
                  
                  {/* Expected Case */}
                  <div style={{ background: 'linear-gradient(to bottom, #1e3a8a, #172554)', borderRadius: '0.5rem', padding: '1.5rem', border: '1px solid #2563eb' }}>
                    <h4 style={{ fontSize: '0.875rem', color: '#60a5fa', textTransform: 'uppercase', fontWeight: 'bold', marginBottom: '1rem', borderBottom: '1px solid #1d4ed8', paddingBottom: '0.5rem' }}>Expected Case</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem', color: '#bfdbfe' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Financial</span><span style={{ fontWeight: 'bold', color: 'white' }}>{sim.expected_case.financial}</span></div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Velocity</span><span style={{ fontWeight: 'bold', color: 'white' }}>{sim.expected_case.velocity}</span></div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Risk</span><span style={{ fontWeight: 'bold', color: 'white' }}>{sim.expected_case.risk}</span></div>
                      <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#93c5fd', fontStyle: 'italic', borderTop: '1px solid #1e40af', paddingTop: '0.5rem' }}>"{sim.expected_case.summary}"</div>
                    </div>
                  </div>

                  {/* Worst Case */}
                  <div style={{ background: 'linear-gradient(to bottom, #7f1d1d, #450a0a)', borderRadius: '0.5rem', padding: '1.5rem', border: '1px solid #dc2626' }}>
                    <h4 style={{ fontSize: '0.875rem', color: '#f87171', textTransform: 'uppercase', fontWeight: 'bold', marginBottom: '1rem', borderBottom: '1px solid #b91c1c', paddingBottom: '0.5rem' }}>Worst Case</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem', color: '#fecaca' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Financial</span><span style={{ fontWeight: 'bold', color: 'white' }}>{sim.worst_case.financial}</span></div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Velocity</span><span style={{ fontWeight: 'bold', color: 'white' }}>{sim.worst_case.velocity}</span></div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Risk</span><span style={{ fontWeight: 'bold', color: 'white' }}>{sim.worst_case.risk}</span></div>
                      <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#fca5a5', fontStyle: 'italic', borderTop: '1px solid #991b1b', paddingTop: '0.5rem' }}>"{sim.worst_case.summary}"</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* BOARD OF DIRECTORS MODE (Phase 22) */}
      {data.board_advice && data.board_advice.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', background: '#020617', border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #1e293b', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.25rem', textTransform: 'uppercase', color: '#e2e8f0', letterSpacing: '0.15em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '1.5rem' }}>♟️</span>
              Board of Directors Advisory
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Extreme Perspective Synthesis</div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {data.board_advice.map((board: any, idx: number) => (
              <div key={idx}>
                <h3 style={{ fontSize: '1rem', color: '#cbd5e1', marginBottom: '1.5rem', borderBottom: '1px solid #334155', paddingBottom: '0.5rem' }}>Topic: <span style={{ color: 'white', fontWeight: 'bold' }}>{board.topic}</span></h3>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem' }}>
                  {board.advice.map((adv: any, aIdx: number) => {
                    let advisorColor = '#94a3b8';
                    if (adv.advisor.includes('Buffett')) advisorColor = '#10b981';
                    if (adv.advisor.includes('Munger')) advisorColor = '#059669';
                    if (adv.advisor.includes('Jobs')) advisorColor = '#a855f7';
                    if (adv.advisor.includes('Musk')) advisorColor = '#ef4444';
                    if (adv.advisor.includes('Bezos')) advisorColor = '#f59e0b';
                    
                    return (
                      <div key={aIdx} style={{ background: '#0f172a', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid #1e293b', position: 'relative' }}>
                        <div style={{ position: 'absolute', top: '-10px', left: '1rem', background: advisorColor, color: 'white', fontSize: '0.65rem', fontWeight: 'bold', padding: '0.125rem 0.5rem', borderRadius: '1rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                          {adv.advisor} Model
                        </div>
                        <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#cbd5e1', lineHeight: '1.5', fontStyle: 'italic' }}>
                          "{adv.critique}"
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* DIGITAL TWIN OS (Phase 25) */}
      {data.digital_twin_predictions && data.digital_twin_predictions.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, #09090b 0%, #171717 100%)', border: '1px solid #3f3f46', position: 'relative', overflow: 'hidden' }}>
          {/* Capstone subtle glow */}
          <div style={{ position: 'absolute', top: '-50%', left: '-50%', width: '200%', height: '200%', background: 'radial-gradient(circle, rgba(14, 165, 233, 0.05) 0%, transparent 60%)', pointerEvents: 'none' }}></div>
          
          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #3f3f46', paddingBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.25rem', textTransform: 'uppercase', color: '#f8fafc', letterSpacing: '0.2em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                Digital Twin OS: Predictive Inference
              </h2>
              <div style={{ fontSize: '0.75rem', color: '#0ea5e9', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 'bold', background: 'rgba(14, 165, 233, 0.1)', padding: '0.25rem 0.75rem', borderRadius: '1rem' }}>
                System Capstone
              </div>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              {data.digital_twin_predictions.map((pred: any, idx: number) => {
                let decColor = '#94a3b8';
                if (pred.predicted_decision === 'APPROVE') decColor = '#10b981';
                if (pred.predicted_decision === 'REJECT') decColor = '#ef4444';
                if (pred.predicted_decision === 'DEFER') decColor = '#f59e0b';
                
                return (
                  <div key={idx} style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '0.5rem', border: '1px solid #27272a', padding: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                      <div style={{ flex: 1, paddingRight: '2rem' }}>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>Scenario</div>
                        <h3 style={{ fontSize: '1.5rem', color: 'white', fontWeight: 'bold', lineHeight: '1.2' }}>{pred.scenario}</h3>
                      </div>
                      
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', background: '#09090b', padding: '1rem', borderRadius: '0.5rem', border: `2px solid ${decColor}`, minWidth: '150px' }}>
                        <span style={{ fontSize: '0.65rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Predicted Decision</span>
                        <span style={{ fontSize: '1.5rem', color: decColor, fontWeight: 'bold', letterSpacing: '0.1em', marginBottom: '0.5rem' }}>{pred.predicted_decision}</span>
                        
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', width: '100%', borderTop: '1px solid #27272a', paddingTop: '0.5rem' }}>
                          <span style={{ fontSize: '0.65rem', color: '#64748b' }}>Alignment:</span>
                          <div style={{ flex: 1, height: '4px', background: '#27272a', borderRadius: '2px', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${pred.alignment_confidence * 100}%`, background: '#0ea5e9' }}></div>
                          </div>
                          <span style={{ fontSize: '0.75rem', color: '#0ea5e9', fontWeight: 'bold' }}>{Math.round(pred.alignment_confidence * 100)}%</span>
                        </div>
                      </div>
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '2rem' }}>
                      {/* Reasoning */}
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#0ea5e9', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem', fontWeight: 'bold' }}>Synthesis & Reasoning</div>
                        <div style={{ fontSize: '0.875rem', color: '#cbd5e1', lineHeight: '1.6', background: '#18181b', padding: '1rem', borderRadius: '0.25rem', borderLeft: '2px solid #0ea5e9' }}>
                          {pred.reasoning}
                        </div>
                      </div>
                      
                      {/* Blind Spots */}
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#ef4444', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                          Cognitive Blind Spots
                        </div>
                        <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {pred.cognitive_blind_spots.map((spot: string, sIdx: number) => (
                            <li key={sIdx} style={{ fontSize: '0.75rem', color: '#fca5a5', background: 'rgba(239, 68, 68, 0.1)', padding: '0.5rem 0.75rem', borderRadius: '0.25rem', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                              • {spot}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      )}

      {/* DEVICE AWARENESS / LIVE TELEMETRY (Phase 15) */}
      {data.device_context && (
        <section style={{ marginBottom: '2rem', display: 'flex', gap: '1rem', alignItems: 'center', background: 'rgba(5, 46, 22, 0.5)', padding: '1rem 1.5rem', borderRadius: '0.5rem', border: '1px solid #10b981' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', paddingRight: '1.5rem', borderRight: '1px solid #064e3b' }}>
            <span style={{ display: 'inline-block', width: '10px', height: '10px', background: '#10b981', borderRadius: '50%', animation: 'pulse 2s infinite' }}></span>
            <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: '#34d399', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Live Telemetry</span>
          </div>
          
          <div style={{ display: 'flex', gap: '2rem', flex: 1 }}>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: '0.65rem', color: '#6ee7b7', textTransform: 'uppercase' }}>Active Device</span>
              <span style={{ fontSize: '0.875rem', color: 'white', fontWeight: 'bold' }}>{data.device_context.device_name}</span>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: '0.65rem', color: '#6ee7b7', textTransform: 'uppercase' }}>Location</span>
              <span style={{ fontSize: '0.875rem', color: 'white', fontWeight: 'bold' }}>{data.device_context.location || 'Unknown'}</span>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
              <span style={{ fontSize: '0.65rem', color: '#6ee7b7', textTransform: 'uppercase' }}>Current Focus</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', color: '#a7f3d0', fontWeight: 'bold' }}>{data.device_context.active_app}</span>
                {data.device_context.context_payload && Object.keys(data.device_context.context_payload).map((k) => (
                  <span key={k} style={{ fontSize: '0.75rem', color: '#d1fae5', background: '#064e3b', padding: '0.125rem 0.5rem', borderRadius: '1rem' }}>
                    {k}: {data.device_context!.context_payload![k]}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* BUSINESS REALITY (Phase 10.3) */}
      {data.business_intelligence && (
        <section style={{ marginBottom: '2rem', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
          <div style={{ background: '#0f172a', padding: '1.5rem', borderRadius: '0.5rem', borderBottom: '4px solid #10b981' }}>
            <h3 style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Current MRR</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981' }}>${data.business_intelligence.mrr.toLocaleString()}</div>
          </div>
          
          <div style={{ background: '#0f172a', padding: '1.5rem', borderRadius: '0.5rem', borderBottom: data.business_intelligence.runway_months < 6 ? '4px solid #ef4444' : '4px solid #3b82f6' }}>
            <h3 style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Runway</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: data.business_intelligence.runway_months < 6 ? '#ef4444' : '#3b82f6' }}>
              {data.business_intelligence.runway_months === Infinity ? '∞' : data.business_intelligence.runway_months} <span style={{fontSize:'1rem'}}>months</span>
            </div>
          </div>
          
          <div style={{ background: '#0f172a', padding: '1.5rem', borderRadius: '0.5rem', borderBottom: '4px solid #f59e0b' }}>
            <h3 style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Burn Rate</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fcd34d' }}>${data.business_intelligence.monthly_burn_rate.toLocaleString()}/mo</div>
          </div>
          
          <div style={{ background: '#0f172a', padding: '1.5rem', borderRadius: '0.5rem', borderBottom: data.business_intelligence.founder_roi_score < 1.0 ? '4px solid #ef4444' : '4px solid #8b5cf6' }}>
            <h3 style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Founder ROI</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: data.business_intelligence.founder_roi_score < 1.0 ? '#ef4444' : '#a78bfa' }}>
              {data.business_intelligence.founder_roi_score}x
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>on {data.business_intelligence.hours_tracked} hrs tracked</div>
          </div>
        </section>
      )}

      {/* OPPORTUNITY OS (Phase 11.1) */}
      {data.opportunity_intelligence && (
        <section className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(to right, #064e3b, #0f172a)', border: '1px solid #10b981' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: '#34d399', letterSpacing: '0.05em' }}>
              Opportunity OS
            </h2>
            <div style={{ background: '#022c22', padding: '0.5rem 1rem', borderRadius: '2rem', border: '1px solid #10b981' }}>
              <span style={{ fontSize: '0.75rem', color: '#a7f3d0', textTransform: 'uppercase', marginRight: '0.5rem' }}>Opportunity Score:</span>
              <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#34d399' }}>{data.opportunity_intelligence.opportunity_score}</span>
            </div>
          </div>

          <div style={{ padding: '1.5rem', background: 'rgba(0,0,0,0.4)', borderRadius: '0.5rem' }}>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>
              {data.opportunity_intelligence.title}
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '1.5rem' }}>
              <div>
                <span style={{ display: 'block', fontSize: '0.75rem', color: '#a7f3d0', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Revenue Potential</span>
                <span style={{ fontSize: '1.25rem', color: '#10b981', fontWeight: 'bold' }}>{data.opportunity_intelligence.revenue_potential}</span>
              </div>
              
              <div style={{ borderLeft: '3px solid #3b82f6', paddingLeft: '1rem' }}>
                <span style={{ display: 'block', fontSize: '0.75rem', color: '#93c5fd', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Recommended Action</span>
                <span style={{ fontSize: '1.125rem', color: 'white', fontWeight: 'bold' }}>{data.opportunity_intelligence.recommended_action}</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* RESEARCH OS (Phase 12.0) */}
      {data.research_queue && data.research_queue.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', background: '#1e1b4b', border: '1px solid #6366f1' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: '#a5b4fc', letterSpacing: '0.05em' }}>
              Autonomous Research Queue
            </h2>
            <div style={{ background: '#312e81', padding: '0.25rem 0.75rem', borderRadius: '1rem', fontSize: '0.75rem', color: '#c7d2fe' }}>
              {data.research_queue.length} Active Tasks
            </div>
          </div>
          
          <div style={{ display: 'grid', gap: '1rem' }}>
            {data.research_queue.map((r: any, i: number) => (
              <div key={i} style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '0.5rem', borderLeft: r.status === 'COMPLETE' ? '3px solid #10b981' : '3px solid #6366f1' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 'bold', color: 'white' }}>"{r.query}"</h3>
                  <span style={{ fontSize: '0.75rem', fontWeight: 'bold', padding: '0.25rem 0.5rem', borderRadius: '0.25rem', background: r.status === 'COMPLETE' ? '#064e3b' : '#312e81', color: r.status === 'COMPLETE' ? '#34d399' : '#a5b4fc' }}>
                    {r.status}
                  </span>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#a5b4fc', marginBottom: '0.5rem' }}>Triggered by: {r.trigger_source}</div>
                {r.synthesis_report && (
                  <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#e0e7ff', background: '#312e81', padding: '0.75rem', borderRadius: '0.25rem' }}>
                    {r.synthesis_report}
                  </div>
                )}
                {r.sources_cited && r.sources_cited.length > 0 && (
                  <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#818cf8' }}>
                    <strong>Sources:</strong> {r.sources_cited.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* OUTCOME RESOLUTION QUEUE */}
      {(pendingOutcomes.length > 0 || inferredOutcomes.length > 0) && (
        <section className="card" style={{ marginBottom: '2rem', background: '#374151', border: '1px solid #fbbf24' }}>
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: '#fbbf24', marginBottom: '1rem' }}>Outcome Resolution Queue ({pendingOutcomes.length + inferredOutcomes.length})</h2>
          
          {inferredOutcomes.length > 0 && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '0.75rem', color: '#34d399', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Inferred Outcomes (1-Click)</h3>
              <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {inferredOutcomes.map((inf, i) => (
                  <li key={i} style={{ padding: '0.75rem', background: '#064e3b', borderRadius: '0.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderLeft: '4px solid #34d399' }}>
                    <div>
                      <strong style={{ display: 'block', fontSize: '0.875rem' }}>{inf.recommendation_text}</strong>
                      <span style={{ fontSize: '0.75rem', color: '#a7f3d0' }}>{inf.outcome}</span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button 
                        onClick={async () => {
                          await confirmOutcome(inf.id, 'SUCCESS');
                          fetchData();
                        }}
                        style={{ background: '#34d399', color: 'black', padding: '0.25rem 0.75rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}>
                        Confirm
                      </button>
                      <button 
                        onClick={async () => {
                          await confirmOutcome(inf.id, 'REJECTED');
                          fetchData();
                        }}
                        style={{ background: 'transparent', color: '#fca5a5', padding: '0.25rem 0.75rem', borderRadius: '0.25rem', border: '1px solid #fca5a5', cursor: 'pointer' }}>
                        Reject
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {pendingOutcomes.length > 0 && (
            <div>
              <h3 style={{ fontSize: '0.75rem', color: '#fbbf24', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Pending Execution Logs (Manual Review)</h3>
              <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {pendingOutcomes.map((exec, i) => (
                  <li key={i} style={{ padding: '0.75rem', background: 'var(--bg-main)', borderRadius: '0.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>{exec.command.substring(0, 50)}...</span>
                    <button 
                      onClick={() => openOutcomeModal(exec)}
                      style={{ background: '#3b82f6', color: 'white', padding: '0.25rem 0.75rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer' }}>
                      Log Outcome
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {/* CONTEXT ENGINE: WORK SESSION */}
      {activeSessionData?.session && (
        <section className="card" style={{ marginBottom: '2rem', border: '1px solid #10b981' }}>
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: '#10b981', marginBottom: '1rem', letterSpacing: '0.05em' }}>Current Work Session</h2>
          <div style={{ background: 'var(--bg-main)', padding: '1.5rem', borderRadius: '0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#6b7280', textTransform: 'uppercase' }}>Session ID: {activeSessionData.session.id.split('-')[0]}</span>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#34d399', marginTop: '0.25rem' }}>{activeSessionData.session.session_summary || "Active (Gathering Context...)"}</h3>
              </div>
              <div style={{ padding: '0.5rem 1rem', background: '#064e3b', borderRadius: '2rem', color: '#34d399', fontSize: '0.875rem', fontWeight: 'bold' }}>
                ● RECORDING
              </div>
            </div>
            
            <h4 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Live Observation Stream</h4>
            {activeSessionData.observations.length > 0 ? (
              <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '200px', overflowY: 'auto' }}>
                {activeSessionData.observations.map((obs: any, i: number) => (
                  <li key={i} style={{ padding: '0.5rem', background: '#111827', borderRadius: '0.25rem', fontSize: '0.875rem', display: 'flex', gap: '1rem' }}>
                    <span style={{ color: '#6b7280', fontFamily: 'monospace' }}>[{new Date(obs.created_at).toLocaleTimeString()}]</span>
                    <span style={{ color: obs.source === 'Voice' ? '#60a5fa' : '#a78bfa', fontWeight: 'bold', width: '60px' }}>{obs.source}</span>
                    <span style={{ color: '#d1d5db' }}>{JSON.stringify(obs.payload).substring(0, 100)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>No observations yet...</p>
            )}
          </div>
        </section>
      )}

      {/* CONSTRAINT OS (Phase 11.2) */}
      {data.constraint_intelligence && (
        <section className="card" style={{ marginBottom: '2rem', background: '#450a0a', borderLeft: '6px solid #ef4444' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: '#fca5a5', letterSpacing: '0.05em', fontWeight: 'bold' }}>
              Current Constraint
            </h2>
            <div style={{ background: '#7f1d1d', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: '1px solid #ef4444' }}>
              <span style={{ fontSize: '0.75rem', color: '#fca5a5', textTransform: 'uppercase', marginRight: '0.5rem' }}>Severity:</span>
              <span style={{ fontSize: '1rem', fontWeight: 'bold', color: 'white' }}>{data.constraint_intelligence.severity}</span>
            </div>
          </div>

          <div style={{ padding: '0.5rem 0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.75rem', color: '#fca5a5', textTransform: 'uppercase' }}>Type:</span>
              <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white', textTransform: 'uppercase' }}>{data.constraint_intelligence.type}</span>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
              <div>
                <span style={{ display: 'block', fontSize: '0.75rem', color: '#fca5a5', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Evidence</span>
                <span style={{ fontSize: '1rem', color: '#fecaca' }}>{data.constraint_intelligence.evidence}</span>
              </div>
              
              <div style={{ borderLeft: '2px solid #ef4444', paddingLeft: '1rem' }}>
                <span style={{ display: 'block', fontSize: '0.75rem', color: '#fca5a5', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Recommended Action</span>
                <span style={{ fontSize: '1.125rem', color: 'white', fontWeight: 'bold' }}>{data.constraint_intelligence.recommended_action}</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* TRUTH OS / EPISTEMOLOGY (Phase 23) */}
      {data.epistemology_audits && data.epistemology_audits.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', background: '#020617', border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #1e293b', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.125rem', textTransform: 'uppercase', color: '#f8fafc', letterSpacing: '0.15em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#facc15" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
              Truth OS: Epistemological Baseline
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Chief Auditor</div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {data.epistemology_audits.map((audit: any, idx: number) => {
              let statusColor = '#94a3b8';
              let statusBg = '#0f172a';
              if (audit.verification_status === 'VERIFIED') { statusColor = '#34d399'; statusBg = 'rgba(16, 185, 129, 0.1)'; }
              if (audit.verification_status === 'DEBUNKED') { statusColor = '#f87171'; statusBg = 'rgba(239, 68, 68, 0.1)'; }
              if (audit.verification_status === 'UNVERIFIED') { statusColor = '#facc15'; statusBg = 'rgba(250, 204, 21, 0.1)'; }
              
              return (
                <div key={idx} style={{ background: '#0f172a', borderRadius: '0.5rem', border: '1px solid #334155', padding: '1.25rem', display: 'flex', gap: '1.5rem', alignItems: 'flex-start' }}>
                  
                  {/* Status Indicator */}
                  <div style={{ flex: '0 0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: statusBg, border: `2px solid ${statusColor}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: statusColor, fontWeight: 'bold', fontSize: '1.25rem' }}>
                      {audit.verification_status === 'VERIFIED' ? '✓' : audit.verification_status === 'DEBUNKED' ? '✗' : '?'}
                    </div>
                    <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', color: statusColor, fontWeight: 'bold' }}>{audit.verification_status}</div>
                  </div>
                  
                  {/* Claim Content */}
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                      <h3 style={{ fontSize: '1.125rem', color: 'white', fontWeight: 'bold' }}>"{audit.claim}"</h3>
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                        <span style={{ fontSize: '0.65rem', color: '#94a3b8', textTransform: 'uppercase' }}>Confidence</span>
                        <span style={{ fontSize: '1rem', color: audit.confidence_score > 0.8 ? '#34d399' : audit.confidence_score > 0.4 ? '#facc15' : '#f87171', fontWeight: 'bold' }}>
                          {Math.round(audit.confidence_score * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    <div style={{ display: 'flex', gap: '2rem', marginBottom: '1rem', fontSize: '0.875rem' }}>
                      <div><span style={{ color: '#64748b' }}>Source:</span> <span style={{ color: '#e2e8f0' }}>{audit.source}</span></div>
                      <div>
                        <span style={{ color: '#64748b' }}>Evidence:</span> 
                        <span style={{ color: '#38bdf8', marginLeft: '0.5rem' }}>{audit.evidence.length} items</span>
                      </div>
                    </div>
                    
                    <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.25rem', borderLeft: `3px solid ${statusColor}`, fontSize: '0.875rem', color: '#cbd5e1', fontStyle: 'italic', lineHeight: '1.5' }}>
                      <span style={{ fontSize: '0.65rem', color: '#94a3b8', textTransform: 'uppercase', display: 'block', marginBottom: '0.25rem', fontStyle: 'normal', fontWeight: 'bold' }}>Auditor Notes</span>
                      {audit.auditor_notes}
                    </div>
                  </div>
                  
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* SIMULATION OS (Phase 24) */}
      {data.simulation_timelines && data.simulation_timelines.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', background: '#0a0a0a', border: '1px solid #262626' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #262626', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.125rem', textTransform: 'uppercase', color: '#e5e5e5', letterSpacing: '0.15em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6L6 18M6 6l12 12"></path></svg>
              Simulation OS: Alternate Timelines
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#737373', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Isolated Sandbox Environment</div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {data.simulation_timelines.map((timeline: any, idx: number) => {
              let termColor = '#737373';
              if (timeline.terminal_state === 'SURVIVED') termColor = '#10b981';
              if (timeline.terminal_state === 'BANKRUPT') termColor = '#ef4444';
              if (timeline.terminal_state === 'ACQUIRED') termColor = '#3b82f6';
              
              return (
                <div key={idx} style={{ background: '#171717', borderRadius: '0.5rem', border: '1px solid #404040', padding: '1.5rem', position: 'relative', overflow: 'hidden' }}>
                  {/* Holographic overlay effect */}
                  <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(168, 85, 247, 0.03) 2px, rgba(168, 85, 247, 0.03) 4px)', pointerEvents: 'none' }}></div>
                  
                  <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#a855f7', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 'bold', marginBottom: '0.25rem' }}>{timeline.timeline_name}</div>
                        <h3 style={{ fontSize: '1.25rem', color: 'white', fontWeight: 'bold' }}>Event: {timeline.injected_event}</h3>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', background: 'rgba(0,0,0,0.5)', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: `1px solid ${termColor}` }}>
                        <span style={{ fontSize: '0.65rem', color: '#a3a3a3', textTransform: 'uppercase' }}>Terminal State</span>
                        <span style={{ fontSize: '1rem', color: termColor, fontWeight: 'bold', letterSpacing: '0.05em' }}>{timeline.terminal_state}</span>
                      </div>
                    </div>
                    
                    <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
                      {timeline.cascading_effects.map((effect: any, eIdx: number) => (
                        <div key={eIdx} style={{ flex: '0 0 250px', background: '#262626', borderLeft: '2px solid #a855f7', padding: '1rem', borderRadius: '0 0.25rem 0.25rem 0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#d4d4d8', textTransform: 'uppercase', marginBottom: '0.5rem', fontWeight: 'bold' }}>Month {effect.month}</div>
                          <div style={{ fontSize: '0.875rem', color: '#ef4444', marginBottom: '0.5rem' }}>{effect.financial_impact}</div>
                          <div style={{ fontSize: '0.875rem', color: '#a3a3a3' }}>{effect.operational_impact}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* EXECUTIVE COUNCIL DEBATE (Phase 19) */}
      {data.executive_council && data.executive_council.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', background: '#18181b', border: '1px solid #3f3f46' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #3f3f46', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1rem', textTransform: 'uppercase', color: '#e4e4e7', letterSpacing: '0.1em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ display: 'inline-block', width: '12px', height: '12px', background: '#a855f7', clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)', animation: 'pulse 3s infinite' }}></span>
              Executive Council
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#a1a1aa', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Strategic Debate & Resolution</div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {data.executive_council.map((debate: any, idx: number) => (
              <div key={idx} style={{ background: '#09090b', borderRadius: '0.5rem', border: '1px solid #27272a', padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontSize: '0.65rem', color: '#a855f7', textTransform: 'uppercase', fontWeight: 'bold', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>Proposal</span>
                    <h3 style={{ fontSize: '1.25rem', color: 'white', fontWeight: 'bold' }}>{debate.topic}</h3>
                  </div>
                  <div style={{ fontSize: '0.75rem', background: debate.status === 'DEBATING' ? 'rgba(234, 179, 8, 0.2)' : 'rgba(16, 185, 129, 0.2)', color: debate.status === 'DEBATING' ? '#fde047' : '#34d399', padding: '0.25rem 0.75rem', borderRadius: '1rem', textTransform: 'uppercase', fontWeight: 'bold', letterSpacing: '0.05em' }}>
                    {debate.status}
                  </div>
                </div>
                
                {/* Arguments Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                  {debate.arguments.map((arg: any, argIdx: number) => {
                    let stanceColor = '#94a3b8';
                    if (arg.stance === 'LAUNCH NOW' || arg.stance === 'PROCEED') stanceColor = '#34d399';
                    if (arg.stance === 'DELAY' || arg.stance === 'CAUTION') stanceColor = '#fbbf24';
                    if (arg.stance === 'IMPOSSIBLE' || arg.stance === 'REJECT') stanceColor = '#f87171';
                    if (arg.stance === 'NEUTRAL' || arg.stance === 'FEASIBLE') stanceColor = '#60a5fa';
                    
                    return (
                      <div key={argIdx} style={{ background: '#18181b', padding: '1rem', borderRadius: '0.5rem', borderTop: `3px solid ${stanceColor}`, display: 'flex', flexDirection: 'column' }}>
                        <div style={{ fontSize: '0.875rem', color: 'white', fontWeight: 'bold', marginBottom: '0.25rem' }}>{arg.executive}</div>
                        <div style={{ fontSize: '0.65rem', color: stanceColor, textTransform: 'uppercase', fontWeight: 'bold', marginBottom: '0.75rem' }}>{arg.stance}</div>
                        <div style={{ fontSize: '0.75rem', color: '#d4d4d8', fontStyle: 'italic', lineHeight: '1.4', flex: 1 }}>"{arg.argument}"</div>
                      </div>
                    );
                  })}
                </div>
                
                {/* Resolution / Action */}
                <div style={{ background: debate.founder_decision ? 'rgba(16, 185, 129, 0.1)' : 'rgba(168, 85, 247, 0.1)', border: `1px solid ${debate.founder_decision ? '#10b981' : '#a855f7'}`, padding: '1rem', borderRadius: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: debate.founder_decision ? '#34d399' : '#c084fc', textTransform: 'uppercase', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                      {debate.founder_decision ? 'Founder Decision' : 'Chief of Staff Request'}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'white' }}>
                      {debate.founder_decision ? debate.founder_decision : 'Arguments synthesized. Awaiting Founder resolution.'}
                    </div>
                  </div>
                  {!debate.founder_decision && (
                    <button style={{ background: '#a855f7', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '0.25rem', fontSize: '0.75rem', fontWeight: 'bold', cursor: 'pointer', textTransform: 'uppercase' }}>
                      Make Decision
                    </button>
                  )}
                </div>

              </div>
            ))}
          </div>
        </section>
      )}

      {/* MISSION AUTONOMY PIPELINE (Phase 18) */}
      {data.mission_autonomy && data.mission_autonomy.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', background: '#020617', border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #1e293b', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1rem', textTransform: 'uppercase', color: '#f8fafc', letterSpacing: '0.1em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ display: 'inline-block', width: '12px', height: '12px', background: '#0ea5e9', clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)', animation: 'pulse 2s infinite' }}></span>
              Mission Autonomy Pipeline
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Multi-Agent Orchestration</div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {data.mission_autonomy.map((mission: any, idx: number) => (
              <div key={idx} style={{ background: '#0f172a', borderRadius: '0.5rem', border: '1px solid #334155', padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1.125rem', color: 'white', fontWeight: 'bold' }}>{mission.mission_name}</h3>
                  <div style={{ fontSize: '0.75rem', background: mission.status === 'IN_PROGRESS' ? 'rgba(14, 165, 233, 0.2)' : 'rgba(16, 185, 129, 0.2)', color: mission.status === 'IN_PROGRESS' ? '#38bdf8' : '#34d399', padding: '0.25rem 0.75rem', borderRadius: '1rem', textTransform: 'uppercase', fontWeight: 'bold', letterSpacing: '0.05em' }}>
                    {mission.status}
                  </div>
                </div>
                
                {/* Visual Pipeline */}
                <div style={{ display: 'flex', alignItems: 'flex-start', position: 'relative' }}>
                  {/* Connecting Line */}
                  <div style={{ position: 'absolute', top: '1.25rem', left: '2rem', right: '2rem', height: '2px', background: '#334155', zIndex: 0 }}></div>
                  
                  {mission.workflow_pipeline.map((stage: any, sIdx: number) => {
                    const isCompleted = stage.status === 'COMPLETED';
                    const isActive = stage.status === 'IN_PROGRESS';
                    
                    
                    let nodeColor = '#334155'; // Pending
                    if (isCompleted) nodeColor = '#10b981'; // Green
                    if (isActive) nodeColor = '#0ea5e9'; // Blue
                    
                    return (
                      <div key={sIdx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative', zIndex: 1 }}>
                        {/* Node Circle */}
                        <div style={{ 
                          width: '2.5rem', height: '2.5rem', borderRadius: '50%', 
                          background: isCompleted || isActive ? nodeColor : '#1e293b', 
                          border: `2px solid ${isCompleted || isActive ? nodeColor : '#475569'}`,
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          marginBottom: '0.75rem', color: isCompleted || isActive ? 'white' : '#94a3b8',
                          boxShadow: isActive ? `0 0 15px ${nodeColor}` : 'none'
                        }}>
                          {isCompleted ? '✓' : stage.stage}
                        </div>
                        
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: '0.75rem', color: isCompleted || isActive ? 'white' : '#94a3b8', fontWeight: 'bold', marginBottom: '0.25rem' }}>{stage.agent}</div>
                          <div style={{ fontSize: '0.65rem', color: '#64748b', maxWidth: '120px' }}>{stage.task}</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* AUTONOMOUS WORKFORCE (Phase 14) */}
      {data.agent_workforce && data.agent_workforce.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', background: '#020617', border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #1e293b', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1rem', textTransform: 'uppercase', color: '#f8fafc', letterSpacing: '0.1em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ display: 'inline-block', width: '8px', height: '8px', background: '#3b82f6', borderRadius: '50%', boxShadow: '0 0 10px #3b82f6' }}></span>
              Autonomous Workforce
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Active Swarm</div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
            {data.agent_workforce.map((agent: any, idx: number) => {
              const isExecuting = agent.status === 'EXECUTING';
              return (
                <div key={idx} style={{ 
                  background: isExecuting ? 'rgba(59, 130, 246, 0.1)' : 'rgba(30, 41, 59, 0.5)', 
                  border: isExecuting ? '1px solid #3b82f6' : '1px solid #334155',
                  borderRadius: '0.5rem', padding: '1rem' 
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.875rem', fontWeight: 'bold', color: 'white', textTransform: 'uppercase' }}>
                      {agent.role} Agent
                    </div>
                    <div style={{ 
                      fontSize: '0.65rem', 
                      background: isExecuting ? '#1e3a8a' : '#1e293b', 
                      color: isExecuting ? '#93c5fd' : '#94a3b8', 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '1rem',
                      textTransform: 'uppercase',
                      fontWeight: 'bold',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.3rem'
                    }}>
                      {isExecuting && (
                        <span style={{ display: 'inline-block', width: '6px', height: '6px', background: '#60a5fa', borderRadius: '50%', animation: 'pulse 1.5s infinite' }}></span>
                      )}
                      {agent.status}
                    </div>
                  </div>
                  
                  {isExecuting ? (
                    <div>
                      <div style={{ fontSize: '0.65rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Current Operation</div>
                      <div style={{ fontSize: '0.875rem', color: '#e2e8f0', lineHeight: '1.4' }}>{agent.current_action}</div>
                    </div>
                  ) : (
                    <div style={{ fontSize: '0.875rem', color: '#64748b', fontStyle: 'italic' }}>Standing by for delegation.</div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* AUTONOMY GOVERNANCE (Phase 15.5) */}
      {data.autonomy_governance && data.autonomy_governance.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', background: '#18181b', border: '1px solid #52525b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #27272a', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1rem', textTransform: 'uppercase', color: '#e4e4e7', letterSpacing: '0.1em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ display: 'inline-block', width: '12px', height: '14px', background: '#a1a1aa', clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)' }}></span>
              Autonomy Governance Layer
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#71717a', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Trust Gate</div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
            {data.autonomy_governance.map((gov: any, idx: number) => {
              // Level colors: 0 (Gray), 1 (Yellow), 2 (Blue), 3 (Green), 4 (Purple)
              const levelColors = ['#52525b', '#ca8a04', '#2563eb', '#16a34a', '#9333ea'];
              const levelNames = ['Level 0: Observe', 'Level 1: Recommend', 'Level 2: Execute w/ Approval', 'Level 3: Execute Independently', 'Level 4: Mission Autonomy'];
              const activeColor = levelColors[gov.autonomy_level];
              const activeName = levelNames[gov.autonomy_level];
              
              return (
                <div key={idx} style={{ 
                  background: '#27272a', 
                  borderLeft: `4px solid ${activeColor}`,
                  borderRadius: '0.5rem', padding: '1rem' 
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.875rem', fontWeight: 'bold', color: 'white' }}>
                      {gov.domain}
                    </div>
                    <div style={{ 
                      fontSize: '0.65rem', 
                      background: 'rgba(0,0,0,0.3)', 
                      color: activeColor, 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '1rem',
                      textTransform: 'uppercase',
                      fontWeight: 'bold',
                      border: `1px solid ${activeColor}`
                    }}>
                      {activeName}
                    </div>
                  </div>
                  
                  <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.65rem', color: '#a1a1aa', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Trust Score</div>
                      <div style={{ width: '100%', background: '#18181b', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${gov.trust_score * 100}%`, background: gov.trust_score > 0.8 ? '#10b981' : (gov.trust_score > 0.4 ? '#eab308' : '#ef4444'), height: '100%', borderRadius: '3px' }}></div>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'white', marginTop: '0.25rem', textAlign: 'right' }}>{Math.round(gov.trust_score * 100)}%</div>
                    </div>
                    
                    <div style={{ flex: 1, borderLeft: '1px solid #3f3f46', paddingLeft: '1rem' }}>
                      <div style={{ fontSize: '0.65rem', color: '#a1a1aa', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Success Rate</div>
                      <div style={{ fontSize: '1rem', color: 'white', fontWeight: 'bold' }}>{Math.round(gov.success_rate * 100)}%</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* REALITY PROOFS (Phase 16) */}
      {data.reality_proofs && data.reality_proofs.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', background: '#09090b', border: '1px solid #27272a' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #27272a', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1rem', textTransform: 'uppercase', color: '#e4e4e7', letterSpacing: '0.1em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ display: 'inline-block', width: '12px', height: '12px', background: '#10b981', clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)' }}></span>
              Execution Ledgers & Reality Proofs
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#71717a', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Cryptographic Verification</div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {data.reality_proofs.map((proof: any, idx: number) => (
              <div key={idx} style={{ 
                background: '#18181b', 
                border: '1px solid #3f3f46',
                borderRadius: '0.5rem', padding: '1rem',
                display: 'flex', alignItems: 'center', gap: '1rem'
              }}>
                <div style={{ flex: '0 0 auto', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                  ✓
                </div>
                
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.25rem' }}>
                    <span style={{ fontSize: '0.875rem', fontWeight: 'bold', color: 'white' }}>{proof.agent_role}</span>
                    {proof.verified && (
                      <span style={{ fontSize: '0.65rem', background: '#064e3b', color: '#34d399', padding: '0.125rem 0.5rem', borderRadius: '1rem', textTransform: 'uppercase', fontWeight: 'bold' }}>Verified</span>
                    )}
                  </div>
                  <div style={{ fontSize: '0.875rem', color: '#e4e4e7', marginBottom: '0.5rem' }}>{proof.action_taken}</div>
                  
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.75rem' }}>
                    <a href={proof.proof_url} target="_blank" rel="noreferrer" style={{ color: '#3b82f6', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                      View Artifact
                    </a>
                    <span style={{ color: '#71717a' }}>|</span>
                    <span style={{ color: '#a1a1aa', fontFamily: 'monospace' }}>Hash: {proof.proof_hash?.substring(0, 16)}...</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* HIGHEST LEVERAGE ACTION */}
      <section style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-secondary)', letterSpacing: '0.05em' }}>
            Highest Leverage Action
          </h2>
          <button 
            onClick={handleShowAudit}
            style={{ background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--text-secondary)', padding: '0.25rem 0.75rem', borderRadius: '0.25rem', cursor: 'pointer', fontSize: '0.75rem', textTransform: 'uppercase' }}>
            Why?
          </button>
        </div>
        <div style={{ background: 'var(--accent)', color: 'black', padding: '1.5rem', borderRadius: '0.5rem' }}>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
            {data.highest_leverage_action.statement}
          </h3>
          <p style={{ marginBottom: '1rem', opacity: 0.9 }}>{data.highest_leverage_action.reason}</p>
          
          {data.highest_leverage_action.constraint_reason && (
            <div style={{ marginBottom: '1.5rem', background: 'rgba(0,0,0,0.1)', padding: '1rem', borderRadius: '0.5rem', borderLeft: '4px solid #ef4444' }}>
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 'bold', color: '#991b1b', display: 'block', marginBottom: '0.25rem' }}>Constraint Resolution</span>
              <span style={{ fontSize: '0.875rem', color: '#450a0a' }}>{data.highest_leverage_action.constraint_reason}</span>
            </div>
          )}
          
          <div style={{ display: 'flex', gap: '2rem', fontSize: '0.875rem' }}>
            <div>
              <strong>Impact:</strong> {data.highest_leverage_action.impact_score}/10
            </div>
            <div>
              <strong>Confidence:</strong> {data.highest_leverage_action.confidence_score}
            </div>
            <div>
              <strong>Expected Leverage:</strong> {data.highest_leverage_action.estimated_leverage}
            </div>
          </div>
          
          {/* MENTOR SYNTHESIS (Polymath Engine) */}
          {data.highest_leverage_action.expert_advice && (
            <div style={{ marginTop: '1.5rem', background: '#1f2937', color: 'white', padding: '1rem', borderRadius: '0.5rem', borderLeft: '4px solid #fbbf24' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <h4 style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#fbbf24', letterSpacing: '0.05em' }}>Mentor Synthesis</h4>
                <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>{data.highest_leverage_action.expert_advice.expert_name}</span>
              </div>
              <strong style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: '#34d399' }}>
                Framework: {data.highest_leverage_action.expert_advice.framework_name}
              </strong>
              <p style={{ fontSize: '0.875rem', lineHeight: '1.5', color: '#d1d5db' }}>
                {data.highest_leverage_action.expert_advice.advice}
              </p>
            </div>
          )}
        </div>
      </section>

      {/* FOUNDER DIGITAL TWIN V2 (Phase 17) */}
      {data.digital_twin && (
        <section className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, #171717 0%, #2e1065 100%)', border: '1px solid #8b5cf6', boxShadow: '0 4px 20px rgba(139, 92, 246, 0.15)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid rgba(139, 92, 246, 0.2)', paddingBottom: '1rem' }}>
            <h2 style={{ fontSize: '1rem', textTransform: 'uppercase', color: '#ddd6fe', letterSpacing: '0.1em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ display: 'inline-block', width: '12px', height: '12px', background: '#8b5cf6', borderRadius: '50%', boxShadow: '0 0 12px #8b5cf6', animation: 'pulse 3s infinite' }}></span>
              Founder Digital Twin
            </h2>
            <div style={{ fontSize: '0.75rem', color: '#c4b5fd', textTransform: 'uppercase', letterSpacing: '0.05em' }}>DNA Prediction Engine</div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Energy Model */}
              <div style={{ background: 'rgba(0,0,0,0.4)', padding: '1.5rem', borderRadius: '0.5rem', borderLeft: '3px solid #f59e0b' }}>
                <h3 style={{ fontSize: '0.75rem', color: '#fcd34d', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Current Energy State ({data.digital_twin.energy_state.current_time})</h3>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'white' }}>{data.digital_twin.energy_state.energy_level}</div>
                  <div style={{ fontSize: '0.75rem', background: 'rgba(245, 158, 11, 0.2)', color: '#fde68a', padding: '0.25rem 0.5rem', borderRadius: '1rem', fontWeight: 'bold' }}>Optimal: {data.digital_twin.energy_state.optimal_task}</div>
                </div>
              </div>

              {/* Preference Graph */}
              <div style={{ background: 'rgba(0,0,0,0.4)', padding: '1.5rem', borderRadius: '0.5rem' }}>
                <h3 style={{ fontSize: '0.75rem', color: '#c4b5fd', textTransform: 'uppercase', marginBottom: '1rem' }}>Preference Graph</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {data.digital_twin.preferences.map((p: any, i: number) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                      <span style={{ color: '#34d399', fontWeight: 'bold' }}>{p.preferred}</span>
                      <span style={{ color: '#6b7280', margin: '0 0.5rem' }}>&gt;</span>
                      <span style={{ color: '#f87171' }}>{p.rejected}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Decision Prediction Engine */}
            <div style={{ background: '#1e1b4b', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #4c1d95', display: 'flex', flexDirection: 'column' }}>
              <h3 style={{ fontSize: '0.75rem', color: '#c4b5fd', textTransform: 'uppercase', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 16 16 12 12 8"></polyline><line x1="8" y1="12" x2="16" y2="12"></line></svg>
                Active Decision Prediction
              </h3>
              
              <div style={{ fontSize: '0.875rem', color: '#e2e8f0', marginBottom: '1rem', fontStyle: 'italic', background: 'rgba(0,0,0,0.2)', padding: '0.75rem', borderRadius: '0.25rem' }}>
                "{data.digital_twin.active_prediction.situation}"
              </div>
              
              <div style={{ marginTop: 'auto' }}>
                <div style={{ fontSize: '0.75rem', color: '#a78bfa', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Predicted Choice</div>
                <div style={{ fontSize: '1.25rem', color: '#34d399', fontWeight: 'bold', marginBottom: '1rem' }}>{data.digital_twin.active_prediction.prediction}</div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                  <div style={{ fontSize: '0.875rem', color: '#c4b5fd', maxWidth: '75%', lineHeight: '1.4' }}>
                    {data.digital_twin.active_prediction.reason}
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.65rem', color: '#8b5cf6', textTransform: 'uppercase', marginBottom: '0.125rem' }}>Confidence</div>
                    <div style={{ fontSize: '1.5rem', color: 'white', fontWeight: 'bold' }}>{Math.round(data.digital_twin.active_prediction.confidence * 100)}%</div>
                  </div>
                </div>
              </div>
            </div>
            
          </div>
        </section>
      )}

      {/* RELATIONSHIP INTELLIGENCE (Phase 10.1) */}
      {data.relationship_intelligence && (
        <section className="card" style={{ marginBottom: '2rem', border: '1px solid #f472b6', background: 'linear-gradient(to right, #111827, #31152a)' }}>
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: '#f472b6', marginBottom: '1rem', letterSpacing: '0.05em' }}>
            Relationship Intelligence
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
            
            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '0.5rem' }}>
              <h3 style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Top Strategic Contacts</h3>
              <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {data.relationship_intelligence.top_strategic_contacts.map((c: any, i: number) => (
                  <li key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', padding: '0.5rem', background: '#1f2937', borderRadius: '0.25rem' }}>
                    <span><strong>{c.name}</strong> ({c.role})</span>
                    <span style={{ color: '#34d399' }}>{c.leverage}x Lev</span>
                  </li>
                ))}
              </ul>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '0.5rem', border: '1px solid #991b1b' }}>
              <h3 style={{ fontSize: '0.75rem', color: '#fca5a5', textTransform: 'uppercase', marginBottom: '0.5rem' }}>At-Risk Relationships</h3>
              {data.relationship_intelligence.relationships_at_risk.length > 0 ? (
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {data.relationship_intelligence.relationships_at_risk.map((r: any, i: number) => (
                    <li key={i} style={{ fontSize: '0.875rem', padding: '0.5rem', background: '#450a0a', borderLeft: '3px solid #f87171', borderRadius: '0.25rem' }}>
                      <strong style={{ color: '#fca5a5' }}>{r.name}</strong>
                      <p style={{ fontSize: '0.75rem', marginTop: '0.25rem', color: '#fecaca' }}>Val: {r.strategic_value} | {r.reason}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p style={{ fontSize: '0.875rem', color: '#9ca3af' }}>No high-value relationships neglected.</p>
              )}
            </div>

            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '0.5rem', border: '1px solid #d97706' }}>
              <h3 style={{ fontSize: '0.75rem', color: '#fbbf24', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Pending Commitments</h3>
              {data.relationship_intelligence.pending_commitments.length > 0 ? (
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {data.relationship_intelligence.pending_commitments.map((c: any, i: number) => (
                    <li key={i} style={{ fontSize: '0.75rem', padding: '0.5rem', background: '#451a03', borderLeft: '3px solid #fbbf24', borderRadius: '0.25rem', color: '#fde68a' }}>
                      {c.insight}
                    </li>
                  ))}
                </ul>
              ) : (
                <p style={{ fontSize: '0.875rem', color: '#9ca3af' }}>All commitments fulfilled.</p>
              )}
            </div>
            
          </div>
        </section>
      )}

      {/* ATTENTION OS AUDIT */}
      <AttentionAuditWidget attentionAudit={attentionAudit} />

      {/* FOUNDER MRI (Phase 11.0) */}
      {data.founder_intelligence && (
        <section className="card" style={{ marginBottom: '2rem', border: '1px solid #8b5cf6', background: 'linear-gradient(to right, #1e1b4b, #2e1065)' }}>
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: '#c4b5fd', marginBottom: '1rem', letterSpacing: '0.05em' }}>Founder MRI</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
            {/* Peak Window */}
            <div style={{ background: 'rgba(0,0,0,0.4)', padding: '1.5rem', borderRadius: '0.5rem', borderTop: '3px solid #10b981' }}>
              <h3 style={{ fontSize: '0.75rem', color: '#a7f3d0', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Peak Execution Window</h3>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'white' }}>
                {data.founder_intelligence.peak_performance_window}
              </div>
              <p style={{ fontSize: '0.75rem', color: '#6ee7b7', marginTop: '0.5rem' }}>Highest focus, lowest energy drain.</p>
            </div>

            {/* Primary Failure Cause */}
            <div style={{ background: 'rgba(0,0,0,0.4)', padding: '1.5rem', borderRadius: '0.5rem', borderTop: '3px solid #ef4444' }}>
              <h3 style={{ fontSize: '0.75rem', color: '#fca5a5', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Primary Failure Cause</h3>
              <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: 'white' }}>
                {data.founder_intelligence.primary_failure_cause}
              </div>
            </div>

            {/* Energy Vampires */}
            <div style={{ background: 'rgba(0,0,0,0.4)', padding: '1.5rem', borderRadius: '0.5rem', borderTop: '3px solid #f59e0b' }}>
              <h3 style={{ fontSize: '0.75rem', color: '#fcd34d', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Energy Vampires</h3>
              {data.founder_intelligence.energy_vampires && data.founder_intelligence.energy_vampires.length > 0 ? (
                <ul style={{ display: 'grid', gap: '0.5rem' }}>
                  {data.founder_intelligence.energy_vampires.map((v: any, i: number) => (
                    <li key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                      <span style={{ color: 'white' }}>{v.name}</span>
                      <span style={{ color: '#ef4444', fontWeight: 'bold' }}>{v.avg_drain}/10 drain</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <span style={{ color: '#9ca3af', fontSize: '0.875rem' }}>No vampires detected.</span>
              )}
            </div>
          </div>

          {/* Stop Doing List */}
          {data.founder_intelligence.stop_doing_list && data.founder_intelligence.stop_doing_list.length > 0 && (
            <div style={{ marginTop: '1.5rem', background: '#450a0a', padding: '1.5rem', borderRadius: '0.5rem', borderLeft: '4px solid #ef4444' }}>
              <h3 style={{ fontSize: '0.875rem', color: '#fca5a5', textTransform: 'uppercase', marginBottom: '1rem', fontWeight: 'bold' }}>🛑 WHAT TO STOP DOING</h3>
              <ul style={{ display: 'grid', gap: '0.75rem' }}>
                {data.founder_intelligence.stop_doing_list.map((item: any, i: number) => (
                  <li key={i} style={{ display: 'grid', gap: '0.25rem' }}>
                    <span style={{ color: 'white', fontWeight: 'bold', fontSize: '1rem' }}>{item.activity}</span>
                    <span style={{ color: '#fca5a5', fontSize: '0.875rem' }}>{item.reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {/* MISSION GRAPH (Phase 10.2) */}
      {data.mission_graph && data.mission_graph.length > 0 && (
        <section className="card" style={{ marginBottom: '2rem', border: '1px solid #3b82f6', background: 'linear-gradient(to right, #111827, #0f172a)' }}>
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: '#60a5fa', marginBottom: '1rem', letterSpacing: '0.05em' }}>Mission Health & Project Momentum</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
            <div style={{ display: 'grid', gap: '1rem' }}>
              {data.mission_graph.map((m: any, i: number) => (
                <div key={i} style={{ background: 'rgba(0,0,0,0.3)', padding: '1.5rem', borderRadius: '0.5rem', borderLeft: `4px solid ${m.health_score >= 50 ? '#34d399' : '#f87171'}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                    <div>
                      <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', color: 'white' }}>{m.title}</h3>
                      <div style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
                        <span style={{ color: '#9ca3af', marginRight: '0.5rem' }}>Constraint:</span>
                        <span style={{ color: m.constraint ? '#fbbf24' : '#10b981', fontWeight: 'bold' }}>{m.constraint || 'None'}</span>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 'bold', color: m.health_score >= 50 ? '#34d399' : '#f87171' }}>Health: {m.health_score}%</div>
                      <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '0.25rem' }}>Velocity: {m.momentum_forecast}</div>
                    </div>
                  </div>
                  {m.projects && m.projects.length > 0 ? (
                    <ul style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                      {m.projects.map((p: any, j: number) => (
                        <li key={j} style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.25rem', border: p.forecast === 'Stall' ? '1px solid #ef4444' : '1px solid transparent' }}>
                          <strong style={{ display: 'block', marginBottom: '0.5rem', color: 'white' }}>{p.title}</strong>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#9ca3af', marginBottom: '0.5rem' }}>
                            <span>Momentum: {p.momentum_score}%</span>
                            <span>Vel: {p.velocity}/day</span>
                          </div>
                          <div style={{ fontSize: '0.75rem', fontWeight: 'bold', padding: '0.25rem', textAlign: 'center', borderRadius: '0.25rem', 
                            background: p.forecast === 'Stall' ? '#7f1d1d' : p.forecast === 'At Risk' ? '#78350f' : '#064e3b',
                            color: p.forecast === 'Stall' ? '#fca5a5' : p.forecast === 'At Risk' ? '#fcd34d' : '#6ee7b7'
                          }}>
                            Forecast: {p.forecast}
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>No active projects.</p>
                  )}
                </div>
              ))}
            </div>

            {/* STRATEGIC BOTTLENECKS WIDGET */}
            <div>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #b91c1c' }}>
                <h3 style={{ fontSize: '0.875rem', color: '#ef4444', textTransform: 'uppercase', marginBottom: '1rem' }}>Strategic Bottlenecks</h3>
                {data.strategic_bottlenecks && data.strategic_bottlenecks.length > 0 ? (
                  <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {data.strategic_bottlenecks.map((b: any, i: number) => (
                      <li key={i} style={{ background: '#450a0a', padding: '0.75rem', borderRadius: '0.25rem', borderLeft: '3px solid #ef4444' }}>
                        <strong style={{ display: 'block', fontSize: '0.875rem', color: 'white', marginBottom: '0.25rem' }}>{b.statement}</strong>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#fca5a5' }}>
                          <span>Blocks {b.blocks_count} tasks</span>
                          <span>Impact: {b.blast_radius_impact}</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ fontSize: '0.875rem', color: '#9ca3af' }}>No critical bottlenecks detected.</p>
                )}
              </div>
            </div>
          </div>
        </section>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* TOP PRIORITIES */}
        <section className="card">
          <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '1rem' }}>Top Priorities</h2>
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
      </div>

      {/* OUTCOME MODAL */}
      {showOutcomeModal && selectedExecution && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#1f2937', padding: '2rem', borderRadius: '0.5rem', width: '500px', maxWidth: '90%' }}>
            <h2 style={{ marginBottom: '1rem' }}>Log Outcome</h2>
            <div style={{ marginBottom: '1rem', padding: '1rem', background: '#111827', borderRadius: '0.25rem', fontFamily: 'monospace', fontSize: '0.875rem' }}>
              {selectedExecution.command}
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Status</label>
                <select value={outcomeForm.status} onChange={e => setOutcomeForm({...outcomeForm, status: e.target.value})} style={{ width: '100%', padding: '0.5rem', background: '#111827', color: 'white', border: '1px solid #374151', borderRadius: '0.25rem' }}>
                  <option value="SUCCESS">Success</option>
                  <option value="PARTIAL">Partial Success</option>
                  <option value="FAILURE">Failure</option>
                </select>
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Domain</label>
                  <select value={outcomeForm.domain} onChange={e => setOutcomeForm({...outcomeForm, domain: e.target.value})} style={{ width: '100%', padding: '0.5rem', background: '#111827', color: 'white', border: '1px solid #374151', borderRadius: '0.25rem' }}>
                    <option value="Execution">Execution</option>
                    <option value="Architecture">Architecture</option>
                    <option value="Research">Research</option>
                    <option value="Sales">Sales</option>
                    <option value="Product">Product</option>
                  </select>
                </div>
                
                {outcomeForm.status !== 'SUCCESS' && (
                  <div>
                    <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Failure Reason</label>
                    <select value={outcomeForm.failure_reason} onChange={e => setOutcomeForm({...outcomeForm, failure_reason: e.target.value})} style={{ width: '100%', padding: '0.5rem', background: '#111827', color: 'white', border: '1px solid #374151', borderRadius: '0.25rem' }}>
                      <option value="None">None</option>
                      <option value="Overengineering">Overengineering</option>
                      <option value="Lack of validation">Lack of validation</option>
                      <option value="Poor prioritization">Poor prioritization</option>
                      <option value="Slow execution">Slow execution</option>
                      <option value="External dependency">External dependency</option>
                    </select>
                  </div>
                )}
              </div>
              
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Outcome / Notes</label>
                <textarea value={outcomeForm.outcome} onChange={e => setOutcomeForm({...outcomeForm, outcome: e.target.value})} style={{ width: '100%', padding: '0.5rem', background: '#111827', color: 'white', border: '1px solid #374151', borderRadius: '0.25rem', minHeight: '80px' }} />
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Impact (1-10)</label>
                  <input type="number" min="1" max="10" value={outcomeForm.impact_score} onChange={e => setOutcomeForm({...outcomeForm, impact_score: parseFloat(e.target.value)})} style={{ width: '100%', padding: '0.5rem', background: '#111827', color: 'white', border: '1px solid #374151', borderRadius: '0.25rem' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Hours Saved</label>
                  <input type="number" min="0" step="0.5" value={outcomeForm.hours_saved} onChange={e => setOutcomeForm({...outcomeForm, hours_saved: parseFloat(e.target.value)})} style={{ width: '100%', padding: '0.5rem', background: '#111827', color: 'white', border: '1px solid #374151', borderRadius: '0.25rem' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Hours Invested</label>
                  <input type="number" min="0" step="0.5" value={outcomeForm.hours_invested} onChange={e => setOutcomeForm({...outcomeForm, hours_invested: parseFloat(e.target.value)})} style={{ width: '100%', padding: '0.5rem', background: '#111827', color: 'white', border: '1px solid #374151', borderRadius: '0.25rem' }} />
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowOutcomeModal(false)} style={{ padding: '0.5rem 1rem', background: 'transparent', border: '1px solid #4b5563', color: 'white', borderRadius: '0.25rem', cursor: 'pointer' }}>Cancel</button>
              <button onClick={handleLogOutcome} style={{ padding: '0.5rem 1rem', background: '#34d399', border: 'none', color: 'black', fontWeight: 'bold', borderRadius: '0.25rem', cursor: 'pointer' }}>Log Outcome & Learn</button>
            </div>
          </div>
        </div>
      )}

      {/* AUDIT MODAL */}
      {showAuditModal && auditData && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#1f2937', padding: '2rem', borderRadius: '0.5rem', width: '500px', maxWidth: '90%' }}>
            <h2 style={{ marginBottom: '1rem', color: '#60a5fa' }}>Audit Trace: Recommendation</h2>
            
            <div style={{ background: '#111827', padding: '1rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>{auditData.statement}</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{auditData.llm_explanation}</p>
            </div>

            <h3 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Deterministic Scoring Breakdown</h3>
            <div style={{ background: '#111827', padding: '1rem', borderRadius: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Impact Score (x0.35):</span>
                <span>{auditData.impact_score.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Urgency Score (x0.25):</span>
                <span>{auditData.urgency_score.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Intent Alignment (x0.20):</span>
                <span>{auditData.intent_alignment_score.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Trust Score (x0.10):</span>
                <span>{auditData.trust_score.toFixed(2)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Reversibility Score (x0.10):</span>
                <span>{auditData.reversibility_score.toFixed(2)}</span>
              </div>
              <div style={{ height: '1px', background: '#374151', margin: '0.5rem 0' }}></div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', fontSize: '1.1rem', color: '#34d399' }}>
                <span>Final Score:</span>
                <span>{auditData.final_score.toFixed(2)}</span>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '2rem' }}>
              <button onClick={() => setShowAuditModal(false)} style={{ padding: '0.5rem 1.5rem', background: '#3b82f6', border: 'none', color: 'white', borderRadius: '0.25rem', cursor: 'pointer' }}>Close</button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
