export type MessageRole = 'user' | 'assistant';

export type ConnectionStatus = 'connected' | 'connecting' | 'disconnected' | 'error';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  agentUsed?: string;
  isStreaming?: boolean;
}

export interface StreamEvent {
  type: 'token' | 'done' | 'error';
  content?: string;
  session_id?: string;
  agent_used?: string;
  error?: string;
}

export interface ChatResponse {
  response: string;
  sources?: Array<{
    content: string;
    score: number;
    metadata?: Record<string, unknown>;
  }>;
  agent_used?: string;
  timestamp: string;
}
