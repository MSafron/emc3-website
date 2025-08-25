from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sku = Column(String, unique=True, nullable=False, index=True)
    price = Column(Float, nullable=False)
    description = Column(Text)
    manufacturer = Column(String)
    country = Column(String)
    
    # Технические характеристики из CSV
    power_watts = Column(Integer)  # Мощность (Вт)
    luminous_flux = Column(Integer)  # Световой поток (Лм)
    color_temperature = Column(Integer)  # Цветовая температура (К)
    manufacturing_time = Column(String)  # Срок изготовления
    
    # SEO поля
    seo_title = Column(String)
    seo_description = Column(Text)
    seo_keywords = Column(Text)
    
    # Изображения (пока как строка, можно расширить до отдельной таблицы)
    images = Column(Text)
    
    # Связи
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи с заказами
    order_items = relationship("OrderItem", back_populates="product")