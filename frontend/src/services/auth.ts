import apiClient from './api';
import {
  User,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  UserProfile,
  UpdateProfileRequest,
  ChangePasswordRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
} from '@/types';

class AuthService {
  // Вход в систему
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', data);
    
    if (response.tokens) {
      apiClient.setAuthToken(response.tokens.access_token);
    }
    
    return response;
  }

  // Регистрация
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    
    if (response.tokens) {
      apiClient.setAuthToken(response.tokens.access_token);
    }
    
    return response;
  }

  // Выход из системы
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      apiClient.clearAuthToken();
    }
  }

  // Обновление токена
  async refreshToken(): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/refresh');
    
    if (response.tokens) {
      apiClient.setAuthToken(response.tokens.access_token);
    }
    
    return response;
  }

  // Получение текущего пользователя
  async getCurrentUser(): Promise<User> {
    return await apiClient.get<User>('/auth/me');
  }

  // Получение профиля пользователя
  async getProfile(): Promise<UserProfile> {
    return await apiClient.get<UserProfile>('/auth/profile');
  }

  // Обновление профиля
  async updateProfile(data: UpdateProfileRequest): Promise<UserProfile> {
    return await apiClient.patch<UserProfile>('/auth/profile', data);
  }

  // Изменение пароля
  async changePassword(data: ChangePasswordRequest): Promise<void> {
    await apiClient.post('/auth/change-password', data);
  }

  // Запрос на восстановление пароля
  async forgotPassword(data: ForgotPasswordRequest): Promise<void> {
    await apiClient.post('/auth/forgot-password', data);
  }

  // Сброс пароля
  async resetPassword(data: ResetPasswordRequest): Promise<void> {
    await apiClient.post('/auth/reset-password', data);
  }

  // Подтверждение email
  async verifyEmail(token: string): Promise<void> {
    await apiClient.post('/auth/verify-email', { token });
  }

  // Повторная отправка письма подтверждения
  async resendVerificationEmail(): Promise<void> {
    await apiClient.post('/auth/resend-verification');
  }

  // Проверка токена
  async validateToken(): Promise<boolean> {
    try {
      await this.getCurrentUser();
      return true;
    } catch {
      return false;
    }
  }

  // Получение B2B статуса пользователя
  async getB2BStatus(): Promise<{
    is_b2b: boolean;
    discount_level: number;
    annual_volume: number;
    next_discount_threshold: number;
  }> {
    return await apiClient.get('/auth/b2b-status');
  }

  // Запрос на получение B2B статуса
  async requestB2BStatus(data: {
    company_registration: string;
    tax_number: string;
    business_description: string;
    annual_volume_estimate: number;
  }): Promise<void> {
    await apiClient.post('/auth/request-b2b', data);
  }
}

export const authService = new AuthService();
export default authService;