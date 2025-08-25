export * from './format';
export * from './validation';
export * from './constants';

// Дополнительные утилитарные функции
export function clsx(...args: (string | undefined | null | boolean)[]): string {
  return args.filter(Boolean).join(' ');
}

export function generateId(): string {
  return Math.random().toString(36).substr(2, 9);
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: any;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

export function scrollToTop(): void {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
}

export function copyToClipboard(text: string): Promise<boolean> {
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text)
      .then(() => true)
      .catch(() => false);
  }
  
  // Fallback для старых браузеров
  const textArea = document.createElement('textarea');
  textArea.value = text;
  document.body.appendChild(textArea);
  textArea.select();
  
  try {
    document.execCommand('copy');
    document.body.removeChild(textArea);
    return Promise.resolve(true);
  } catch {
    document.body.removeChild(textArea);
    return Promise.resolve(false);
  }
}

export function downloadFile(url: string, filename: string): void {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function getImageUrl(
  path?: string,
  size: 'thumbnail' | 'card' | 'detail' | 'gallery' = 'card'
): string {
  if (!path) {
    return '/images/placeholder.jpg';
  }
  
  // Если путь уже полный URL, возвращаем как есть
  if (path.startsWith('http')) {
    return path;
  }
  
  // Добавляем размер к пути изображения
  const pathParts = path.split('.');
  const extension = pathParts.pop();
  const basePath = pathParts.join('.');
  
  return `/images/${basePath}_${size}.${extension}`;
}

export function pluralize(
  count: number,
  one: string,
  few: string,
  many: string
): string {
  const lastDigit = count % 10;
  const lastTwoDigits = count % 100;
  
  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) {
    return many;
  }
  
  if (lastDigit === 1) {
    return one;
  }
  
  if (lastDigit >= 2 && lastDigit <= 4) {
    return few;
  }
  
  return many;
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function isEmptyObject(obj: object): boolean {
  return Object.keys(obj).length === 0;
}

export function omit<T extends Record<string, any>, K extends keyof T>(
  obj: T,
  keys: K[]
): Omit<T, K> {
  const result = { ...obj };
  keys.forEach(key => delete result[key]);
  return result;
}

export function pick<T extends Record<string, any>, K extends keyof T>(
  obj: T,
  keys: K[]
): Pick<T, K> {
  const result = {} as Pick<T, K>;
  keys.forEach(key => {
    if (key in obj) {
      result[key] = obj[key];
    }
  });
  return result;
}

export default {
  clsx,
  generateId,
  debounce,
  throttle,
  scrollToTop,
  copyToClipboard,
  downloadFile,
  getImageUrl,
  pluralize,
  sleep,
  isEmptyObject,
  omit,
  pick,
};