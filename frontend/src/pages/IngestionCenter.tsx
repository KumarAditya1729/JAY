import { useState, useEffect } from 'react';
import { uploadFile, getIngestionStatus, getPendingReviews, approveReview, rejectReview, editReview, getIngestionAccuracy, getConnectorAudits, syncGithub } from '../api';
import { UploadCloud, CheckCircle, Edit2, XCircle, Box } from 'lucide-react';

export default function IngestionCenter() {
  const [accuracy, setAccuracy] = useState<any>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [audits, setAudits] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [githubRepo, setGithubRepo] = useState('');
  const [syncing, setSyncing] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<any>({});

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      await getIngestionStatus(); // fetch to trigger any side effects if needed
      const acc = await getIngestionAccuracy();
      setAccuracy(acc);
      const revs = await getPendingReviews();
      setReviews(revs);
      const auds = await getConnectorAudits();
      setAudits(auds);
    } catch (e) {
      console.error(e);
    }
  };

  const handleDrop = async (e: any) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      setUploading(true);
      try {
        await uploadFile(files[0]);
        await fetchData();
      } catch (e) {
        console.error("Upload failed", e);
        alert("Upload failed. Check console.");
      }
      setUploading(false);
    }
  };

  const handleSyncGithub = async () => {
    if (!githubRepo) return;
    setSyncing(true);
    try {
      await syncGithub(githubRepo);
      setGithubRepo('');
      await fetchData();
    } catch (e: any) {
      console.error(e);
      alert(e.message || "Sync failed");
    }
    setSyncing(false);
  };

  const handleApprove = async (id: string) => {
    try {
      await approveReview(id);
      await fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleReject = async (id: string) => {
    try {
      await rejectReview(id);
      await fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  const startEditing = (r: any) => {
    setEditingId(r.id);
    setEditForm({
      title: r.payload.title,
      body: r.payload.body,
      kind: r.payload.kind,
      importance: r.payload.importance
    });
  };

  const submitEdit = async (id: string) => {
    try {
      await editReview(id, editForm);
      setEditingId(null);
      await fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="page-container">
      <header className="page-header">
        <h1>Ingestion Center</h1>
        <p>Passive local file and GitHub ingestion to the Memory Core</p>
      </header>

      {/* Accuracy Dashboard */}
      {accuracy && accuracy.total > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h2>Extraction Accuracy Dashboard</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '1rem', marginTop: '1rem' }}>
            <div style={{ padding: '1rem', background: '#1f2937', borderRadius: '0.5rem', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{accuracy.total}</div>
              <div style={{ color: '#9ca3af', fontSize: '0.8rem' }}>Total Extractions</div>
            </div>
            <div style={{ padding: '1rem', background: '#1f2937', borderRadius: '0.5rem', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#34d399' }}>{accuracy.approved_pct}%</div>
              <div style={{ color: '#9ca3af', fontSize: '0.8rem' }}>Approved</div>
            </div>
            <div style={{ padding: '1rem', background: '#1f2937', borderRadius: '0.5rem', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#ef4444' }}>{accuracy.rejected_pct}%</div>
              <div style={{ color: '#9ca3af', fontSize: '0.8rem' }}>Rejected</div>
            </div>
            <div style={{ padding: '1rem', background: '#1f2937', borderRadius: '0.5rem', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#60a5fa' }}>{accuracy.edited_pct}%</div>
              <div style={{ color: '#9ca3af', fontSize: '0.8rem' }}>Edited</div>
            </div>
            <div style={{ padding: '1rem', background: '#1f2937', borderRadius: '0.5rem', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#fbbf24' }}>{accuracy.avg_confidence}</div>
              <div style={{ color: '#9ca3af', fontSize: '0.8rem' }}>Avg Confidence</div>
            </div>
          </div>
        </div>
      )}

      <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        
        {/* Local Files Dropzone */}
        <div className="card" 
             onDragOver={(e) => e.preventDefault()} 
             onDrop={handleDrop}
             style={{ border: '2px dashed #4b5563', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem 2rem', cursor: 'pointer' }}>
          <UploadCloud size={48} style={{ marginBottom: '1rem', color: '#9ca3af' }} />
          <h3>Drag & Drop Files Here</h3>
          <p style={{ color: '#9ca3af', fontSize: '0.9rem', textAlign: 'center', marginTop: '0.5rem' }}>Supports PDF, Markdown, TXT, DOCX</p>
          {uploading && <p style={{ marginTop: '1rem', color: '#60a5fa' }}>Processing & Extracting...</p>}
        </div>

        {/* Cloud Connectors */}
        <div className="card">
          <h2>Cloud Connectors</h2>
          <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ background: '#1f2937', padding: '1.5rem', borderRadius: '0.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <Box size={32} />
              <div style={{ flex: 1 }}>
                <h3>GitHub</h3>
                <p style={{ color: '#9ca3af', fontSize: '0.85rem' }}>Sync commits and issues as Memories</p>
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                  <input 
                    type="text" 
                    placeholder="Owner/Repo (e.g. facebook/react)" 
                    value={githubRepo}
                    onChange={(e) => setGithubRepo(e.target.value)}
                    style={{ flex: 1, padding: '0.5rem', borderRadius: '0.25rem', border: '1px solid #374151', background: '#111827', color: 'white' }}
                  />
                  <button 
                    onClick={handleSyncGithub}
                    disabled={syncing}
                    style={{ background: '#3b82f6', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer' }}>
                    {syncing ? 'Syncing...' : 'Sync'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Connector Audit Trail */}
      {audits.length > 0 && (
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <h2>Connector Audit Trail</h2>
          <p style={{ color: '#9ca3af', fontSize: '0.9rem', marginBottom: '1rem' }}>Log of all third-party cloud connector ingestions.</p>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #374151', color: '#9ca3af' }}>
                  <th style={{ padding: '0.75rem 0' }}>Source</th>
                  <th style={{ padding: '0.75rem 0' }}>Date</th>
                  <th style={{ padding: '0.75rem 0' }}>Imported</th>
                  <th style={{ padding: '0.75rem 0' }}>Rejected</th>
                  <th style={{ padding: '0.75rem 0' }}>Confidence</th>
                  <th style={{ padding: '0.75rem 0' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {audits.map(a => (
                  <tr key={a.id} style={{ borderBottom: '1px solid #1f2937' }}>
                    <td style={{ padding: '0.75rem 0', textTransform: 'capitalize' }}>{a.source} ({a.processing_version})</td>
                    <td style={{ padding: '0.75rem 0' }}>{new Date(a.imported_at).toLocaleString()}</td>
                    <td style={{ padding: '0.75rem 0', color: '#34d399' }}>{a.items_imported}</td>
                    <td style={{ padding: '0.75rem 0', color: '#ef4444' }}>{a.items_rejected}</td>
                    <td style={{ padding: '0.75rem 0' }}>{a.average_confidence}</td>
                    <td style={{ padding: '0.75rem 0' }}>
                      <span style={{ 
                        padding: '0.25rem 0.5rem', 
                        borderRadius: '0.25rem', 
                        fontSize: '0.75rem',
                        background: a.status === 'SUCCESS' ? '#064e3b' : a.status === 'FAILED' ? '#7f1d1d' : '#78350f',
                        color: a.status === 'SUCCESS' ? '#34d399' : a.status === 'FAILED' ? '#f87171' : '#fbbf24'
                      }}>
                        {a.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pending Reviews */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h2>Pending Manual Reviews</h2>
        <p style={{ color: '#9ca3af', fontSize: '0.9rem', marginBottom: '1rem' }}>Low confidence extractions require your approval before joining active memory. Edit, Approve, or Reject.</p>
        
        {reviews.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#9ca3af', background: '#1f2937', borderRadius: '0.5rem' }}>
            <CheckCircle size={32} style={{ margin: '0 auto 1rem', color: '#34d399' }} />
            <p>All clear. No pending reviews.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {reviews.map(r => (
              <div key={r.id} style={{ background: '#1f2937', padding: '1.5rem', borderRadius: '0.5rem' }}>
                
                {editingId === r.id ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <input 
                      value={editForm.title} 
                      onChange={e => setEditForm({...editForm, title: e.target.value})} 
                      style={{ padding: '0.5rem', width: '100%', background: '#111827', color: 'white', border: '1px solid #374151' }} 
                    />
                    <textarea 
                      value={editForm.body} 
                      onChange={e => setEditForm({...editForm, body: e.target.value})} 
                      style={{ padding: '0.5rem', width: '100%', minHeight: '100px', background: '#111827', color: 'white', border: '1px solid #374151' }} 
                    />
                    <div style={{ display: 'flex', gap: '1rem' }}>
                      <select 
                        value={editForm.kind} 
                        onChange={e => setEditForm({...editForm, kind: e.target.value})}
                        style={{ padding: '0.5rem', background: '#111827', color: 'white', border: '1px solid #374151' }}>
                        <option value="idea">Idea</option>
                        <option value="task">Task</option>
                        <option value="decision">Decision</option>
                        <option value="project">Project</option>
                        <option value="person">Person</option>
                        <option value="document">Document</option>
                        <option value="commitment">Commitment</option>
                      </select>
                      <input 
                        type="number" 
                        min="1" max="5" 
                        value={editForm.importance} 
                        onChange={e => setEditForm({...editForm, importance: parseInt(e.target.value)})}
                        style={{ padding: '0.5rem', width: '80px', background: '#111827', color: 'white', border: '1px solid #374151' }} 
                      />
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                      <button onClick={() => submitEdit(r.id)} style={{ background: '#34d399', color: 'black', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}>Save & Approve</button>
                      <button onClick={() => setEditingId(null)} style={{ background: '#4b5563', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer' }}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <span style={{ background: '#fbbf24', color: '#000', padding: '0.2rem 0.5rem', borderRadius: '0.25rem', fontSize: '0.8rem', fontWeight: 'bold' }}>{r.payload.kind.toUpperCase()}</span>
                      <h3 style={{ marginTop: '0.5rem' }}>{r.payload.title}</h3>
                      <p style={{ color: '#d1d5db', marginTop: '0.5rem', fontSize: '0.9rem' }}>{r.payload.body}</p>
                      <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', fontSize: '0.8rem', color: '#9ca3af' }}>
                        <span>Source: {r.payload.source}</span>
                        <span>Confidence: {r.payload.confidence}</span>
                      </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      <button onClick={() => handleApprove(r.id)} style={{ background: '#3b82f6', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <CheckCircle size={16} /> Approve
                      </button>
                      <button onClick={() => startEditing(r)} style={{ background: '#4b5563', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Edit2 size={16} /> Edit
                      </button>
                      <button onClick={() => handleReject(r.id)} style={{ background: '#ef4444', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <XCircle size={16} /> Reject
                      </button>
                    </div>
                  </div>
                )}

              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
