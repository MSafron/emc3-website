import { useState, useCallback } from 'react';
import {
  Product,
  ProductListResponse,
  ProductFilter,
  ProductSortOption,
  Category,
  FilterOptions,
  PaginationParams,
} from '@/types';
import { productService } from '@/services';
import { useAsyncState, usePagination } from './useApi';

// Hook для работы со списком товаров
export function useProducts(initialFilters?: ProductFilter) {
  const productsState = useAsyncState<ProductListResponse>();
  const pagination = usePagination(1, 20);
  const [filters, setFilters] = useState<ProductFilter>(initialFilters || {});
  const [sort, setSort] = useState<ProductSortOption>({ field: 'created_at', order: 'desc' });

  const loadProducts = useCallback(async () => {
    const params = {
      filters,
      sort,
      pagination: {
        page: pagination.page,
        limit: pagination.limit,
      },
    };

    const result = await productsState.execute(() => productService.getProducts(params));
    if (result) {
      pagination.setTotal(result.total);
    }
    return result;
  }, [filters, sort, pagination.page, pagination.limit]);

  const updateFilters = useCallback((newFilters: Partial<ProductFilter>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    pagination.reset();
  }, [pagination]);

  const updateSort = useCallback((newSort: ProductSortOption) => {
    setSort(newSort);
    pagination.reset();
  }, [pagination]);

  const clearFilters = useCallback(() => {
    setFilters({});
    pagination.reset();
  }, [pagination]);

  return {
    ...productsState,
    products: productsState.data?.products || [],
    pagination,
    filters,
    sort,
    loadProducts,
    updateFilters,
    updateSort,
    clearFilters,
  };
}

// Hook для работы с отдельным товаром
export function useProduct(productId?: number) {
  const productState = useAsyncState<Product>();
  const similarProductsState = useAsyncState<Product[]>();

  const loadProduct = useCallback(async (id: number) => {
    const result = await productState.execute(() => productService.getProduct(id));
    return result;
  }, []);

  const loadSimilarProducts = useCallback(async (id: number, limit = 6) => {
    const result = await similarProductsState.execute(() => 
      productService.getSimilarProducts(id, limit)
    );
    return result;
  }, []);

  // Автоматическая загрузка товара при инициализации
  const initializeProduct = useCallback(async (id: number) => {
    await loadProduct(id);
    await loadSimilarProducts(id);
  }, [loadProduct, loadSimilarProducts]);

  return {
    product: productState.data,
    similarProducts: similarProductsState.data || [],
    isLoading: productState.isLoading || similarProductsState.isLoading,
    error: productState.error || similarProductsState.error,
    loadProduct,
    loadSimilarProducts,
    initializeProduct,
  };
}

// Hook для работы с категориями
export function useCategories() {
  const categoriesState = useAsyncState<Category[]>();

  const loadCategories = useCallback(async () => {
    const result = await categoriesState.execute(() => productService.getCategories());
    return result;
  }, []);

  const getCategory = useCallback(async (id: number) => {
    const result = await productService.getCategory(id);
    return result;
  }, []);

  const getSubcategories = useCallback(async (parentId: number) => {
    const result = await productService.getSubcategories(parentId);
    return result;
  }, []);

  return {
    ...categoriesState,
    categories: categoriesState.data || [],
    loadCategories,
    getCategory,
    getSubcategories,
  };
}

// Hook для работы с фильтрами товаров
export function useProductFilters(categoryId?: number) {
  const filtersState = useAsyncState<FilterOptions>();

  const loadFilterOptions = useCallback(async () => {
    const result = await filtersState.execute(() => 
      productService.getFilterOptions(categoryId)
    );
    return result;
  }, [categoryId]);

  return {
    ...filtersState,
    filterOptions: filtersState.data,
    loadFilterOptions,
  };
}

// Hook для поиска товаров
export function useProductSearch() {
  const searchState = useAsyncState<Product[]>();
  const [query, setQuery] = useState('');

  const search = useCallback(async (searchQuery: string, limit = 10) => {
    setQuery(searchQuery);
    if (!searchQuery.trim()) {
      searchState.setData([]);
      return [];
    }

    const result = await searchState.execute(() => 
      productService.searchProducts(searchQuery, limit)
    );
    return result;
  }, []);

  const clearSearch = useCallback(() => {
    setQuery('');
    searchState.setData([]);
  }, []);

  return {
    ...searchState,
    results: searchState.data || [],
    query,
    search,
    clearSearch,
  };
}

export default {
  useProducts,
  useProduct,
  useCategories,
  useProductFilters,
  useProductSearch,
};