from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.orders import OrderStatus

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    discount_percent: float = 0.0

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    discount_percent: Optional[float] = None

class OrderItemInDBBase(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True

class OrderItem(OrderItemInDBBase):
    total_price: float
    product: Optional["Product"] = None

class OrderBase(BaseModel):
    delivery_address: Optional[str] = None
    delivery_city: Optional[str] = None
    delivery_postal_code: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    delivery_address: Optional[str] = None
    delivery_city: Optional[str] = None
    delivery_postal_code: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    notes: Optional[str] = None

class OrderInDBBase(OrderBase):
    id: int
    user_id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Order(OrderInDBBase):
    order_items: List[OrderItem] = []
    user: Optional["User"] = None

class OrderList(BaseModel):
    items: List[Order]
    total: int
    page: int
    size: int
    pages: int

# B2B Pricing схемы
class PriceCalculation(BaseModel):
    base_price: float
    discount_percent: float
    final_price: float
    quantity: int

class CartItem(BaseModel):
    product_id: int
    quantity: int

class CartCalculation(BaseModel):
    items: List[OrderItem]
    total_amount: float
    total_discount: float

# Импорт для forward references
from .products import Product
from .users import User
Order.model_rebuild()
OrderItem.model_rebuild()