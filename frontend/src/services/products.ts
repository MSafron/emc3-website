import apiClient from './api';
import {
  Product,
  ProductListResponse,
  ProductFilter,
  ProductSortOption,
  Category,
  FilterOptions,
  PaginationParams,
} from '@/types';

class ProductService {
  // Получение списка товаров с фильтрацией и пагинацией
  async getProducts(params: {
    filters?: ProductFilter;
    sort?: ProductSortOption;
    pagination?: PaginationParams;
  } = {}): Promise<ProductListResponse> {
    const queryParams = this.buildQueryParams(params);
    return await apiClient.get<ProductListResponse>('/products', queryParams);
  }

  // Получение товара по ID
  async getProduct(id: number): Promise<Product> {
    return await apiClient.get<Product>(`/products/${id}`);
  }

  // Получение товара по артикулу
  async getProductByArticle(article: string): Promise<Product> {
    return await apiClient.get<Product>(`/products/article/${article}`);
  }

  // Поиск товаров
  async searchProducts(query: string, limit = 10): Promise<Product[]> {
    return await apiClient.get<Product[]>('/products/search', {
      q: query,
      limit,
    });
  }

  // Получение похожих товаров
  async getSimilarProducts(productId: number, limit = 6): Promise<Product[]> {
    return await apiClient.get<Product[]>(`/products/${productId}/similar`, {
      limit,
    });
  }

  // Получение рекомендованных товаров
  async getRecommendedProducts(limit = 8): Promise<Product[]> {
    return await apiClient.get<Product[]>('/products/recommended', {
      limit,
    });
  }

  // Получение новых товаров
  async getNewProducts(limit = 12): Promise<Product[]> {
    return await apiClient.get<Product[]>('/products/new', {
      limit,
    });
  }

  // Получение популярных товаров
  async getPopularProducts(limit = 12): Promise<Product[]> {
    return await apiClient.get<Product[]>('/products/popular', {
      limit,
    });
  }

  // Получение товаров по категории
  async getProductsByCategory(
    categoryId: number,
    params: {
      filters?: Omit<ProductFilter, 'category_id'>;
      sort?: ProductSortOption;
      pagination?: PaginationParams;
    } = {}
  ): Promise<ProductListResponse> {
    const queryParams = this.buildQueryParams({
      ...params,
      filters: { ...params.filters, category_id: categoryId },
    });
    return await apiClient.get<ProductListResponse>('/products', queryParams);
  }

  // Получение категорий
  async getCategories(): Promise<Category[]> {
    return await apiClient.get<Category[]>('/categories');
  }

  // Получение категории по ID
  async getCategory(id: number): Promise<Category> {
    return await apiClient.get<Category>(`/categories/${id}`);
  }

  // Получение дочерних категорий
  async getSubcategories(parentId: number): Promise<Category[]> {
    return await apiClient.get<Category[]>(`/categories/${parentId}/children`);
  }

  // Получение опций для фильтров
  async getFilterOptions(categoryId?: number): Promise<FilterOptions> {
    const params = categoryId ? { category_id: categoryId } : {};
    return await apiClient.get<FilterOptions>('/products/filter-options', params);
  }

  // Получение B2B цены товара
  async getB2BPrice(productId: number, quantity: number): Promise<{
    unit_price: number;
    total_price: number;
    discount_percentage: number;
    discount_amount: number;
  }> {
    return await apiClient.get(`/products/${productId}/b2b-price`, {
      quantity,
    });
  }

  // Получение информации о наличии товара
  async checkAvailability(productId: number, quantity: number): Promise<{
    available: boolean;
    in_stock: number;
    estimated_delivery?: string;
  }> {
    return await apiClient.get(`/products/${productId}/availability`, {
      quantity,
    });
  }

  // Уведомление о поступлении товара
  async subscribeToAvailability(productId: number, email: string): Promise<void> {
    await apiClient.post(`/products/${productId}/notify`, { email });
  }

  // Добавление отзыва о товаре
  async addReview(productId: number, data: {
    rating: number;
    comment: string;
    pros?: string;
    cons?: string;
  }): Promise<void> {
    await apiClient.post(`/products/${productId}/reviews`, data);
  }

  // Получение отзывов о товаре
  async getReviews(productId: number, page = 1, limit = 10): Promise<{
    reviews: Array<{
      id: number;
      rating: number;
      comment: string;
      pros?: string;
      cons?: string;
      user_name: string;
      created_at: string;
    }>;
    total: number;
    average_rating: number;
  }> {
    return await apiClient.get(`/products/${productId}/reviews`, {
      page,
      limit,
    });
  }

  // Построение параметров запроса
  private buildQueryParams(params: {
    filters?: ProductFilter;
    sort?: ProductSortOption;
    pagination?: PaginationParams;
  }): Record<string, any> {
    const queryParams: Record<string, any> = {};

    // Фильтры
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            queryParams[key] = value.join(',');
          } else {
            queryParams[key] = value;
          }
        }
      });
    }

    // Сортировка
    if (params.sort) {
      queryParams.sort_by = params.sort.field;
      queryParams.sort_order = params.sort.order;
    }

    // Пагинация
    if (params.pagination) {
      if (params.pagination.page) {
        queryParams.page = params.pagination.page;
      }
      if (params.pagination.limit) {
        queryParams.limit = params.pagination.limit;
      }
    }

    return queryParams;
  }
}

export const productService = new ProductService();
export default productService;