import api from './api';
import { Session, Message, ChatRequest, ChatResponse } from '../types/chat.types';

export class ChatService {
  async getSessions(): Promise<Session[]> {
    const response = await api.get<Session[]>('/api/v1/chat/sessions');
    return response.data;
  }

  async getSession(sessionId: string): Promise<Session> {
    const response = await api.get<Session>(`/api/v1/chat/sessions/${sessionId}`);
    return response.data;
  }

  async createSession(title?: string): Promise<Session> {
    const response = await api.post<Session>('/api/v1/chat/sessions', { title });
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
    onChunk: (chunk: string) => void
  ): Promise<void> {
    const response = await fetch(`${api.defaults.baseURL}/api/v1/chat/message/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${api.defaults.headers.common['Authorization']}`,
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

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const parsed = JSON.parse(data);
            if (parsed.content) {
              onChunk(parsed.content);
            }
          } catch {
            // Ignore parsing errors
          }
        }
      }
    }
  }
}

export const chatService = new ChatService();
