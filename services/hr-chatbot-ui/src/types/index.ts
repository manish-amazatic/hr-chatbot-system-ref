/**
 * TypeScript type definitions for the HR Chatbot application
 */

// Authentication types
export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  department: string
  designation: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  isLoading: boolean
}

// Chat types
export interface ChatSession {
  id: string
  user_id: string
  title: string
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
  message_count: number
}

export interface ChatMessage {
  id: string
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  sources?: Array<{
    document: string
    chunk: string
    score: number
  }>
  agent_used?: string
  confidence_score?: number
  timestamp: string
}

export interface ChatMessageRequest {
  session_id?: string
  message: string
}

export interface ChatMessageResponse {
  session_id: string
  response: string
  sources?: ChatMessage['sources']
  agent_used?: string
  confidence_score?: number
  message_id: string
}

// API Error types
export interface ApiError {
  detail: string
  status?: number
}
