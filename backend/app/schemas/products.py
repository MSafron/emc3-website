from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    sku: str
    price: float
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    country: Optional[str] = None
    power_watts: Optional[int] = None
    luminous_flux: Optional[int] = None
    color_temperature: Optional[int] = None
    manufacturing_time: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    images: Optional[str] = None
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    category_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    country: Optional[str] = None
    power_watts: Optional[int] = None
    luminous_flux: Optional[int] = None
    color_temperature: Optional[int] = None
    manufacturing_time: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    images: Optional[str] = None
    category_id: Optional[int] = None

class ProductInDBBase(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Product(ProductInDBBase):
    pass

class ProductWithCategory(Product):
    category: Optional["Category"] = None

class ProductFilter(BaseModel):
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_power: Optional[int] = None
    max_power: Optional[int] = None
    min_flux: Optional[int] = None
    max_flux: Optional[int] = None
    color_temperature: Optional[int] = None
    manufacturer: Optional[str] = None
    search: Optional[str] = None

class ProductList(BaseModel):
    items: List[Product]
    total: int
    page: int
    size: int
    pages: int

# Импорт для forward references
from .categories import Category
ProductWithCategory.model_rebuild()