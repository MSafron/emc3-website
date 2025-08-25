// Форматирование цены
export function formatPrice(
  price: number,
  currency = 'RUB',
  showCurrency = true
): string {
  const formatted = new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(price);

  return showCurrency ? `${formatted} ₽` : formatted;
}

// Форматирование цены с учетом B2B скидки
export function formatPriceWithDiscount(
  originalPrice: number,
  discountedPrice?: number,
  currency = 'RUB'
): { original: string; discounted?: string; savings?: string } {
  const original = formatPrice(originalPrice, currency);
  
  if (!discountedPrice || discountedPrice >= originalPrice) {
    return { original };
  }

  const discounted = formatPrice(discountedPrice, currency);
  const savings = formatPrice(originalPrice - discountedPrice, currency);

  return { original, discounted, savings };
}

// Форматирование процента скидки
export function formatDiscount(percentage: number): string {
  return `${Math.round(percentage)}%`;
}

// Форматирование числа с разделителями тысяч
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('ru-RU').format(num);
}

// Форматирование даты
export function formatDate(
  date: string | Date,
  options: Intl.DateTimeFormatOptions = {}
): string {
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  };

  const formatOptions = { ...defaultOptions, ...options };
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  return new Intl.DateTimeFormat('ru-RU', formatOptions).format(dateObj);
}

// Форматирование относительной даты (например, "2 дня назад")
export function formatRelativeDate(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return 'только что';
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} мин. назад`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} ч. назад`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) {
    return `${diffInDays} дн. назад`;
  }

  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return `${diffInMonths} мес. назад`;
  }

  const diffInYears = Math.floor(diffInMonths / 12);
  return `${diffInYears} г. назад`;
}

// Форматирование размера файла
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Б';

  const k = 1024;
  const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

// Форматирование технических характеристик LED-светильников
export function formatPower(watts: number): string {
  return `${watts} Вт`;
}

export function formatLuminousFlux(lumens: number): string {
  return `${formatNumber(lumens)} лм`;
}

export function formatColorTemperature(kelvin: number): string {
  return `${formatNumber(kelvin)} К`;
}

export function formatBeamAngle(degrees: number): string {
  return `${degrees}°`;
}

export function formatVoltage(voltage: string): string {
  return voltage.includes('В') ? voltage : `${voltage} В`;
}

export function formatDimensions(dimensions: string): string {
  return dimensions;
}

export function formatWeight(grams: number): string {
  if (grams >= 1000) {
    return `${(grams / 1000).toFixed(1)} кг`;
  }
  return `${grams} г`;
}

export function formatWarranty(months: number): string {
  if (months >= 12) {
    const years = Math.floor(months / 12);
    const remainingMonths = months % 12;
    
    if (remainingMonths === 0) {
      return `${years} ${getYearWord(years)}`;
    }
    
    return `${years} ${getYearWord(years)} ${remainingMonths} ${getMonthWord(remainingMonths)}`;
  }
  
  return `${months} ${getMonthWord(months)}`;
}

// Вспомогательные функции для склонения слов
function getYearWord(years: number): string {
  if (years % 10 === 1 && years % 100 !== 11) {
    return 'год';
  } else if ([2, 3, 4].includes(years % 10) && ![12, 13, 14].includes(years % 100)) {
    return 'года';
  } else {
    return 'лет';
  }
}

function getMonthWord(months: number): string {
  if (months % 10 === 1 && months % 100 !== 11) {
    return 'месяц';
  } else if ([2, 3, 4].includes(months % 10) && ![12, 13, 14].includes(months % 100)) {
    return 'месяца';
  } else {
    return 'месяцев';
  }
}

// Форматирование артикула товара
export function formatArticle(article: string): string {
  return article.toUpperCase();
}

// Форматирование телефонного номера
export function formatPhone(phone: string): string {
  const cleaned = phone.replace(/\D/g, '');
  
  if (cleaned.startsWith('7') && cleaned.length === 11) {
    return `+7 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7, 9)}-${cleaned.slice(9)}`;
  }
  
  return phone;
}

// Форматирование процента
export function formatPercentage(value: number, decimals = 0): string {
  return `${value.toFixed(decimals)}%`;
}

export default {
  formatPrice,
  formatPriceWithDiscount,
  formatDiscount,
  formatNumber,
  formatDate,
  formatRelativeDate,
  formatFileSize,
  formatPower,
  formatLuminousFlux,
  formatColorTemperature,
  formatBeamAngle,
  formatVoltage,
  formatDimensions,
  formatWeight,
  formatWarranty,
  formatArticle,
  formatPhone,
  formatPercentage,
};