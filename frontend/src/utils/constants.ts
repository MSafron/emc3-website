// API конфигурация
export const API_CONFIG = {
  BASE_URL: '/api',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
} as const;

// Роуты приложения
export const ROUTES = {
  HOME: '/',
  CATALOG: '/catalog',
  PRODUCT: '/product',
  CART: '/cart',
  LOGIN: '/login',
  REGISTER: '/register',
  PROFILE: '/profile',
  ORDERS: '/orders',
  SEARCH: '/search',
} as const;

// Настройки пагинации
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [12, 20, 40, 60],
  MAX_VISIBLE_PAGES: 5,
} as const;

// Настройки корзины
export const CART = {
  MAX_QUANTITY: 999,
  MIN_QUANTITY: 1,
  STORAGE_KEY: 'emc3_cart',
  AUTO_SAVE_DELAY: 1000,
} as const;

// B2B скидки
export const B2B_DISCOUNTS = {
  BRONZE: {
    threshold: 50000,
    discount: 5,
    name: 'Бронзовый',
  },
  SILVER: {
    threshold: 100000,
    discount: 10,
    name: 'Серебряный',
  },
  GOLD: {
    threshold: 250000,
    discount: 15,
    name: 'Золотой',
  },
  PLATINUM: {
    threshold: 500000,
    discount: 20,
    name: 'Платиновый',
  },
} as const;

// Количественные скидки
export const QUANTITY_DISCOUNTS = [
  { min: 5, max: 9, discount: 3 },
  { min: 10, max: 49, discount: 5 },
  { min: 50, max: 99, discount: 8 },
  { min: 100, max: 999, discount: 12 },
] as const;

// Статусы заказов с русскими названиями
export const ORDER_STATUSES = {
  pending: 'Ожидает подтверждения',
  confirmed: 'Подтвержден',
  processing: 'В обработке',
  shipped: 'Отправлен',
  delivered: 'Доставлен',
  cancelled: 'Отменен',
  refunded: 'Возвращен',
} as const;

// Статусы оплаты
export const PAYMENT_STATUSES = {
  pending: 'Ожидает оплаты',
  paid: 'Оплачен',
  failed: 'Ошибка оплаты',
  refunded: 'Возвращен',
} as const;

// Способы оплаты
export const PAYMENT_METHODS = {
  cash: 'Наличные',
  bank_transfer: 'Банковский перевод',
  card: 'Банковская карта',
  invoice: 'По счету',
} as const;

// Типы пользователей
export const USER_TYPES = {
  individual: 'Физическое лицо',
  company: 'Юридическое лицо',
  dealer: 'Дилер',
  distributor: 'Дистрибьютор',
} as const;

// Настройки поиска
export const SEARCH = {
  MIN_QUERY_LENGTH: 2,
  DEBOUNCE_DELAY: 300,
  MAX_SUGGESTIONS: 10,
  MAX_RECENT_SEARCHES: 5,
} as const;

// Настройки изображений
export const IMAGES = {
  PLACEHOLDER: '/images/placeholder.jpg',
  QUALITY: 80,
  FORMATS: ['webp', 'jpg', 'png'],
  SIZES: {
    THUMBNAIL: { width: 150, height: 150 },
    CARD: { width: 300, height: 300 },
    DETAIL: { width: 600, height: 600 },
    GALLERY: { width: 800, height: 800 },
  },
} as const;

// Характеристики светильников
export const LED_SPECS = {
  COLOR_TEMPERATURES: [2700, 3000, 4000, 5000, 6500],
  POWER_RANGES: [
    { label: 'до 10 Вт', min: 0, max: 10 },
    { label: '10-25 Вт', min: 10, max: 25 },
    { label: '25-50 Вт', min: 25, max: 50 },
    { label: '50-100 Вт', min: 50, max: 100 },
    { label: 'свыше 100 Вт', min: 100, max: 9999 },
  ],
  IP_RATINGS: ['IP20', 'IP40', 'IP44', 'IP54', 'IP65', 'IP67'],
  BEAM_ANGLES: [15, 24, 36, 60, 90, 120],
} as const;

// Категории товаров
export const PRODUCT_CATEGORIES = {
  INDOOR: 'Внутреннее освещение',
  OUTDOOR: 'Уличное освещение',
  INDUSTRIAL: 'Промышленное освещение',
  ARCHITECTURAL: 'Архитектурное освещение',
  EMERGENCY: 'Аварийное освещение',
  DECORATIVE: 'Декоративное освещение',
} as const;

// Настройки уведомлений
export const NOTIFICATIONS = {
  DEFAULT_DURATION: 5000,
  ERROR_DURATION: 8000,
  SUCCESS_DURATION: 3000,
  MAX_VISIBLE: 5,
} as const;

// Настройки валидации
export const VALIDATION = {
  PASSWORD_MIN_LENGTH: 8,
  NAME_MIN_LENGTH: 2,
  NAME_MAX_LENGTH: 50,
  PHONE_PATTERN: /^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$/,
  EMAIL_PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  INN_PATTERN: /^(\d{10}|\d{12})$/,
  OGRN_PATTERN: /^(\d{13}|\d{15})$/,
} as const;

// Настройки localStorage ключей
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'emc3_auth_token',
  CART_ITEMS: 'emc3_cart_items',
  USER_PREFERENCES: 'emc3_user_preferences',
  RECENT_SEARCHES: 'emc3_recent_searches',
  VIEWED_PRODUCTS: 'emc3_viewed_products',
  THEME: 'emc3_theme',
} as const;

// Настройки производительности
export const PERFORMANCE = {
  LAZY_LOADING_THRESHOLD: 100,
  INFINITE_SCROLL_THRESHOLD: 200,
  DEBOUNCE_DELAY: 300,
  THROTTLE_DELAY: 100,
  IMAGE_LOADING_DELAY: 50,
} as const;

// Текстовые константы
export const MESSAGES = {
  LOADING: 'Загрузка...',
  ERROR_GENERIC: 'Произошла ошибка. Попробуйте еще раз.',
  ERROR_NETWORK: 'Ошибка сети. Проверьте подключение к интернету.',
  ERROR_NOT_FOUND: 'Страница не найдена.',
  ERROR_UNAUTHORIZED: 'Необходима авторизация.',
  SUCCESS_ADDED_TO_CART: 'Товар добавлен в корзину',
  SUCCESS_ORDER_CREATED: 'Заказ успешно создан',
  SUCCESS_PROFILE_UPDATED: 'Профиль обновлен',
  CONFIRM_DELETE: 'Вы уверены, что хотите удалить?',
  CONFIRM_LOGOUT: 'Вы уверены, что хотите выйти?',
} as const;

// Мета-данные для SEO
export const SEO = {
  DEFAULT_TITLE: 'EMC3 - LED освещение для бизнеса',
  DEFAULT_DESCRIPTION: 'Профессиональные LED-светильники для промышленного и коммерческого освещения. Высокое качество, гарантия, B2B цены.',
  DEFAULT_KEYWORDS: 'LED освещение, светодиодные светильники, промышленное освещение, B2B, оптовые цены',
  SITE_NAME: 'EMC3',
} as const;

export default {
  API_CONFIG,
  ROUTES,
  PAGINATION,
  CART,
  B2B_DISCOUNTS,
  QUANTITY_DISCOUNTS,
  ORDER_STATUSES,
  PAYMENT_STATUSES,
  PAYMENT_METHODS,
  USER_TYPES,
  SEARCH,
  IMAGES,
  LED_SPECS,
  PRODUCT_CATEGORIES,
  NOTIFICATIONS,
  VALIDATION,
  STORAGE_KEYS,
  PERFORMANCE,
  MESSAGES,
  SEO,
};