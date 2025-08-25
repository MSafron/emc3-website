import apiClient from './api';
import {
  Order,
  OrderListResponse,
  OrderFilter,
  CreateOrderRequest,
  CartItem,
  PriceCalculation,
  OrderStatus,
  PaginationParams,
} from '@/types';

class OrderService {
  // Создание заказа
  async createOrder(data: CreateOrderRequest): Promise<Order> {
    return await apiClient.post<Order>('/orders', data);
  }

  // Получение списка заказов пользователя
  async getOrders(params: {
    filters?: OrderFilter;
    pagination?: PaginationParams;
  } = {}): Promise<OrderListResponse> {
    const queryParams = this.buildQueryParams(params);
    return await apiClient.get<OrderListResponse>('/orders', queryParams);
  }

  // Получение заказа по ID
  async getOrder(id: number): Promise<Order> {
    return await apiClient.get<Order>(`/orders/${id}`);
  }

  // Получение заказа по номеру
  async getOrderByNumber(orderNumber: string): Promise<Order> {
    return await apiClient.get<Order>(`/orders/number/${orderNumber}`);
  }

  // Отмена заказа
  async cancelOrder(id: number, reason?: string): Promise<void> {
    await apiClient.post(`/orders/${id}/cancel`, { reason });
  }

  // Повторный заказ
  async reorder(id: number): Promise<Order> {
    return await apiClient.post<Order>(`/orders/${id}/reorder`);
  }

  // Получение истории статусов заказа
  async getOrderHistory(id: number): Promise<Array<{
    status: OrderStatus;
    comment?: string;
    created_at: string;
  }>> {
    return await apiClient.get(`/orders/${id}/history`);
  }

  // Получение документов по заказу
  async getOrderDocuments(id: number): Promise<Array<{
    id: number;
    type: 'invoice' | 'receipt' | 'delivery_note' | 'warranty';
    name: string;
    url: string;
    created_at: string;
  }>> {
    return await apiClient.get(`/orders/${id}/documents`);
  }

  // Скачивание документа
  async downloadDocument(orderId: number, documentId: number): Promise<any> {
    const response = await apiClient.get(
      `/orders/${orderId}/documents/${documentId}/download`
    );
    return response;
  }

  // Расчет стоимости корзины
  async calculateCart(items: Array<{
    product_id: number;
    quantity: number;
  }>): Promise<{
    items: Array<PriceCalculation & { product_id: number }>;
    subtotal: number;
    discount_amount: number;
    discount_percentage: number;
    shipping_cost: number;
    total_amount: number;
  }> {
    return await apiClient.post('/orders/calculate', { items });
  }

  // Проверка доступности товаров для заказа
  async checkCartAvailability(items: Array<{
    product_id: number;
    quantity: number;
  }>): Promise<Array<{
    product_id: number;
    available: boolean;
    in_stock: number;
    requested: number;
    estimated_delivery?: string;
  }>> {
    return await apiClient.post('/orders/check-availability', { items });
  }

  // Получение способов доставки
  async getShippingMethods(data: {
    city: string;
    total_weight?: number;
    total_amount?: number;
  }): Promise<Array<{
    id: number;
    name: string;
    description: string;
    cost: number;
    estimated_days: number;
    is_available: boolean;
  }>> {
    return await apiClient.post('/orders/shipping-methods', data);
  }

  // Получение способов оплаты
  async getPaymentMethods(): Promise<Array<{
    id: string;
    name: string;
    description: string;
    is_available: boolean;
    commission_percentage?: number;
  }>> {
    return await apiClient.get('/orders/payment-methods');
  }

  // Создание черновика заказа для сохранения корзины
  async saveDraft(items: CartItem[]): Promise<{ draft_id: string }> {
    return await apiClient.post('/orders/draft', { items });
  }

  // Загрузка черновика заказа
  async loadDraft(draftId: string): Promise<{ items: CartItem[] }> {
    return await apiClient.get(`/orders/draft/${draftId}`);
  }

  // Удаление черновика
  async deleteDraft(draftId: string): Promise<void> {
    await apiClient.delete(`/orders/draft/${draftId}`);
  }

  // Получение статистики заказов пользователя
  async getOrderStats(): Promise<{
    total_orders: number;
    total_spent: number;
    average_order_value: number;
    last_order_date?: string;
    discount_level: number;
    orders_by_status: Record<OrderStatus, number>;
  }> {
    return await apiClient.get('/orders/stats');
  }

  // Добавление комментария к заказу
  async addComment(id: number, comment: string): Promise<void> {
    await apiClient.post(`/orders/${id}/comment`, { comment });
  }

  // Оценка заказа
  async rateOrder(id: number, data: {
    rating: number;
    comment?: string;
    delivery_rating?: number;
    product_quality_rating?: number;
  }): Promise<void> {
    await apiClient.post(`/orders/${id}/rate`, data);
  }

  // Построение параметров запроса
  private buildQueryParams(params: {
    filters?: OrderFilter;
    pagination?: PaginationParams;
  }): Record<string, any> {
    const queryParams: Record<string, any> = {};

    // Фильтры
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams[key] = value;
        }
      });
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

export const orderService = new OrderService();
export default orderService;