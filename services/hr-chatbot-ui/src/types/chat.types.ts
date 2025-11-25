export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sources?: Source[];
  agentUsed?: string;
}

export interface Source {
  documentId: string;
  content: string;
  score: number;
  metadata?: Record<string, any>;
}

export interface Session {
  id: string;
  userId: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, any>;
}

export interface ChatRequest {
  message: string;
  sessionId?: string;
}

export interface ChatResponse {
  session_id: string;
  response: string;
  sources?: Source[];
  agent_used?: string;
  timestamp: string;
}

export interface ChatContextType {
  sessions: Session[];
  currentSession: Session | null;
  messages: Message[];
  isLoading: boolean;
  createSession: () => Promise<void>;
  selectSession: (sessionId: string) => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
  sendMessage: (message: string, useStreaming?: boolean) => Promise<void>;
  loadSessions: () => Promise<void>;
  setCurrentSession: (session: Session | null) => void;
  setMessages: (messages: Message[]) => void;
}
