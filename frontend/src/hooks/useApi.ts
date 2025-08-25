import { useState, useCallback } from 'react';
import { AsyncState, MutationState } from '@/types';

// Hook для асинхронных запросов с состоянием загрузки
export function useAsyncState<T>(initialData: T | null = null): AsyncState<T> & {
  setData: (data: T | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  execute: (asyncFn: () => Promise<T>) => Promise<T | undefined>;
} {
  const [data, setData] = useState<T | null>(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setLoading = useCallback((loading: boolean) => {
    setIsLoading(loading);
  }, []);

  const setErrorState = useCallback((error: string | null) => {
    setError(error);
  }, []);

  const execute = useCallback(async (asyncFn: () => Promise<T>) => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await asyncFn();
      setData(result);
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'Произошла ошибка';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    data,
    isLoading,
    error,
    setData,
    setLoading,
    setError: setErrorState,
    execute,
  };
}

// Hook для мутаций (создание, обновление, удаление)
export function useMutation<T = any, P = any>(): MutationState & {
  execute: (asyncFn: (params: P) => Promise<T>) => (params: P) => Promise<T | undefined>;
  reset: () => void;
} {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const execute = useCallback((asyncFn: (params: P) => Promise<T>) => {
    return async (params: P) => {
      try {
        setIsLoading(true);
        setError(null);
        setIsSuccess(false);
        const result = await asyncFn(params);
        setIsSuccess(true);
        return result;
      } catch (err: any) {
        const errorMessage = err.message || 'Произошла ошибка';
        setError(errorMessage);
        throw err;
      } finally {
        setIsLoading(false);
      }
    };
  }, []);

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setIsSuccess(false);
  }, []);

  return {
    isLoading,
    error,
    isSuccess,
    execute,
    reset,
  };
}

// Hook для работы с пагинацией
export function usePagination(initialPage = 1, initialLimit = 20) {
  const [page, setPage] = useState(initialPage);
  const [limit, setLimit] = useState(initialLimit);
  const [total, setTotal] = useState(0);

  const totalPages = Math.ceil(total / limit);
  const hasNextPage = page < totalPages;
  const hasPrevPage = page > 1;

  const nextPage = useCallback(() => {
    if (hasNextPage) {
      setPage(prev => prev + 1);
    }
  }, [hasNextPage]);

  const prevPage = useCallback(() => {
    if (hasPrevPage) {
      setPage(prev => prev - 1);
    }
  }, [hasPrevPage]);

  const goToPage = useCallback((pageNumber: number) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setPage(pageNumber);
    }
  }, [totalPages]);

  const reset = useCallback(() => {
    setPage(initialPage);
    setTotal(0);
  }, [initialPage]);

  return {
    page,
    limit,
    total,
    totalPages,
    hasNextPage,
    hasPrevPage,
    setPage,
    setLimit,
    setTotal,
    nextPage,
    prevPage,
    goToPage,
    reset,
  };
}

// Hook для debounce
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  const updateDebouncedValue = useCallback(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  // Эмуляция useEffect
  if (typeof window !== 'undefined') {
    updateDebouncedValue();
  }

  return debouncedValue;
}

// Hook для локального хранилища
export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T) => void, () => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key]);

  const removeValue = useCallback(() => {
    try {
      setStoredValue(initialValue);
      window.localStorage.removeItem(key);
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}

export default {
  useAsyncState,
  useMutation,
  usePagination,
  useDebounce,
  useLocalStorage,
};