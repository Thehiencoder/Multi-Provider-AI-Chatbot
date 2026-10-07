import React from 'react';
import { Sparkles, Cpu } from 'lucide-react';

export default function ModelSelector({
  providers,
  selectedProvider,
  selectedModel,
  onSelectProvider,
  onSelectModel,
  disabled
}) {
  const currentProviderObj = providers.find((p) => p.provider === selectedProvider);
  const availableModels = currentProviderObj ? currentProviderObj.models : [];

  return (
    <div className="model-selector-group">
      {/* Provider Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
        <Sparkles size={16} color="var(--accent-primary)" />
        <select
          className="select-dropdown"
          value={selectedProvider}
          onChange={(e) => onSelectProvider(e.target.value)}
          disabled={disabled}
        >
          {providers.map((p) => (
            <option key={p.provider} value={p.provider}>
              {p.name} {p.is_available ? '●' : '(No Key)'}
            </option>
          ))}
        </select>
      </div>

      {/* Model Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
        <Cpu size={16} color="var(--accent-secondary)" />
        <select
          className="select-dropdown"
          value={selectedModel}
          onChange={(e) => onSelectModel(e.target.value)}
          disabled={disabled || availableModels.length === 0}
        >
          {availableModels.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
