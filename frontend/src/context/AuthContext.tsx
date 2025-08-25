import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { User, LoginRequest, RegisterRequest, AuthResponse } from '@/types';
import { authService } from '@/services';

// Типы для состояния авторизации
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Типы для действий
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: User }
  | { type: 'AUTH_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'UPDATE_USER'; payload: User };

// Интерфейс контекста
interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  refreshUser: () => Promise<void>;
}

// Начальное состояние
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

// Редьюсер для управления состоянием
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    case 'AUTH_ERROR':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };
    case 'LOGOUT':
      return {
        ...initialState,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
}

// Создание контекста
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Провайдер контекста
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Проверка токена при загрузке приложения
  useEffect(() => {
    checkAuthToken();
  }, []);

  // Проверка действительности токена
  const checkAuthToken = async () => {
    try {
      dispatch({ type: 'AUTH_START' });
      const isValid = await authService.validateToken();
      
      if (isValid) {
        const user = await authService.getCurrentUser();
        dispatch({ type: 'AUTH_SUCCESS', payload: user });
      } else {
        dispatch({ type: 'LOGOUT' });
      }
    } catch (error) {
      dispatch({ type: 'LOGOUT' });
    }
  };

  // Вход в систему
  const login = async (credentials: LoginRequest) => {
    try {
      dispatch({ type: 'AUTH_START' });
      const response: AuthResponse = await authService.login(credentials);
      dispatch({ type: 'AUTH_SUCCESS', payload: response.user });
    } catch (error: any) {
      dispatch({ type: 'AUTH_ERROR', payload: error.message || 'Ошибка входа в систему' });
      throw error;
    }
  };

  // Регистрация
  const register = async (data: RegisterRequest) => {
    try {
      dispatch({ type: 'AUTH_START' });
      const response: AuthResponse = await authService.register(data);
      dispatch({ type: 'AUTH_SUCCESS', payload: response.user });
    } catch (error: any) {
      dispatch({ type: 'AUTH_ERROR', payload: error.message || 'Ошибка регистрации' });
      throw error;
    }
  };

  // Выход из системы
  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      // Игнорируем ошибки при выходе
    } finally {
      dispatch({ type: 'LOGOUT' });
    }
  };

  // Очистка ошибки
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Обновление данных пользователя
  const refreshUser = async () => {
    try {
      const user = await authService.getCurrentUser();
      dispatch({ type: 'UPDATE_USER', payload: user });
    } catch (error) {
      // Если не удалось обновить данные пользователя, выходим
      dispatch({ type: 'LOGOUT' });
    }
  };

  const contextValue: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    clearError,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Хук для использования контекста
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;