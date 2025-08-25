import { Address } from './user';

export interface CartItem {
  id: string;
  product_id: number;
  product: {
    id: number;
    name: string;
    article: string;
    price: number;
    b2b_price?: number;
    images?: string[];
    in_stock: boolean;
    stock_quantity: number;
  };
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Cart {
  items: CartItem[];
  total_items: number;
  subtotal: number;
  discount_amount: number;
  discount_percentage: number;
  total_amount: number;
}

export interface Order {
  id: number;
  user_id: number;
  order_number: string;
  status: OrderStatus;
  items: OrderItem[];
  subtotal: number;
  discount_amount: number;
  discount_percentage: number;
  shipping_cost: number;
  total_amount: number;
  shipping_address: Address;
  billing_address?: Address;
  payment_method: PaymentMethod;
  payment_status: PaymentStatus;
  notes?: string;
  created_at: string;
  updated_at: string;
  shipped_at?: string;
  delivered_at?: string;
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  product_name: string;
  product_article: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export enum OrderStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  PROCESSING = 'processing',
  SHIPPED = 'shipped',
  DELIVERED = 'delivered',
  CANCELLED = 'cancelled',
  REFUNDED = 'refunded'
}

export enum PaymentMethod {
  CASH = 'cash',
  BANK_TRANSFER = 'bank_transfer',
  CARD = 'card',
  INVOICE = 'invoice'
}

export enum PaymentStatus {
  PENDING = 'pending',
  PAID = 'paid',
  FAILED = 'failed',
  REFUNDED = 'refunded'
}

export interface CreateOrderRequest {
  items: {
    product_id: number;
    quantity: number;
  }[];
  shipping_address: Omit<Address, 'id'>;
  billing_address?: Omit<Address, 'id'>;
  payment_method: PaymentMethod;
  notes?: string;
}

export interface OrderListResponse {
  orders: Order[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface OrderFilter {
  status?: OrderStatus;
  payment_status?: PaymentStatus;
  date_from?: string;
  date_to?: string;
  search?: string;
}

export interface BulkPricing {
  min_quantity: number;
  max_quantity?: number;
  discount_percentage: number;
}

export interface PriceCalculation {
  unit_price: number;
  quantity: number;
  subtotal: number;
  discount_percentage: number;
  discount_amount: number;
  total: number;
}