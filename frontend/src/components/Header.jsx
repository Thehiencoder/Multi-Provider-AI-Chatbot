import React from 'react';
import ModelSelector from './ModelSelector';
import { Trash2, ShieldCheck, ShieldAlert } from 'lucide-react';

export default function Header({
  providers,
  selectedProvider,
  selectedModel,
  onSelectProvider,
  onSelectModel,
  onClearHistory,
  isStreaming,
}) {
  const currentProviderObj = providers.find((p) => p.provider === selectedProvider);
  const isKeyConfigured = currentProviderObj ? currentProviderObj.is_available : false;

  return (
    <header className="chat-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <ModelSelector
          providers={providers}
          selectedProvider={selectedProvider}
          selectedModel={selectedModel}
          onSelectProvider={onSelectProvider}
          onSelectModel={onSelectModel}
          disabled={isStreaming}
        />

        <div className={`provider-badge ${selectedProvider}`}>
          {isKeyConfigured ? (
            <>
              <ShieldCheck size={14} /> Key Active
            </>
          ) : (
            <>
              <ShieldAlert size={14} /> No Key in .env
            </>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <button
          onClick={onClearHistory}
          className="new-chat-btn"
          style={{ width: 'auto', padding: '0.45rem 0.85rem', fontSize: '0.8rem' }}
          title="Clear history for current session"
          disabled={isStreaming}
        >
          <Trash2 size={14} /> Clear Context
        </button>
      </div>
    </header>
  );
}
