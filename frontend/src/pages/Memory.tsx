import { useEffect, useState } from 'react';
import { searchMemory, getMemoryTimeline } from '../api';
import { Search } from 'lucide-react';

export default function Memory() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);

  useEffect(() => {
    getMemoryTimeline().then(setResults).catch(console.error);
  }, []);

  const handleSearch = async () => {
    if (!query) {
      getMemoryTimeline().then(setResults).catch(console.error);
      return;
    }
    const res = await searchMemory(query);
    setResults(res.map((r: any) => r.item));
  };

  return (
    <div>
      <header className="page-header">
        <h1 className="page-title">Memory Vault</h1>
        <p className="page-subtitle">Search Everything</p>
      </header>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <input 
          type="text" 
          value={query} 
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search JAY's memories..."
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          style={{ flex: 1, padding: '1rem', borderRadius: '0.5rem', border: '1px solid var(--border)', background: 'var(--bg-surface)', color: 'white' }}
        />
        <button onClick={handleSearch} style={{ background: 'var(--accent)', color: 'white', padding: '0 1.5rem', borderRadius: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Search size={20} /> Search
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {results.map((mem) => (
          <div key={mem.id} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
               <h3 style={{ fontSize: '1.2rem', color: 'var(--accent-hover)' }}>{mem.title}</h3>
               <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', background: 'var(--bg-main)', padding: '0.2rem 0.5rem', borderRadius: '1rem' }}>
                 {mem.kind}
               </span>
            </div>
            <p style={{ color: 'var(--text-secondary)' }}>{mem.body}</p>
            <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
               Source: {mem.source} | Confidence: {mem.confidence}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
