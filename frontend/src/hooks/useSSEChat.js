import { useState, useRef, useCallback } from 'react';

export function useSSEChat(sessionId, provider, model) {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const sendMessage = useCallback(async (userPrompt, systemPrompt = null) => {
    if (!userPrompt.trim() || isStreaming) return;

    setError(null);
    const userMessage = { role: 'user', content: userPrompt };

    // Optimistically append user message & placeholder assistant message
    setMessages((prev) => [
      ...prev,
      userMessage,
      { role: 'assistant', content: '', isStreaming: true },
    ]);

    setIsStreaming(true);
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          provider: provider,
          model: model,
          messages: [userMessage],
          system_prompt: systemPrompt,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let accumulatedResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete trailing chunk

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith('data:')) continue;

          const dataContent = trimmed.replace(/^data:\s*/, '');
          try {
            const parsed = JSON.parse(dataContent);

            if (parsed.error) {
              setError(parsed.error);
            }

            if (parsed.token) {
              accumulatedResponse += parsed.token;
              setMessages((prev) => {
                const next = [...prev];
                const lastIdx = next.length - 1;
                if (lastIdx >= 0 && next[lastIdx].role === 'assistant') {
                  next[lastIdx] = {
                    ...next[lastIdx],
                    content: accumulatedResponse,
                    isStreaming: true,
                  };
                }
                return next;
              });
            }

            if (parsed.done) {
              // Finalize streaming
              setMessages((prev) => {
                const next = [...prev];
                const lastIdx = next.length - 1;
                if (lastIdx >= 0 && next[lastIdx].role === 'assistant') {
                  next[lastIdx] = {
                    ...next[lastIdx],
                    content: accumulatedResponse,
                    isStreaming: false,
                  };
                }
                return next;
              });
            }
          } catch (jsonErr) {
            console.warn('Failed to parse SSE payload:', dataContent, jsonErr);
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Stream stopped by user.');
      } else {
        console.error('Streaming error:', err);
        setError(err.message || 'An unexpected error occurred during chat.');
      }
      // Remove isStreaming flag from last message
      setMessages((prev) => {
        const next = [...prev];
        const lastIdx = next.length - 1;
        if (lastIdx >= 0 && next[lastIdx].role === 'assistant') {
          next[lastIdx] = { ...next[lastIdx], isStreaming: false };
        }
        return next;
      });
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  }, [sessionId, provider, model, isStreaming]);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  return {
    messages,
    setMessages,
    isStreaming,
    error,
    sendMessage,
    stopGeneration,
  };
}
