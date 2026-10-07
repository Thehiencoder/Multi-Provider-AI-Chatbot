import React from 'react';
import { MessageSquare, Plus, Bot, Layers, Database } from 'lucide-react';

export default function Sidebar({
  sessions,
  currentSessionId,
  onSelectSession,
  onNewSession,
  providers,
}) {
  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="sidebar-header">
        <div className="brand-logo">
          <Layers size={22} color="#6366f1" />
          <span>LLM Gateway</span>
        </div>
      </div>

      {/* New Session Button */}
      <button className="new-chat-btn" onClick={onNewSession}>
        <Plus size={16} />
        <span>New Conversation</span>
      </button>

      {/* Conversations / Sessions List */}
      <div className="sidebar-section-title">Saved Sessions</div>
      <div className="session-list">
        {sessions.map((sess) => (
          <div
            key={sess}
            className={`session-item ${sess === currentSessionId ? 'active' : ''}`}
            onClick={() => onSelectSession(sess)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflow: 'hidden' }}>
              <MessageSquare size={14} style={{ flexShrink: 0 }} />
              <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                {sess.length > 20 ? `${sess.substring(0, 18)}...` : sess}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Redis & Provider Status Footer */}
      <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Database size={13} color="#10b981" />
          <span>Redis Sliding Window Active</span>
        </div>
        <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.2rem' }}>
          {providers.map(p => (
            <span key={p.provider} style={{ padding: '2px 6px', borderRadius: '4px', background: p.is_available ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)', color: p.is_available ? '#10b981' : '#ef4444' }}>
              {p.provider}: {p.is_available ? 'Ready' : 'Off'}
            </span>
          ))}
        </div>
      </div>
    </aside>
  );
}
