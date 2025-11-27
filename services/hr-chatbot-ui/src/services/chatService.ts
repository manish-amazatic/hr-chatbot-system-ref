import api from './api';
import { Session, Message, ChatRequest, ChatResponse } from '../types/chat.types';
import { tokenManager } from '../utils/tokenManager';

export class ChatService {
  async getSessions(): Promise<Session[]> {
    const response = await api.get<Session[]>('/api/v1/chat/sessions');
    return response.data;
  }

  async getSession(sessionId: string): Promise<Session> {
    const response = await api.get<Session>(`/api/v1/chat/sessions/${sessionId}`);
    return response.data;
  }

  async createSession(request: { user_id?: string; title?: string }): Promise<Session> {
    const response = await api.post<Session>('/api/v1/chat/sessions', request);
    return response.data;
  }

  async deleteSession(sessionId: string): Promise<void> {
    await api.delete(`/api/v1/chat/sessions/${sessionId}`);
  }

  async getMessages(sessionId: string): Promise<Message[]> {
    const response = await api.get<Message[]>(`/api/v1/chat/sessions/${sessionId}/messages`);
    return response.data;
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/api/v1/chat/message', request);
    return response.data;
  }

  async sendMessageStream(
    request: ChatRequest,
    onChunk: (chunk: string) => void,
    onSessionId: (sessionId: string) => void,
    onComplete: (agentUsed: string) => void
  ): Promise<void> {
    // const authHeader = api.defaults.headers.common['Authorization'];
    let authHeader = '';
    const token = tokenManager.getToken();
    if (token ) {
        authHeader = `Bearer ${token}`;
    }
    console.log('Auth Header:', authHeader);
    const response = await fetch(`${api.defaults.baseURL}/api/v1/chat/message/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: authHeader,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No reader available');
    }

    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');

      // Keep the last incomplete line in the buffer
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim();
          if (!data) continue;

          try {
            const parsed = JSON.parse(data);

            if (parsed.type === 'session' && parsed.session_id) {
              onSessionId(parsed.session_id);
            } else if (parsed.type === 'token' && parsed.content) {
              onChunk(parsed.content);
            } else if (parsed.type === 'done') {
              if (parsed.session_id) onSessionId(parsed.session_id);
              if (parsed.agent_used) onComplete(parsed.agent_used);
            } else if (parsed.type === 'error') {
              throw new Error(parsed.content || 'Stream error');
            }
          } catch (e) {
            if (e instanceof Error && e.message !== 'Stream error') {
              console.warn('Failed to parse SSE data:', data);
            } else {
              throw e;
            }
          }
        }
      }
    }
  }
}

export const chatService = new ChatService();
