from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate, Category as CategorySchema

router = APIRouter()

def build_category_tree(categories: List[Category]) -> List[CategorySchema]:
    """
    Построить дерево категорий из плоского списка
    """
    category_dict = {cat.id: CategorySchema.from_orm(cat) for cat in categories}
    
    # Инициализируем children для всех категорий
    for cat in category_dict.values():
        cat.children = []
    
    root_categories = []
    
    for cat in category_dict.values():
        if cat.parent_id is None:
            root_categories.append(cat)
        else:
            if cat.parent_id in category_dict:
                category_dict[cat.parent_id].children.append(cat)
    
    return root_categories

@router.get("/", response_model=List[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    """
    Получить иерархию категорий
    """
    categories = db.query(Category).all()
    return build_category_tree(categories)

@router.get("/flat", response_model=List[CategorySchema])
def get_categories_flat(db: Session = Depends(get_db)):
    """
    Получить плоский список всех категорий
    """
    categories = db.query(Category).all()
    return categories

@router.get("/{category_id}", response_model=CategorySchema)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Получить категорию по ID
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category

@router.get("/{category_id}/children", response_model=List[CategorySchema])
def get_category_children(category_id: int, db: Session = Depends(get_db)):
    """
    Получить дочерние категории
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    children = db.query(Category).filter(Category.parent_id == category_id).all()
    return children

@router.post("/", response_model=CategorySchema)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Создать новую категорию
    """
    # Проверка существования slug
    existing_category = db.query(Category).filter(Category.slug == category.slug).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Категория с таким slug уже существует")
    
    # Проверка существования родительской категории
    if category.parent_id:
        parent_category = db.query(Category).filter(Category.id == category.parent_id).first()
        if not parent_category:
            raise HTTPException(status_code=400, detail="Родительская категория не найдена")
    
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=CategorySchema)
def update_category(
    category_id: int, 
    category_update: CategoryUpdate, 
    db: Session = Depends(get_db)
):
    """
    Обновить категорию
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    # Проверка slug при обновлении
    if category_update.slug and category_update.slug != category.slug:
        existing_category = db.query(Category).filter(Category.slug == category_update.slug).first()
        if existing_category:
            raise HTTPException(status_code=400, detail="Категория с таким slug уже существует")
    
    # Проверка родительской категории при обновлении
    if category_update.parent_id:
        if category_update.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Категория не может быть родительской для самой себя")
        
        parent_category = db.query(Category).filter(Category.id == category_update.parent_id).first()
        if not parent_category:
            raise HTTPException(status_code=400, detail="Родительская категория не найдена")
    
    # Обновление полей
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Удалить категорию
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    # Проверка наличия дочерних категорий
    children = db.query(Category).filter(Category.parent_id == category_id).first()
    if children:
        raise HTTPException(
            status_code=400, 
            detail="Нельзя удалить категорию, которая содержит дочерние категории"
        )
    
    # Проверка наличия товаров в категории
    from app.models import Product
    products = db.query(Product).filter(Product.category_id == category_id).first()
    if products:
        raise HTTPException(
            status_code=400,
            detail="Нельзя удалить категорию, которая содержит товары"
        )
    
    db.delete(category)
    db.commit()
    return {"message": "Категория успешно удалена"}