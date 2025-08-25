from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class OrderStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    
    # Адрес доставки
    delivery_address = Column(String)
    delivery_city = Column(String)
    delivery_postal_code = Column(String)
    
    # Контактная информация
    contact_phone = Column(String)
    contact_email = Column(String)
    
    # Комментарии
    notes = Column(String)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # Цена на момент заказа
    discount_percent = Column(Float, default=0.0)  # Примененная скидка
    
    # Связи
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    
    @property
    def total_price(self):
        """Общая стоимость позиции с учетом скидки"""
        base_price = self.quantity * self.unit_price
        discount_amount = base_price * (self.discount_percent / 100)
        return base_price - discount_amount