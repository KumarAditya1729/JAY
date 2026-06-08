import { useEffect, useState } from 'react';
import { getIntent } from '../api';

export default function Intent() {
  const [intents, setIntents] = useState<any[]>([]);

  useEffect(() => {
    getIntent()
      .then(setIntents)
      .catch(console.error);
  }, []);

  const groupBy = (key: string) => intents.filter(i => i.kind === key);

  return (
    <div>
      <header className="page-header">
        <h1 className="page-title">Intent Center</h1>
        <p className="page-subtitle">Mission, Values, Goals, and Non-Negotiables</p>
      </header>

      <div className="grid-cols-2">
        <div className="card">
          <h3 style={{ color: 'var(--accent)', marginBottom: '1rem' }}>Mission</h3>
          <ul>
            {groupBy('mission').map(m => <li key={m.id}>{m.statement}</li>)}
          </ul>
        </div>
        <div className="card">
          <h3 style={{ color: 'var(--accent)', marginBottom: '1rem' }}>Values</h3>
          <ul>
            {groupBy('value').map(m => <li key={m.id}>{m.statement}</li>)}
          </ul>
        </div>
        <div className="card">
          <h3 style={{ color: 'var(--accent)', marginBottom: '1rem' }}>Goals</h3>
          <ul>
            {groupBy('goal').map(m => <li key={m.id}>{m.statement}</li>)}
          </ul>
        </div>
        <div className="card">
          <h3 style={{ color: 'var(--danger)', marginBottom: '1rem' }}>Non-Negotiables</h3>
          <ul>
            {groupBy('non_negotiable').map(m => <li key={m.id}>{m.statement}</li>)}
          </ul>
        </div>
      </div>
    </div>
  );
}
