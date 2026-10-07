import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User, Sparkles, AlertCircle, Copy, Check } from 'lucide-react';

// Code block with copy button
function CodeBlock({ node, inline, className, children, ...props }) {
  const [copied, setCopied] = React.useState(false);
  const match = /language-(\w+)/.exec(className || '');
  const codeString = String(children).replace(/\n$/, '');

  const handleCopy = () => {
    navigator.clipboard.writeText(codeString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!inline && match) {
    return (
      <div style={{ position: 'relative', margin: '0.75rem 0' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#161e2e',
          padding: '0.35rem 0.75rem',
          borderTopLeftRadius: '6px',
          borderTopRightRadius: '6px',
          fontSize: '0.75rem',
          color: 'var(--text-secondary)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)'
        }}>
          <span>{match[1]}</span>
          <button
            onClick={handleCopy}
            style={{
              background: 'transparent',
              border: 'none',
              color: copied ? '#10b981' : 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '0.75rem'
            }}
          >
            {copied ? <Check size={13} /> : <Copy size={13} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
        <pre style={{ margin: 0, borderTopLeftRadius: 0, borderTopRightRadius: 0 }}>
          <code className={className} {...props}>
            {children}
          </code>
        </pre>
      </div>
    );
  }

  return (
    <code className={className} {...props}>
      {children}
    </code>
  );
}

export default function ChatWindow({
  messages,
  isStreaming,
  error,
  onQuickPromptClick,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  if (messages.length === 0) {
    return (
      <div className="chat-window">
        <div className="welcome-hero">
          <div className="welcome-icon">
            <Sparkles size={32} />
          </div>
          <h2 className="welcome-title">Unified Multi-Provider AI</h2>
          <p style={{ maxWidth: '480px', fontSize: '0.95rem' }}>
            Switch seamlessly between OpenAI, Claude, and Gemini with real-time SSE streaming and sliding window Redis memory.
          </p>

          <div className="quick-prompts">
            <div
              className="quick-prompt-card"
              onClick={() => onQuickPromptClick('Explain how Server-Sent Events (SSE) differ from WebSockets in detail.')}
            >
              🚀 <strong>SSE vs WebSockets</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Compare streaming protocols
              </div>
            </div>
            <div
              className="quick-prompt-card"
              onClick={() => onQuickPromptClick('Write an asynchronous Redis Sliding Window implementation in Python.')}
            >
              ⚡ <strong>Redis Sliding Window</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Memory management algorithm
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      {messages.map((msg, index) => {
        const isUser = msg.role === 'user';
        return (
          <div key={index} className={`message-row ${isUser ? 'user' : 'assistant'}`}>
            <div className={`message-avatar ${isUser ? 'user' : 'assistant'}`}>
              {isUser ? <User size={20} /> : <Bot size={20} />}
            </div>

            <div className="message-bubble">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code: CodeBlock,
                }}
              >
                {msg.content}
              </ReactMarkdown>

              {msg.isStreaming && <span className="stream-cursor" />}
            </div>
          </div>
        );
      })}

      {error && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.85rem 1rem',
          background: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: 'var(--radius-md)',
          color: '#f87171',
          fontSize: '0.9rem'
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
