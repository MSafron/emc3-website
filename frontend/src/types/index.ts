export * from './api';
export * from './product';
export * from './user';
export * from './order';

// Общие типы для компонентов
export interface ComponentProps {
  className?: string;
  children?: any;
}

export interface ModalProps extends ComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
}

export interface FormProps extends ComponentProps {
  onSubmit: (data: any) => void;
  isLoading?: boolean;
  error?: string;
}

export interface ButtonProps extends ComponentProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export interface InputProps extends ComponentProps {
  name: string;
  label?: string;
  placeholder?: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  value?: string | number;
  defaultValue?: string | number;
  onChange?: (value: string) => void;
  error?: string;
  required?: boolean;
  disabled?: boolean;
}

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends ComponentProps {
  name: string;
  label?: string;
  placeholder?: string;
  options: SelectOption[];
  value?: string | number;
  defaultValue?: string | number;
  onChange?: (value: string | number) => void;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  multiple?: boolean;
}

// Типы для навигации
export interface NavItem {
  label: string;
  href: string;
  icon?: any;
  children?: NavItem[];
  active?: boolean;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

// Типы для уведомлений
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
}

// Типы для темы
export interface Theme {
  mode: 'light' | 'dark';
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    error: string;
    warning: string;
    success: string;
    info: string;
  };
}

// Утилитарные типы
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};