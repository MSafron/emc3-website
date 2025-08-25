export interface Product {
  id: number;
  name: string;
  article: string;
  category_id: number;
  category_name?: string;
  description?: string;
  price: number;
  b2b_price?: number;
  in_stock: boolean;
  stock_quantity: number;
  power: number; // Мощность в Ваттах
  luminous_flux: number; // Световой поток в Люменах
  color_temperature: number; // Цветовая температура в Кельвинах
  beam_angle?: number; // Угол луча в градусах
  ip_rating?: string; // Степень защиты IP
  voltage?: string; // Рабочее напряжение
  dimensions?: string; // Размеры
  weight?: number; // Вес в граммах
  warranty_months: number; // Гарантия в месяцах
  images?: string[]; // Массив URL изображений
  specifications?: ProductSpecification[];
  created_at: string;
  updated_at: string;
}

export interface ProductSpecification {
  id: number;
  product_id: number;
  name: string;
  value: string;
  unit?: string;
}

export interface ProductFilter {
  category_id?: number;
  min_price?: number;
  max_price?: number;
  min_power?: number;
  max_power?: number;
  min_luminous_flux?: number;
  max_luminous_flux?: number;
  color_temperature?: number[];
  ip_rating?: string[];
  in_stock?: boolean;
  search?: string;
}

export interface ProductSortOption {
  field: 'name' | 'price' | 'power' | 'luminous_flux' | 'created_at';
  order: 'asc' | 'desc';
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  parent_id?: number;
  image_url?: string;
  products_count?: number;
  created_at: string;
  updated_at: string;
}

export interface PriceRange {
  min: number;
  max: number;
}

export interface FilterOptions {
  categories: Category[];
  price_range: PriceRange;
  power_range: PriceRange;
  luminous_flux_range: PriceRange;
  color_temperatures: number[];
  ip_ratings: string[];
}