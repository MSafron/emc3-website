export interface User {
  id: number;
  email: string;
  company_name: string;
  contact_person: string;
  phone: string;
  is_active: boolean;
  is_verified: boolean;
  user_type: UserType;
  discount_level: DiscountLevel;
  created_at: string;
  updated_at: string;
}

export enum UserType {
  INDIVIDUAL = 'individual',
  COMPANY = 'company',
  DEALER = 'dealer',
  DISTRIBUTOR = 'distributor'
}

export enum DiscountLevel {
  NONE = 0,
  BRONZE = 5,
  SILVER = 10,
  GOLD = 15,
  PLATINUM = 20
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  company_name: string;
  contact_person: string;
  phone: string;
  user_type: UserType;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

export interface UserProfile {
  id: number;
  email: string;
  company_name: string;
  contact_person: string;
  phone: string;
  user_type: UserType;
  discount_level: DiscountLevel;
  total_orders: number;
  total_spent: number;
  last_order_date?: string;
  address?: Address;
}

export interface Address {
  id?: number;
  street: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
}

export interface UpdateProfileRequest {
  company_name?: string;
  contact_person?: string;
  phone?: string;
  address?: Omit<Address, 'id'>;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
  confirm_password: string;
}