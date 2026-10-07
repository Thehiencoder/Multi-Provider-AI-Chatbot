import React, { useState, useRef, useEffect } from 'react';
import { Send, Square } from 'lucide-react';

export default function ChatInput({
  onSendMessage,
  onStopGeneration,
  isStreaming,
  disabled
}) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (!isStreaming) {
      textareaRef.current?.focus();
    }
  }, [isStreaming]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (!input.trim() || isStreaming || disabled) return;
    onSendMessage(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleInput = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 150)}px`;
  };

  return (
    <div className="chat-input-container">
      <div className="chat-input-wrapper">
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          placeholder={disabled ? "Provider is unavailable. Check API keys..." : "Type your message here... (Enter to send, Shift+Enter for new line)"}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={disabled}
        />

        {isStreaming ? (
          <button className="stop-btn" onClick={onStopGeneration} title="Stop generating">
            <Square size={16} fill="currentColor" />
          </button>
        ) : (
          <button
            className="send-btn"
            onClick={handleSubmit}
            disabled={!input.trim() || disabled}
            title="Send message"
          >
            <Send size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
