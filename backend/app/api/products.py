from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from app.database import get_db
from app.models import Product, Category
from app.schemas import ProductCreate, ProductUpdate, Product as ProductSchema, ProductList, ProductFilter
from app.utils.pricing import calculate_price_with_discount
import math

router = APIRouter()

@router.get("/", response_model=ProductList)
def get_products(
    skip: int = Query(0, ge=0, description="Количество товаров для пропуска"),
    limit: int = Query(50, ge=1, le=100, description="Количество товаров на странице"),
    category_id: Optional[int] = Query(None, description="ID категории"),
    min_price: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    min_power: Optional[int] = Query(None, ge=0, description="Минимальная мощность (Вт)"),
    max_power: Optional[int] = Query(None, ge=0, description="Максимальная мощность (Вт)"),
    min_flux: Optional[int] = Query(None, ge=0, description="Минимальный световой поток (Лм)"),
    max_flux: Optional[int] = Query(None, ge=0, description="Максимальный световой поток (Лм)"),
    color_temperature: Optional[int] = Query(None, description="Цветовая температура (К)"),
    manufacturer: Optional[str] = Query(None, description="Производитель"),
    search: Optional[str] = Query(None, description="Поиск по названию и артикулу"),
    db: Session = Depends(get_db)
):
    """
    Получить список товаров с фильтрацией и пагинацией
    """
    query = db.query(Product)
    
    # Фильтры
    filters = []
    
    if category_id:
        filters.append(Product.category_id == category_id)
    
    if min_price is not None:
        filters.append(Product.price >= min_price)
    
    if max_price is not None:
        filters.append(Product.price <= max_price)
    
    if min_power is not None:
        filters.append(Product.power_watts >= min_power)
    
    if max_power is not None:
        filters.append(Product.power_watts <= max_power)
    
    if min_flux is not None:
        filters.append(Product.luminous_flux >= min_flux)
    
    if max_flux is not None:
        filters.append(Product.luminous_flux <= max_flux)
    
    if color_temperature:
        filters.append(Product.color_temperature == color_temperature)
    
    if manufacturer:
        filters.append(Product.manufacturer.ilike(f"%{manufacturer}%"))
    
    if search:
        search_filter = or_(
            Product.name.ilike(f"%{search}%"),
            Product.sku.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Общее количество товаров
    total = query.count()
    
    # Применение пагинации
    items = query.offset(skip).limit(limit).all()
    
    # Вычисление метаданных пагинации
    pages = math.ceil(total / limit)
    page = math.floor(skip / limit) + 1
    
    return ProductList(
        items=items,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )

@router.get("/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Получить товар по ID
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product

@router.get("/{product_id}/price")
def get_product_price(
    product_id: int, 
    quantity: int = Query(1, ge=1, description="Количество товара"),
    db: Session = Depends(get_db)
):
    """
    Получить цену товара с учетом B2B скидки
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    price_calculation = calculate_price_with_discount(product.price, quantity)
    return price_calculation

@router.post("/", response_model=ProductSchema)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Создать новый товар
    """
    # Проверка существования артикула
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Товар с таким артикулом уже существует")
    
    # Проверка существования категории
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Категория не найдена")
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    db: Session = Depends(get_db)
):
    """
    Обновить товар
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    # Проверка артикула при обновлении
    if product_update.sku and product_update.sku != product.sku:
        existing_product = db.query(Product).filter(Product.sku == product_update.sku).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="Товар с таким артикулом уже существует")
    
    # Проверка категории при обновлении
    if product_update.category_id:
        category = db.query(Category).filter(Category.id == product_update.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Категория не найдена")
    
    # Обновление полей
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Удалить товар
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    db.delete(product)
    db.commit()
    return {"message": "Товар успешно удален"}