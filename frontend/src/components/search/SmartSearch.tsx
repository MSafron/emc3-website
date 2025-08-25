/**
 * Компонент умного поиска с векторным поиском
 * Использует Supabase Vector Database для релевантных результатов
 */

import React, { useState, useEffect, useRef } from 'react';
import { SearchResult, VectorSearchService, SearchFilters } from '@/services/vectorSearch';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface SmartSearchProps {
  onResultSelect?: (result: SearchResult) => void;
  placeholder?: string;
  showFilters?: boolean;
  autoFocus?: boolean;
  className?: string;
}

interface SearchState {
  query: string;
  results: SearchResult[];
  isLoading: boolean;
  isOpen: boolean;
  error: string | null;
  filters: SearchFilters;
}

export const SmartSearch: React.FC<SmartSearchProps> = ({
  onResultSelect,
  placeholder = "Поиск светильников по описанию...",
  showFilters = false,
  autoFocus = false,
  className = ""
}) => {
  const [state, setState] = useState<SearchState>({
    query: '',
    results: [],
    isLoading: false,
    isOpen: false,
    error: null,
    filters: {}
  });

  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout>();

  // Дебаунс поиска
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (state.query.length < 2) {
      setState(prev => ({ ...prev, results: [], isOpen: false }));
      return;
    }

    searchTimeoutRef.current = setTimeout(() => {
      performSearch();
    }, 500);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [state.query, state.filters]);

  // Закрытие при клике вне компонента
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setState(prev => ({ ...prev, isOpen: false }));
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Автофокус
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  const performSearch = async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const results = await VectorSearchService.searchProducts({
        query: state.query,
        limit: 10,
        threshold: 0.6,
        filters: state.filters
      });

      setState(prev => ({
        ...prev,
        results,
        isLoading: false,
        isOpen: true
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Ошибка поиска',
        isLoading: false,
        results: []
      }));
    }
  };

  const handleInputChange = (value: string) => {
    setState(prev => ({ ...prev, query: value }));
  };

  const handleResultClick = async (result: SearchResult, index: number) => {
    // Логируем клик для аналитики
    try {
      await VectorSearchService.logSearchClick(state.query, result.product_id, index);
    } catch (error) {
      console.warn('Не удалось залогировать клик:', error);
    }

    // Вызываем callback
    if (onResultSelect) {
      onResultSelect(result);
    }

    // Закрываем поиск
    setState(prev => ({ ...prev, isOpen: false }));
  };

  const clearSearch = () => {
    setState(prev => ({
      ...prev,
      query: '',
      results: [],
      isOpen: false,
      error: null
    }));
  };

  const updateFilters = (newFilters: Partial<SearchFilters>) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, ...newFilters }
    }));
  };

  const formatSimilarity = (similarity: number): string => {
    return `${(similarity * 100).toFixed(1)}%`;
  };

  const highlightQuery = (text: string, query: string): string => {
    if (!query) return text;
    
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
  };

  return (
    <div ref={searchRef} className={`relative ${className}`}>
      {/* Основное поле поиска */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
        </div>
        
        <input
          ref={inputRef}
          type="text"
          value={state.query}
          onChange={(e) => handleInputChange(e.target.value)}
          placeholder={placeholder}
          className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg 
                   focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
                   placeholder-gray-400 text-gray-900 bg-white"
          autoComplete="off"
          onFocus={() => {
            if (state.results.length > 0) {
              setState(prev => ({ ...prev, isOpen: true }));
            }
          }}
        />
        
        {state.query && (
          <button
            onClick={clearSearch}
            className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-gray-600"
          >
            <XMarkIcon className="h-5 w-5 text-gray-400" />
          </button>
        )}

        {state.isLoading && (
          <div className="absolute inset-y-0 right-8 flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>

      {/* Фильтры */}
      {showFilters && (
        <div className="mt-2 flex flex-wrap gap-2">
          <select
            value={state.filters.category || ''}
            onChange={(e) => updateFilters({ category: e.target.value || undefined })}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
          >
            <option value="">Все категории</option>
            <option value="Офисные светильники">Офисные</option>
            <option value="Промышленные светильники">Промышленные</option>
            <option value="Уличные светильники">Уличные</option>
            <option value="Архитектурные светильники">Архитектурные</option>
          </select>

          <input
            type="number"
            placeholder="Мощность от"
            value={state.filters.power_min || ''}
            onChange={(e) => updateFilters({ power_min: e.target.value ? Number(e.target.value) : undefined })}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm w-24"
          />

          <input
            type="number"
            placeholder="Мощность до"
            value={state.filters.power_max || ''}
            onChange={(e) => updateFilters({ power_max: e.target.value ? Number(e.target.value) : undefined })}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm w-24"
          />

          <select
            value={state.filters.protection_rating || ''}
            onChange={(e) => updateFilters({ protection_rating: e.target.value || undefined })}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
          >
            <option value="">Любая защита</option>
            <option value="IP20">IP20</option>
            <option value="IP40">IP40</option>
            <option value="IP54">IP54</option>
            <option value="IP65">IP65</option>
            <option value="IP67">IP67</option>
          </select>
        </div>
      )}

      {/* Результаты поиска */}
      {state.isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 
                      rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
          
          {state.error && (
            <div className="p-4 text-red-600 text-sm border-b">
              <p>Ошибка поиска: {state.error}</p>
            </div>
          )}

          {state.results.length === 0 && !state.isLoading && !state.error && state.query.length >= 2 && (
            <div className="p-4 text-gray-500 text-sm text-center">
              <p>По запросу "{state.query}" ничего не найдено</p>
              <p className="mt-1">Попробуйте изменить поисковый запрос</p>
            </div>
          )}

          {state.results.map((result, index) => (
            <div
              key={`${result.product_id}-${index}`}
              onClick={() => handleResultClick(result, index)}
              className="p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer 
                       transition-colors duration-150"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h4 
                    className="font-medium text-gray-900 truncate"
                    dangerouslySetInnerHTML={{ 
                      __html: highlightQuery(result.product_name, state.query) 
                    }}
                  />
                  
                  <div className="flex items-center mt-1 space-x-3 text-sm text-gray-500">
                    <span>{result.article}</span>
                    <span>•</span>
                    <span>{result.category_name}</span>
                  </div>

                  {result.description && (
                    <p 
                      className="mt-1 text-sm text-gray-600 line-clamp-2"
                      dangerouslySetInnerHTML={{ 
                        __html: highlightQuery(result.description, state.query) 
                      }}
                    />
                  )}

                  {/* Технические характеристики */}
                  {result.technical_specs && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {result.technical_specs.power && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs 
                                       bg-blue-100 text-blue-800">
                          {result.technical_specs.power} Вт
                        </span>
                      )}
                      {result.technical_specs.luminous_flux && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs 
                                       bg-green-100 text-green-800">
                          {result.technical_specs.luminous_flux} лм
                        </span>
                      )}
                      {result.technical_specs.color_temperature && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs 
                                       bg-yellow-100 text-yellow-800">
                          {result.technical_specs.color_temperature} К
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <div className="ml-4 flex-shrink-0">
                  <div className="text-xs text-blue-600 font-medium">
                    {formatSimilarity(result.similarity)}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Футер с дополнительными действиями */}
          {state.results.length > 0 && (
            <div className="p-3 bg-gray-50 border-t">
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>Найдено {state.results.length} результатов</span>
                <button
                  onClick={() => {
                    // Можно добавить переход к полной странице результатов
                    console.log('Показать все результаты');
                  }}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  Показать все →
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SmartSearch;