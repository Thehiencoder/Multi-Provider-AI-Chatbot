const API_BASE = '/api';

export async function fetchModels() {
  try {
    const res = await fetch(`${API_BASE}/models`);
    if (!res.ok) throw new Error('Failed to fetch models');
    return await res.json();
  } catch (err) {
    console.error('Error fetching models:', err);
    return [];
  }
}

export async function fetchChatHistory(sessionId) {
  try {
    const res = await fetch(`${API_BASE}/chat/${sessionId}/history`);
    if (!res.ok) throw new Error('Failed to fetch chat history');
    const data = await res.json();
    return data.messages || [];
  } catch (err) {
    console.error(`Error fetching history for session ${sessionId}:`, err);
    return [];
  }
}

export async function clearChatHistory(sessionId) {
  try {
    const res = await fetch(`${API_BASE}/chat/${sessionId}`, {
      method: 'DELETE',
    });
    return res.ok;
  } catch (err) {
    console.error(`Error clearing history for session ${sessionId}:`, err);
    return false;
  }
}
