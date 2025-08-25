from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import math
from app.database import get_db
from app.models import Order, OrderItem, Product, User
from app.models.orders import OrderStatus
from app.schemas import (
    OrderCreate, OrderUpdate, Order as OrderSchema, 
    OrderList, CartItem, CartCalculation
)
from app.utils.auth import get_current_active_user
from app.utils.pricing import calculate_b2b_discount

router = APIRouter()

@router.post("/calculate", response_model=CartCalculation)
def calculate_cart(
    cart_items: List[CartItem],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Рассчитать корзину с B2B скидками
    """
    if not cart_items:
        raise HTTPException(status_code=400, detail="Корзина пуста")
    
    calculated_items = []
    total_amount = 0.0
    total_discount = 0.0
    
    for item in cart_items:
        # Получаем товар
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар с ID {item.product_id} не найден")
        
        # Рассчитываем цену с учетом скидки
        discount_percent = calculate_b2b_discount(item.quantity)
        unit_price = product.price
        base_total = unit_price * item.quantity
        discount_amount = base_total * (discount_percent / 100)
        final_total = base_total - discount_amount
        
        calculated_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "discount_percent": discount_percent,
            "total_price": final_total
        })
        
        total_amount += final_total
        total_discount += discount_amount
    
    return CartCalculation(
        items=calculated_items,
        total_amount=total_amount,
        total_discount=total_discount
    )

@router.post("/", response_model=OrderSchema)
def create_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Создать новый заказ
    """
    if not order.items:
        raise HTTPException(status_code=400, detail="Заказ должен содержать товары")
    
    # Проверяем все товары и рассчитываем общую сумму
    total_amount = 0.0
    order_items_data = []
    
    for item in order.items:
        # Получаем товар
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар с ID {item.product_id} не найден")
        
        # Рассчитываем цену с учетом скидки
        discount_percent = calculate_b2b_discount(item.quantity)
        unit_price = product.price
        base_total = unit_price * item.quantity
        discount_amount = base_total * (discount_percent / 100)
        final_total = base_total - discount_amount
        
        order_items_data.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "discount_percent": discount_percent
        })
        
        total_amount += final_total
    
    # Создаем заказ
    order_data = order.dict()
    del order_data["items"]
    
    db_order = Order(
        **order_data,
        user_id=current_user.id,
        total_amount=total_amount
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Создаем позиции заказа
    for item_data in order_items_data:
        db_order_item = OrderItem(
            **item_data,
            order_id=db_order.id
        )
        db.add(db_order_item)
    
    db.commit()
    db.refresh(db_order)
    
    return db_order

@router.get("/", response_model=OrderList)
def get_orders(
    skip: int = Query(0, ge=0, description="Количество заказов для пропуска"),
    limit: int = Query(20, ge=1, le=100, description="Количество заказов на странице"),
    status: Optional[OrderStatus] = Query(None, description="Фильтр по статусу"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получить список заказов текущего пользователя
    """
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    if status:
        query = query.filter(Order.status == status)
    
    # Сортировка по дате создания (новые сначала)
    query = query.order_by(Order.created_at.desc())
    
    # Общее количество заказов
    total = query.count()
    
    # Применение пагинации
    orders = query.offset(skip).limit(limit).all()
    
    # Вычисление метаданных пагинации
    pages = math.ceil(total / limit) if total > 0 else 1
    page = math.floor(skip / limit) + 1
    
    return OrderList(
        items=orders,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )

@router.get("/{order_id}", response_model=OrderSchema)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получить заказ по ID
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    return order

@router.put("/{order_id}", response_model=OrderSchema)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновить заказ (только определенные поля и статусы)
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    # Проверяем, можно ли изменять заказ
    if order.status in [OrderStatus.shipped, OrderStatus.delivered, OrderStatus.cancelled]:
        raise HTTPException(
            status_code=400,
            detail="Нельзя изменять заказ в статусе 'отправлен', 'доставлен' или 'отменен'"
        )
    
    # Обновляем только разрешенные поля
    update_data = order_update.dict(exclude_unset=True)
    
    # Пользователи могут менять только определенные поля
    allowed_fields = {
        "delivery_address", "delivery_city", "delivery_postal_code",
        "contact_phone", "contact_email", "notes"
    }
    
    # Если пользователь пытается изменить статус, проверяем права
    if "status" in update_data:
        # Пользователи могут только отменять заказы
        if update_data["status"] == OrderStatus.cancelled:
            if order.status not in [OrderStatus.pending, OrderStatus.confirmed]:
                raise HTTPException(
                    status_code=400,
                    detail="Можно отменить только заказы в статусе 'ожидает' или 'подтвержден'"
                )
        else:
            raise HTTPException(
                status_code=403,
                detail="Недостаточно прав для изменения статуса заказа"
            )
    
    # Фильтруем только разрешенные поля
    filtered_updates = {k: v for k, v in update_data.items() 
                       if k in allowed_fields or k == "status"}
    
    # Применяем обновления
    for field, value in filtered_updates.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    return order

@router.delete("/{order_id}")
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Отменить заказ
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    if order.status not in [OrderStatus.pending, OrderStatus.confirmed]:
        raise HTTPException(
            status_code=400,
            detail="Можно отменить только заказы в статусе 'ожидает' или 'подтвержден'"
        )
    
    order.status = OrderStatus.cancelled
    db.commit()
    
    return {"message": "Заказ успешно отменен"}