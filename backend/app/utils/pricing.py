from app.database import settings
from app.schemas.orders import PriceCalculation

def calculate_b2b_discount(quantity: int) -> float:
    """
    Вычисляет процент скидки на основе количества товара
    B2B ценообразование:
    - 5+ шт = -5%
    - 10+ шт = -10% 
    - 50+ шт = -15%
    """
    if quantity >= 50:
        return settings.wholesale_discount_50
    elif quantity >= 10:
        return settings.wholesale_discount_10
    elif quantity >= 5:
        return settings.wholesale_discount_5
    else:
        return 0.0

def calculate_price_with_discount(base_price: float, quantity: int) -> PriceCalculation:
    """
    Вычисляет итоговую цену с учетом B2B скидки
    """
    discount_percent = calculate_b2b_discount(quantity)
    discount_amount = base_price * (discount_percent / 100)
    final_price = base_price - discount_amount
    
    return PriceCalculation(
        base_price=base_price,
        discount_percent=discount_percent,
        final_price=final_price,
        quantity=quantity
    )

def calculate_total_for_item(unit_price: float, quantity: int) -> dict:
    """
    Вычисляет общую стоимость для позиции заказа
    """
    discount_percent = calculate_b2b_discount(quantity)
    base_total = unit_price * quantity
    discount_amount = base_total * (discount_percent / 100)
    final_total = base_total - discount_amount
    
    return {
        "unit_price": unit_price,
        "quantity": quantity,
        "base_total": base_total,
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "final_total": final_total
    }