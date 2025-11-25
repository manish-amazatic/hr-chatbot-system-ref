/**
 * API Service
 * Handles all HTTP requests to the backend
 */
import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  LoginRequest,
  LoginResponse,
  ChatSession,
  ChatMessage,
  ChatMessageRequest,
  ChatMessageResponse,
  ApiError,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor to handle errors
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        if (error.response?.status === 401) {
          // Clear token and redirect to login
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // ==================== Authentication ====================

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.api.post<LoginResponse>('/auth/login', credentials)
    return response.data
  }

  async refreshToken(token: string): Promise<LoginResponse> {
    const response = await this.api.post<LoginResponse>('/auth/refresh', { token })
    return response.data
  }

  // ==================== Chat Sessions ====================

  async getSessions(): Promise<ChatSession[]> {
    const response = await this.api.get<ChatSession[]>('/chat/sessions')
    return response.data
  }

  async getSession(sessionId: string): Promise<ChatSession> {
    const response = await this.api.get<ChatSession>(`/chat/sessions/${sessionId}`)
    return response.data
  }

  async createSession(title?: string): Promise<ChatSession> {
    const response = await this.api.post<ChatSession>('/chat/sessions', { title })
    return response.data
  }

  async updateSessionTitle(sessionId: string, title: string): Promise<ChatSession> {
    const response = await this.api.put<ChatSession>(
      `/chat/sessions/${sessionId}`,
      { title }
    )
    return response.data
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.api.delete(`/chat/sessions/${sessionId}`)
  }

  // ==================== Chat Messages ====================

  async getMessages(sessionId: string): Promise<ChatMessage[]> {
    const response = await this.api.get<ChatMessage[]>(
      `/chat/sessions/${sessionId}/messages`
    )
    return response.data
  }

  async sendMessage(request: ChatMessageRequest): Promise<ChatMessageResponse> {
    const response = await this.api.post<ChatMessageResponse>('/chat/message', request)
    return response.data
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.api.get('/health')
    return response.data
  }
}

// Export singleton instance
export const apiService = new ApiService()
export default apiService
