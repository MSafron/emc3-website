import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { CartItem, Cart, Product, PriceCalculation } from '@/types';
import { orderService } from '@/services';

// Типы для состояния корзины
interface CartState {
  items: CartItem[];
  isLoading: boolean;
  error: string | null;
  totals: {
    subtotal: number;
    discount_amount: number;
    discount_percentage: number;
    total_amount: number;
    total_items: number;
  };
}

// Типы для действий
type CartAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_CART'; payload: CartItem[] }
  | { type: 'ADD_ITEM'; payload: CartItem }
  | { type: 'UPDATE_ITEM'; payload: { id: string; quantity: number } }
  | { type: 'REMOVE_ITEM'; payload: string }
  | { type: 'CLEAR_CART' }
  | { type: 'UPDATE_TOTALS'; payload: CartState['totals'] };

// Интерфейс контекста
interface CartContextType extends CartState {
  addToCart: (product: Product, quantity?: number) => Promise<void>;
  updateQuantity: (itemId: string, quantity: number) => Promise<void>;
  removeFromCart: (itemId: string) => void;
  clearCart: () => void;
  getItemQuantity: (productId: number) => number;
  isInCart: (productId: number) => boolean;
  calculateTotals: () => Promise<void>;
}

// Начальное состояние
const initialState: CartState = {
  items: [],
  isLoading: false,
  error: null,
  totals: {
    subtotal: 0,
    discount_amount: 0,
    discount_percentage: 0,
    total_amount: 0,
    total_items: 0,
  },
};

// Редьюсер для управления состоянием корзины
function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };
    case 'SET_CART':
      return {
        ...state,
        items: action.payload,
        isLoading: false,
        error: null,
      };
    case 'ADD_ITEM': {
      const existingItemIndex = state.items.findIndex(
        item => item.product_id === action.payload.product_id
      );
      
      if (existingItemIndex >= 0) {
        // Товар уже в корзине, увеличиваем количество
        const updatedItems = [...state.items];
        updatedItems[existingItemIndex] = {
          ...updatedItems[existingItemIndex],
          quantity: updatedItems[existingItemIndex].quantity + action.payload.quantity,
          total_price: updatedItems[existingItemIndex].unit_price * 
            (updatedItems[existingItemIndex].quantity + action.payload.quantity),
        };
        return {
          ...state,
          items: updatedItems,
        };
      } else {
        // Новый товар в корзине
        return {
          ...state,
          items: [...state.items, action.payload],
        };
      }
    }
    case 'UPDATE_ITEM': {
      const updatedItems = state.items.map(item => {
        if (item.id === action.payload.id) {
          return {
            ...item,
            quantity: action.payload.quantity,
            total_price: item.unit_price * action.payload.quantity,
          };
        }
        return item;
      });
      return {
        ...state,
        items: updatedItems,
      };
    }
    case 'REMOVE_ITEM':
      return {
        ...state,
        items: state.items.filter(item => item.id !== action.payload),
      };
    case 'CLEAR_CART':
      return {
        ...state,
        items: [],
        totals: initialState.totals,
      };
    case 'UPDATE_TOTALS':
      return {
        ...state,
        totals: action.payload,
      };
    default:
      return state;
  }
}

// Создание контекста
const CartContext = createContext<CartContextType | undefined>(undefined);

// Провайдер контекста
export function CartProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, initialState);

  // Загрузка корзины из localStorage при инициализации
  useEffect(() => {
    loadCartFromStorage();
  }, []);

  // Сохранение корзины в localStorage при изменении
  useEffect(() => {
    if (state.items.length > 0) {
      saveCartToStorage(state.items);
      calculateTotals();
    } else {
      localStorage.removeItem('cart_items');
    }
  }, [state.items]);

  // Загрузка корзины из localStorage
  const loadCartFromStorage = () => {
    try {
      const savedCart = localStorage.getItem('cart_items');
      if (savedCart) {
        const items = JSON.parse(savedCart);
        dispatch({ type: 'SET_CART', payload: items });
      }
    } catch (error) {
      console.error('Error loading cart from storage:', error);
    }
  };

  // Сохранение корзины в localStorage
  const saveCartToStorage = (items: CartItem[]) => {
    try {
      localStorage.setItem('cart_items', JSON.stringify(items));
    } catch (error) {
      console.error('Error saving cart to storage:', error);
    }
  };

  // Добавление товара в корзину
  const addToCart = async (product: Product, quantity = 1) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      const cartItem: CartItem = {
        id: `${product.id}_${Date.now()}`,
        product_id: product.id,
        product: {
          id: product.id,
          name: product.name,
          article: product.article,
          price: product.price,
          b2b_price: product.b2b_price,
          images: product.images,
          in_stock: product.in_stock,
          stock_quantity: product.stock_quantity,
        },
        quantity,
        unit_price: product.b2b_price || product.price,
        total_price: (product.b2b_price || product.price) * quantity,
      };

      dispatch({ type: 'ADD_ITEM', payload: cartItem });
      dispatch({ type: 'SET_LOADING', payload: false });
    } catch (error: any) {
      dispatch({ type: 'SET_ERROR', payload: error.message || 'Ошибка добавления в корзину' });
    }
  };

  // Обновление количества товара
  const updateQuantity = async (itemId: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(itemId);
      return;
    }

    try {
      dispatch({ type: 'UPDATE_ITEM', payload: { id: itemId, quantity } });
    } catch (error: any) {
      dispatch({ type: 'SET_ERROR', payload: error.message || 'Ошибка обновления количества' });
    }
  };

  // Удаление товара из корзины
  const removeFromCart = (itemId: string) => {
    dispatch({ type: 'REMOVE_ITEM', payload: itemId });
  };

  // Очистка корзины
  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' });
    localStorage.removeItem('cart_items');
  };

  // Получение количества конкретного товара в корзине
  const getItemQuantity = (productId: number): number => {
    const items = state.items.filter(item => item.product_id === productId);
    return items.reduce((total, item) => total + item.quantity, 0);
  };

  // Проверка наличия товара в корзине
  const isInCart = (productId: number): boolean => {
    return state.items.some(item => item.product_id === productId);
  };

  // Расчет итогов корзины
  const calculateTotals = async () => {
    try {
      if (state.items.length === 0) {
        dispatch({
          type: 'UPDATE_TOTALS',
          payload: initialState.totals,
        });
        return;
      }

      const items = state.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
      }));

      const calculation = await orderService.calculateCart(items);
      
      dispatch({
        type: 'UPDATE_TOTALS',
        payload: {
          subtotal: calculation.subtotal,
          discount_amount: calculation.discount_amount,
          discount_percentage: calculation.discount_percentage,
          total_amount: calculation.total_amount,
          total_items: state.items.reduce((sum, item) => sum + item.quantity, 0),
        },
      });
    } catch (error) {
      // В случае ошибки расчитываем локально
      const subtotal = state.items.reduce((sum, item) => sum + item.total_price, 0);
      const total_items = state.items.reduce((sum, item) => sum + item.quantity, 0);
      
      dispatch({
        type: 'UPDATE_TOTALS',
        payload: {
          subtotal,
          discount_amount: 0,
          discount_percentage: 0,
          total_amount: subtotal,
          total_items,
        },
      });
    }
  };

  const contextValue: CartContextType = {
    ...state,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    getItemQuantity,
    isInCart,
    calculateTotals,
  };

  return (
    <CartContext.Provider value={contextValue}>
      {children}
    </CartContext.Provider>
  );
}

// Хук для использования контекста
export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}

export default CartContext;