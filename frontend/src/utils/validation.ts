// Валидация email
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Валидация пароля
export function validatePassword(password: string): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Пароль должен содержать минимум 8 символов');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Пароль должен содержать хотя бы одну заглавную букву');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Пароль должен содержать хотя бы одну строчную букву');
  }

  if (!/\d/.test(password)) {
    errors.push('Пароль должен содержать хотя бы одну цифру');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

// Валидация телефонного номера
export function validatePhone(phone: string): boolean {
  const phoneRegex = /^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$/;
  return phoneRegex.test(phone.replace(/\s/g, ''));
}

// Валидация имени/названия компании
export function validateName(name: string): boolean {
  return name.trim().length >= 2;
}

// Валидация количества товара
export function validateQuantity(quantity: number, maxQuantity?: number): {
  isValid: boolean;
  error?: string;
} {
  if (quantity <= 0) {
    return {
      isValid: false,
      error: 'Количество должно быть больше 0',
    };
  }

  if (!Number.isInteger(quantity)) {
    return {
      isValid: false,
      error: 'Количество должно быть целым числом',
    };
  }

  if (maxQuantity && quantity > maxQuantity) {
    return {
      isValid: false,
      error: `Максимальное количество: ${maxQuantity}`,
    };
  }

  return { isValid: true };
}

// Валидация цены
export function validatePrice(price: number): boolean {
  return price > 0 && Number.isFinite(price);
}

// Валидация обязательного поля
export function validateRequired(value: any): boolean {
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  return value !== null && value !== undefined;
}

// Валидация минимальной длины
export function validateMinLength(value: string, minLength: number): boolean {
  return value.trim().length >= minLength;
}

// Валидация максимальной длины
export function validateMaxLength(value: string, maxLength: number): boolean {
  return value.length <= maxLength;
}

// Валидация диапазона чисел
export function validateRange(
  value: number,
  min: number,
  max: number
): boolean {
  return value >= min && value <= max;
}

// Валидация ИНН
export function validateINN(inn: string): boolean {
  const innRegex = /^(\d{10}|\d{12})$/;
  if (!innRegex.test(inn)) {
    return false;
  }

  // Проверка контрольных сумм для ИНН
  if (inn.length === 10) {
    const checkDigit = parseInt(inn[9]);
    const sum = [2, 4, 10, 3, 5, 9, 4, 6, 8]
      .reduce((acc, factor, index) => acc + factor * parseInt(inn[index]), 0);
    return (sum % 11) % 10 === checkDigit;
  }

  if (inn.length === 12) {
    const checkDigit1 = parseInt(inn[10]);
    const checkDigit2 = parseInt(inn[11]);
    
    const sum1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
      .reduce((acc, factor, index) => acc + factor * parseInt(inn[index]), 0);
    
    const sum2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
      .reduce((acc, factor, index) => acc + factor * parseInt(inn[index]), 0);

    return (sum1 % 11) % 10 === checkDigit1 && (sum2 % 11) % 10 === checkDigit2;
  }

  return false;
}

// Валидация ОГРН
export function validateOGRN(ogrn: string): boolean {
  const ogrnRegex = /^(\d{13}|\d{15})$/;
  if (!ogrnRegex.test(ogrn)) {
    return false;
  }

  if (ogrn.length === 13) {
    const controlNumber = parseInt(ogrn[12]);
    const mainPart = ogrn.slice(0, 12);
    const remainder = parseInt(mainPart) % 11;
    return remainder % 10 === controlNumber;
  }

  if (ogrn.length === 15) {
    const controlNumber = parseInt(ogrn[14]);
    const mainPart = ogrn.slice(0, 14);
    const remainder = parseInt(mainPart) % 13;
    return remainder % 10 === controlNumber;
  }

  return false;
}

// Валидация адреса
export function validateAddress(address: {
  street?: string;
  city?: string;
  postalCode?: string;
}): {
  isValid: boolean;
  errors: Record<string, string>;
} {
  const errors: Record<string, string> = {};

  if (!address.street || address.street.trim().length < 5) {
    errors.street = 'Укажите корректный адрес улицы';
  }

  if (!address.city || address.city.trim().length < 2) {
    errors.city = 'Укажите корректное название города';
  }

  if (!address.postalCode || !/^\d{6}$/.test(address.postalCode)) {
    errors.postalCode = 'Укажите корректный почтовый индекс (6 цифр)';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

// Общая функция валидации формы
export function validateForm<T extends Record<string, any>>(
  data: T,
  rules: Record<keyof T, Array<(value: any) => string | null>>
): {
  isValid: boolean;
  errors: Record<keyof T, string>;
} {
  const errors: Record<keyof T, string> = {} as Record<keyof T, string>;

  Object.keys(rules).forEach((field) => {
    const fieldRules = rules[field];
    const value = data[field];

    for (const rule of fieldRules) {
      const error = rule(value);
      if (error) {
        errors[field] = error;
        break;
      }
    }
  });

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

// Правила валидации для использования с validateForm
export const validationRules = {
  required: (fieldName: string) => (value: any) =>
    validateRequired(value) ? null : `${fieldName} обязательно для заполнения`,

  email: (value: string) =>
    validateEmail(value) ? null : 'Некорректный формат email',

  phone: (value: string) =>
    validatePhone(value) ? null : 'Некорректный формат телефона',

  minLength: (min: number) => (value: string) =>
    validateMinLength(value, min) ? null : `Минимум ${min} символов`,

  maxLength: (max: number) => (value: string) =>
    validateMaxLength(value, max) ? null : `Максимум ${max} символов`,

  password: (value: string) => {
    const result = validatePassword(value);
    return result.isValid ? null : result.errors[0];
  },

  quantity: (max?: number) => (value: number) => {
    const result = validateQuantity(value, max);
    return result.isValid ? null : result.error!;
  },
};

export default {
  validateEmail,
  validatePassword,
  validatePhone,
  validateName,
  validateQuantity,
  validatePrice,
  validateRequired,
  validateMinLength,
  validateMaxLength,
  validateRange,
  validateINN,
  validateOGRN,
  validateAddress,
  validateForm,
  validationRules,
};