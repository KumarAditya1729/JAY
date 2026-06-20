export default function AttentionAuditWidget({ attentionAudit }: { attentionAudit: any }) {
  if (!attentionAudit) return null;

  return (
    <section className="card" style={{ marginBottom: '2rem', borderTop: '4px solid #ef4444' }}>
      <h2 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: '#ef4444', marginBottom: '1rem', letterSpacing: '0.05em' }}>Attention OS Audit</h2>
      <div style={{ background: '#3a1c1c', padding: '1.5rem', borderRadius: '0.5rem', borderLeft: '4px solid #f87171' }}>
        <p style={{ fontSize: '0.875rem', color: '#fca5a5', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
          {attentionAudit.audit_text}
        </p>
      </div>
    </section>
  );
}
