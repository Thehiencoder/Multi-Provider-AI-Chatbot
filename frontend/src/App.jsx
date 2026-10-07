import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { useSSEChat } from './hooks/useSSEChat';
import { fetchModels, fetchChatHistory, clearChatHistory } from './services/api';

function generateSessionId() {
  return `session-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 6)}`;
}

export default function App() {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-4o-mini');

  const [sessions, setSessions] = useState(() => {
    const saved = localStorage.getItem('chatbot_sessions');
    return saved ? JSON.parse(saved) : ['default-session'];
  });

  const [currentSessionId, setCurrentSessionId] = useState(() => {
    const active = localStorage.getItem('chatbot_active_session');
    return active || 'default-session';
  });

  const {
    messages,
    setMessages,
    isStreaming,
    error,
    sendMessage,
    stopGeneration,
  } = useSSEChat(currentSessionId, selectedProvider, selectedModel);

  // 1. Fetch available models from backend
  useEffect(() => {
    async function loadModels() {
      const data = await fetchModels();
      if (data && data.length > 0) {
        setProviders(data);
        // Find first available provider
        const available = data.find((p) => p.is_available) || data[0];
        setSelectedProvider(available.provider);
        if (available.models && available.models.length > 0) {
          setSelectedModel(available.models[0].id);
        }
      }
    }
    loadModels();
  }, []);

  // 2. Load conversation history when switching sessions
  useEffect(() => {
    async function loadHistory() {
      if (!currentSessionId) return;
      const history = await fetchChatHistory(currentSessionId);
      setMessages(history);
    }
    loadHistory();
    localStorage.setItem('chatbot_active_session', currentSessionId);
  }, [currentSessionId]);

  // Sync sessions list to localStorage
  useEffect(() => {
    localStorage.setItem('chatbot_sessions', JSON.stringify(sessions));
  }, [sessions]);

  // Provider change handler
  const handleSelectProvider = (provId) => {
    setSelectedProvider(provId);
    const prov = providers.find((p) => p.provider === provId);
    if (prov && prov.models.length > 0) {
      setSelectedModel(prov.models[0].id);
    }
  };

  // New Chat session
  const handleNewSession = () => {
    const newId = generateSessionId();
    setSessions((prev) => [newId, ...prev]);
    setCurrentSessionId(newId);
    setMessages([]);
  };

  // Select existing session
  const handleSelectSession = (sessId) => {
    if (sessId === currentSessionId) return;
    setCurrentSessionId(sessId);
  };

  // Clear current history
  const handleClearHistory = async () => {
    if (window.confirm('Are you sure you want to clear conversation memory for this session?')) {
      await clearChatHistory(currentSessionId);
      setMessages([]);
    }
  };

  const currentProviderObj = providers.find((p) => p.provider === selectedProvider);
  const isProviderReady = currentProviderObj ? currentProviderObj.is_available : false;

  return (
    <div className="app-container">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        providers={providers}
      />

      <main className="main-chat-area">
        <Header
          providers={providers}
          selectedProvider={selectedProvider}
          selectedModel={selectedModel}
          onSelectProvider={handleSelectProvider}
          onSelectModel={setSelectedModel}
          onClearHistory={handleClearHistory}
          isStreaming={isStreaming}
        />

        <ChatWindow
          messages={messages}
          isStreaming={isStreaming}
          error={error}
          onQuickPromptClick={(prompt) => sendMessage(prompt)}
        />

        <ChatInput
          onSendMessage={sendMessage}
          onStopGeneration={stopGeneration}
          isStreaming={isStreaming}
          disabled={!isProviderReady}
        />
      </main>
    </div>
  );
}
