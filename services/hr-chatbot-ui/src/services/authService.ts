import api from './api';
import { LoginRequest, LoginResponse, User } from '../types/auth.types';
import { tokenManager } from '../utils/tokenManager';

export class AuthService {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    // Login via HRMS Mock API
    const response = await api.post<LoginResponse>(
      'http://localhost:8000/api/v1/auth/login',
      {
        email: credentials.email,
        password: credentials.password,
      },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    // Store token and user
    if (response.data.access_token) {
      tokenManager.setToken(response.data.access_token);
      if (response.data.user) {
        tokenManager.setUser(response.data.user);
      }
    }

    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/v1/auth/me');
    return response.data;
  }

  logout(): void {
    tokenManager.clear();
  }

  isAuthenticated(): boolean {
    return !!tokenManager.getToken();
  }

  getToken(): string | null {
    return tokenManager.getToken();
  }

  getUser(): User | null {
    return tokenManager.getUser();
  }
}

export const authService = new AuthService();
