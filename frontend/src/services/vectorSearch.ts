/**
 * Сервис векторного поиска для EMC3 Frontend
 * Интеграция с Supabase Vector Database для умного поиска товаров
 */

import React from 'react';
import apiClient from './api';

export interface SearchResult {
  product_id: number;
  article: string;
  product_name: string;
  category_name: string;
  similarity: number;
  description?: string;
  technical_specs?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface RecommendationResult {
  product_id: number;
  article: string;
  product_name: string;
  similarity: number;
  category_name?: string;
}

export interface SearchFilters {
  category?: string;
  power_min?: number;
  power_max?: number;
  price_min?: number;
  price_max?: number;
  protection_rating?: string;
  installation_area?: string;
}

export interface SearchRequest {
  query: string;
  limit?: number;
  threshold?: number;
  filters?: SearchFilters;
}

export interface SearchAnalytics {
  total_searches: number;
  unique_queries: number;
  average_results: number;
  top_queries: Array<[string, number]>;
  period_days: number;
}

/**
 * Класс для работы с векторным поиском
 */
export class VectorSearchService {
  private static readonly BASE_URL = '/api/search';

  /**
   * Поиск товаров по текстовому запросу
   */
  static async searchProducts(request: SearchRequest): Promise<SearchResult[]> {
    try {
      const response = await apiClient.post(`${this.BASE_URL}/vector`, {
        query: request.query,
        limit: request.limit || 20,
        threshold: request.threshold || 0.7,
        filters: request.filters || {}
      });

      return response.data.results || [];
    } catch (error) {
      console.error('Ошибка векторного поиска:', error);
      throw new Error('Не удалось выполнить поиск товаров');
    }
  }

  /**
   * Быстрый поиск для автодополнения
   */
  static async quickSearch(query: string, limit: number = 10): Promise<SearchResult[]> {
    if (query.length < 2) {
      return [];
    }

    try {
      const response = await apiClient.get(`${this.BASE_URL}/quick`, {
        params: {
          q: query,
          limit
        }
      });

      return response.data.results || [];
    } catch (error) {
      console.error('Ошибка быстрого поиска:', error);
      return [];
    }
  }

  /**
   * Получение рекомендаций для товара
   */
  static async getRecommendations(
    productId: number, 
    limit: number = 10,
    excludeSameCategory: boolean = false
  ): Promise<RecommendationResult[]> {
    try {
      const response = await apiClient.get(`${this.BASE_URL}/recommendations/${productId}`, {
        params: {
          limit,
          exclude_same_category: excludeSameCategory
        }
      });

      return response.data.recommendations || [];
    } catch (error) {
      console.error('Ошибка получения рекомендаций:', error);
      return [];
    }
  }

  /**
   * Поиск товаров по техническим характеристикам
   */
  static async searchBySpecs(
    specs: Record<string, any>, 
    limit: number = 15
  ): Promise<SearchResult[]> {
    try {
      const response = await apiClient.post(`${this.BASE_URL}/by-specs`, {
        technical_specs: specs,
        limit
      });

      return response.data.results || [];
    } catch (error) {
      console.error('Ошибка поиска по характеристикам:', error);
      return [];
    }
  }

  /**
   * Получение популярных поисковых запросов
   */
  static async getPopularQueries(limit: number = 10): Promise<string[]> {
    try {
      const response = await apiClient.get(`${this.BASE_URL}/popular-queries`, {
        params: { limit }
      });

      return response.data.queries || [];
    } catch (error) {
      console.error('Ошибка получения популярных запросов:', error);
      return [];
    }
  }

  /**
   * Логирование клика по результату поиска
   */
  static async logSearchClick(
    query: string, 
    productId: number, 
    position: number
  ): Promise<void> {
    try {
      await apiClient.post(`${this.BASE_URL}/log-click`, {
        query,
        product_id: productId,
        position
      });
    } catch (error) {
      console.error('Ошибка логирования клика:', error);
      // Не блокируем пользователя если логирование не удалось
    }
  }

  /**
   * Получение аналитики поиска (для админов)
   */
  static async getSearchAnalytics(days: number = 30): Promise<SearchAnalytics> {
    try {
      const response = await apiClient.get(`${this.BASE_URL}/analytics`, {
        params: { days }
      });

      return response.data;
    } catch (error) {
      console.error('Ошибка получения аналитики:', error);
      throw error;
    }
  }

  /**
   * Поиск с предложениями исправлений
   */
  static async searchWithSuggestions(query: string): Promise<{
    results: SearchResult[];
    suggestions: string[];
    corrected_query?: string;
  }> {
    try {
      const response = await apiClient.post(`${this.BASE_URL}/smart`, {
        query
      });

      return {
        results: response.data.results || [],
        suggestions: response.data.suggestions || [],
        corrected_query: response.data.corrected_query
      };
    } catch (error) {
      console.error('Ошибка умного поиска:', error);
      throw error;
    }
  }
}

/**
 * Хук для дебаунса поисковых запросов
 */
export function useSearchDebounce<T>(
  value: T,
  delay: number = 500
): T {
  const [debouncedValue, setDebouncedValue] = React.useState<T>(value);

  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Хук для работы с векторным поиском
 */
export function useVectorSearch() {
  const [isSearching, setIsSearching] = React.useState(false);
  const [searchResults, setSearchResults] = React.useState<SearchResult[]>([]);
  const [searchError, setSearchError] = React.useState<string | null>(null);
  const [lastQuery, setLastQuery] = React.useState<string>('');

  const searchProducts = React.useCallback(async (request: SearchRequest) => {
    if (!request.query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    setSearchError(null);
    setLastQuery(request.query);

    try {
      const results = await VectorSearchService.searchProducts(request);
      setSearchResults(results);
    } catch (error) {
      setSearchError(error instanceof Error ? error.message : 'Ошибка поиска');
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  const clearSearch = React.useCallback(() => {
    setSearchResults([]);
    setSearchError(null);
    setLastQuery('');
  }, []);

  return {
    isSearching,
    searchResults,
    searchError,
    lastQuery,
    searchProducts,
    clearSearch
  };
}

/**
 * Хук для получения рекомендаций товаров
 */
export function useProductRecommendations(productId?: number) {
  const [recommendations, setRecommendations] = React.useState<RecommendationResult[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!productId) {
      setRecommendations([]);
      return;
    }

    const fetchRecommendations = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const results = await VectorSearchService.getRecommendations(productId);
        setRecommendations(results);
      } catch (error) {
        setError(error instanceof Error ? error.message : 'Ошибка загрузки рекомендаций');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, [productId]);

  return {
    recommendations,
    isLoading,
    error
  };
}

/**
 * Утилиты для работы с результатами поиска
 */
export class SearchUtils {
  /**
   * Форматирование similarity score для отображения
   */
  static formatSimilarity(similarity: number): string {
    return `${(similarity * 100).toFixed(1)}%`;
  }

  /**
   * Группировка результатов по категориям
   */
  static groupByCategory(results: SearchResult[]): Record<string, SearchResult[]> {
    return results.reduce((groups, result) => {
      const category = result.category_name || 'Без категории';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(result);
      return groups;
    }, {} as Record<string, SearchResult[]>);
  }

  /**
   * Сортировка результатов по релевантности и другим критериям
   */
  static sortResults(
    results: SearchResult[], 
    sortBy: 'similarity' | 'name' | 'category' = 'similarity'
  ): SearchResult[] {
    return [...results].sort((a, b) => {
      switch (sortBy) {
        case 'similarity':
          return b.similarity - a.similarity;
        case 'name':
          return a.product_name.localeCompare(b.product_name);
        case 'category':
          return (a.category_name || '').localeCompare(b.category_name || '');
        default:
          return 0;
      }
    });
  }

  /**
   * Фильтрация результатов по минимальной релевантности
   */
  static filterByRelevance(
    results: SearchResult[], 
    minSimilarity: number = 0.7
  ): SearchResult[] {
    return results.filter(result => result.similarity >= minSimilarity);
  }

  /**
   * Извлечение ключевых слов из поискового запроса
   */
  static extractKeywords(query: string): string[] {
    return query
      .toLowerCase()
      .replace(/[^\w\sа-яё]/gi, ' ')
      .split(/\s+/)
      .filter(word => word.length > 2)
      .filter(word => !['для', 'или', 'как', 'что', 'где', 'когда', 'светильник'].includes(word));
  }

  /**
   * Создание поискового запроса из фильтров
   */
  static buildQueryFromFilters(filters: SearchFilters): string {
    const parts: string[] = [];

    if (filters.category) {
      parts.push(filters.category);
    }

    if (filters.power_min || filters.power_max) {
      if (filters.power_min && filters.power_max) {
        parts.push(`мощность ${filters.power_min}-${filters.power_max} ватт`);
      } else if (filters.power_min) {
        parts.push(`мощность от ${filters.power_min} ватт`);
      } else if (filters.power_max) {
        parts.push(`мощность до ${filters.power_max} ватт`);
      }
    }

    if (filters.protection_rating) {
      parts.push(`защита ${filters.protection_rating}`);
    }

    if (filters.installation_area) {
      parts.push(`для ${filters.installation_area}`);
    }

    return parts.join(' ');
  }
}

export default VectorSearchService;