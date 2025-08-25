import pandas as pd
import re
from sqlalchemy.orm import Session
from app.models import Category, Product
from app.database import SessionLocal
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text):
    """Очистка текста от лишних символов"""
    if pd.isna(text):
        return None
    return str(text).strip()

def extract_number(text, default=None):
    """Извлечение числа из текста"""
    if pd.isna(text):
        return default
    
    # Поиск числа в тексте
    match = re.search(r'(\d+)', str(text))
    if match:
        return int(match.group(1))
    return default

def extract_float(text, default=None):
    """Извлечение числа с плавающей точкой из текста"""
    if pd.isna(text):
        return default
    
    # Замена запятой на точку для правильного парсинга
    text = str(text).replace(',', '.')
    match = re.search(r'(\d+\.?\d*)', text)
    if match:
        return float(match.group(1))
    return default

def create_slug(name):
    """Создание slug из названия категории"""
    if not name:
        return ""
    
    # Транслитерация основных русских букв
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    
    slug = name.lower()
    for ru, en in translit_dict.items():
        slug = slug.replace(ru, en)
    
    # Замена пробелов и спецсимволов на дефисы
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Удаление дефисов в начале и конце
    slug = slug.strip('-')
    
    return slug

def import_categories_and_products(csv_file_path: str):
    """
    Импорт категорий и товаров из CSV файла
    """
    logger.info(f"Начинаем импорт данных из {csv_file_path}")
    
    try:
        # Чтение CSV файла
        df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8')
        logger.info(f"Загружено {len(df)} строк из CSV")
        
        # Создание сессии БД
        db = SessionLocal()
        
        try:
            # Словарь для хранения созданных категорий
            categories_dict = {}
            
            # Статистика
            categories_created = 0
            products_created = 0
            products_updated = 0
            
            for index, row in df.iterrows():
                try:
                    # Обработка категорий
                    category1 = clean_text(row.get('Категория уровень 1'))
                    category2 = clean_text(row.get('Категория уровень 2'))
                    
                    parent_category = None
                    main_category = None
                    
                    # Создание родительской категории (уровень 1)
                    if category1:
                        if category1 not in categories_dict:
                            slug1 = create_slug(category1)
                            # Проверка существования по slug
                            existing_cat1 = db.query(Category).filter(Category.slug == slug1).first()
                            if not existing_cat1:
                                parent_category = Category(
                                    name=category1,
                                    slug=slug1,
                                    description=f"Категория {category1}"
                                )
                                db.add(parent_category)
                                db.commit()
                                db.refresh(parent_category)
                                categories_created += 1
                                logger.info(f"Создана категория уровня 1: {category1}")
                            else:
                                parent_category = existing_cat1
                            
                            categories_dict[category1] = parent_category
                        else:
                            parent_category = categories_dict[category1]
                    
                    # Создание дочерней категории (уровень 2)
                    if category2:
                        category_key = f"{category1}:{category2}"
                        if category_key not in categories_dict:
                            slug2 = create_slug(category2)
                            # Проверка существования по slug
                            existing_cat2 = db.query(Category).filter(Category.slug == slug2).first()
                            if not existing_cat2:
                                main_category = Category(
                                    name=category2,
                                    slug=slug2,
                                    description=f"Категория {category2}",
                                    parent_id=parent_category.id if parent_category else None
                                )
                                db.add(main_category)
                                db.commit()
                                db.refresh(main_category)
                                categories_created += 1
                                logger.info(f"Создана категория уровня 2: {category2}")
                            else:
                                main_category = existing_cat2
                            
                            categories_dict[category_key] = main_category
                        else:
                            main_category = categories_dict[category_key]
                    
                    # Обработка товара
                    product_name = clean_text(row.get('Название'))
                    product_sku = clean_text(row.get('Артикул'))
                    
                    if not product_name or not product_sku:
                        logger.warning(f"Пропуск строки {index}: отсутствует название или артикул")
                        continue
                    
                    # Извлечение данных товара
                    price = extract_float(row.get('Цена'), 0.0)
                    power_watts = extract_number(row.get('Мощность (Вт)'))
                    luminous_flux = extract_number(row.get('Световой поток (Лм)'))
                    color_temperature = extract_number(row.get('Цветовая температура (К)'))
                    
                    # Проверка существования товара
                    existing_product = db.query(Product).filter(Product.sku == product_sku).first()
                    
                    if existing_product:
                        # Обновление существующего товара
                        existing_product.name = product_name
                        existing_product.price = price
                        existing_product.description = clean_text(row.get('Описание'))
                        existing_product.manufacturer = clean_text(row.get('Производитель'))
                        existing_product.country = clean_text(row.get('Страна'))
                        existing_product.power_watts = power_watts
                        existing_product.luminous_flux = luminous_flux
                        existing_product.color_temperature = color_temperature
                        existing_product.manufacturing_time = clean_text(row.get('Срок изготовления'))
                        existing_product.seo_title = clean_text(row.get('SEO заголовок'))
                        existing_product.seo_description = clean_text(row.get('SEO описание'))
                        existing_product.seo_keywords = clean_text(row.get('SEO ключевые слова'))
                        existing_product.images = clean_text(row.get('Изображения'))
                        existing_product.category_id = main_category.id if main_category else (parent_category.id if parent_category else None)
                        
                        products_updated += 1
                        
                    else:
                        # Создание нового товара
                        new_product = Product(
                            name=product_name,
                            sku=product_sku,
                            price=price,
                            description=clean_text(row.get('Описание')),
                            manufacturer=clean_text(row.get('Производитель')),
                            country=clean_text(row.get('Страна')),
                            power_watts=power_watts,
                            luminous_flux=luminous_flux,
                            color_temperature=color_temperature,
                            manufacturing_time=clean_text(row.get('Срок изготовления')),
                            seo_title=clean_text(row.get('SEO заголовок')),
                            seo_description=clean_text(row.get('SEO описание')),
                            seo_keywords=clean_text(row.get('SEO ключевые слова')),
                            images=clean_text(row.get('Изображения')),
                            category_id=main_category.id if main_category else (parent_category.id if parent_category else None)
                        )
                        
                        db.add(new_product)
                        products_created += 1
                    
                    # Коммит каждые 50 товаров
                    if (index + 1) % 50 == 0:
                        db.commit()
                        logger.info(f"Обработано {index + 1} строк")
                
                except Exception as e:
                    logger.error(f"Ошибка при обработке строки {index}: {e}")
                    continue
            
            # Финальный коммит
            db.commit()
            
            logger.info(f"""
            Импорт завершен!
            Создано категорий: {categories_created}
            Создано товаров: {products_created}
            Обновлено товаров: {products_updated}
            """)
            
            return {
                "categories_created": categories_created,
                "products_created": products_created,
                "products_updated": products_updated
            }
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Критическая ошибка при импорте: {e}")
        raise

if __name__ == "__main__":
    # Запуск импорта
    csv_path = "../../import_b24.csv"  # Путь к CSV файлу
    result = import_categories_and_products(csv_path)
    print(f"Результат импорта: {result}")