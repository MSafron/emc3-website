from pydantic import BaseModel
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryInDBBase(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class Category(CategoryInDBBase):
    children: List["Category"] = []

class CategoryWithProducts(Category):
    products: List["ProductBase"] = []

# Импорт для forward references
from .products import ProductBase
CategoryWithProducts.model_rebuild()
Category.model_rebuild()