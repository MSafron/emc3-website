import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { ApiResponse, ApiError, HttpStatus } from '@/types';

class ApiClient {
  private client: AxiosInstance;
  private authToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor для добавления токена авторизации
    this.client.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor для обработки ошибок
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error: AxiosError) => {
        const apiError = this.handleError(error);
        return Promise.reject(apiError);
      }
    );
  }

  private handleError(error: AxiosError): ApiError {
    if (error.response) {
      // Сервер ответил с кодом ошибки
      const { status, data } = error.response;
      
      switch (status) {
        case HttpStatus.UNAUTHORIZED:
          this.clearAuthToken();
          return {
            message: 'Необходима авторизация',
            code: 'UNAUTHORIZED',
            details: data,
          };
        case HttpStatus.FORBIDDEN:
          return {
            message: 'Доступ запрещен',
            code: 'FORBIDDEN',
            details: data,
          };
        case HttpStatus.NOT_FOUND:
          return {
            message: 'Ресурс не найден',
            code: 'NOT_FOUND',
            details: data,
          };
        case HttpStatus.UNPROCESSABLE_ENTITY:
          return {
            message: 'Ошибка валидации данных',
            code: 'VALIDATION_ERROR',
            details: data,
          };
        case HttpStatus.INTERNAL_SERVER_ERROR:
          return {
            message: 'Внутренняя ошибка сервера',
            code: 'SERVER_ERROR',
            details: data,
          };
        default:
          return {
            message: (data as any)?.message || 'Произошла ошибка',
            code: 'API_ERROR',
            details: data,
          };
      }
    } else if (error.request) {
      // Запрос был отправлен, но ответ не получен
      return {
        message: 'Сервер недоступен',
        code: 'NETWORK_ERROR',
      };
    } else {
      // Ошибка настройки запроса
      return {
        message: error.message || 'Неизвестная ошибка',
        code: 'REQUEST_ERROR',
      };
    }
  }

  // Методы для работы с токеном авторизации
  setAuthToken(token: string) {
    this.authToken = token;
    localStorage.setItem('auth_token', token);
  }

  clearAuthToken() {
    this.authToken = null;
    localStorage.removeItem('auth_token');
  }

  loadAuthToken() {
    const token = localStorage.getItem('auth_token');
    if (token) {
      this.authToken = token;
    }
  }

  // HTTP методы
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put(url, data);
    return response.data;
  }

  async patch<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.patch(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete(url);
    return response.data;
  }

  // Метод для загрузки файлов
  async upload<T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  }
}

// Создаем единственный экземпляр API клиента
const apiClient = new ApiClient();

// Загружаем токен при инициализации
apiClient.loadAuthToken();

export default apiClient;