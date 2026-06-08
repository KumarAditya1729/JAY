import { useEffect, useState } from 'react';
import { getBriefing } from '../api';

export default function Briefings() {
  const [briefing, setBriefing] = useState<any>(null);
  const [type, setType] = useState<'morning' | 'evening' | 'weekly' | 'monthly'>('morning');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getBriefing(type)
      .then(setBriefing)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [type]);

  return (
    <div>
      <header className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">Daily Briefing</h1>
          <p className="page-subtitle">Situational Awareness</p>
        </div>
        <select 
          value={type} 
          onChange={(e) => setType(e.target.value as any)}
          style={{ padding: '0.5rem', borderRadius: '0.5rem', background: 'var(--bg-surface)', color: 'white', border: '1px solid var(--border)' }}
        >
          <option value="morning">Morning Brief</option>
          <option value="evening">Evening Review</option>
          <option value="weekly">Weekly Review</option>
          <option value="monthly">Monthly Review</option>
        </select>
      </header>

      {loading ? <div>Loading...</div> : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {Object.entries(briefing || {}).map(([key, val]: [string, any]) => {
             if (key === 'id' || key === 'founder_id' || key === 'date' || key === 'type') return null;
             return (
               <div key={key} className="card">
                 <h3 style={{ textTransform: 'capitalize', marginBottom: '1rem', color: 'var(--accent)' }}>
                    {key.replace(/_/g, ' ')}
                 </h3>
                 {Array.isArray(val) ? (
                    <ul style={{ paddingLeft: '1.2rem' }}>
                      {val.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                 ) : (
                    <p>{String(val)}</p>
                 )}
               </div>
             )
          })}
        </div>
      )}
    </div>
  );
}
