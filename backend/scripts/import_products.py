"""
Скрипт для импорта товаров из CSV файла в базу данных EMC3
Поддерживает массовую загрузку LED светильников с техническими характеристиками
"""

import os
import sys
import asyncio
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from decimal import Decimal

# Добавляем путь к корню проекта
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine
from app.models.products import Product
from app.models.categories import Category
from sqlalchemy.orm import Session
from sqlalchemy import select

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_products.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProductImporter:
    """Класс для импорта товаров из различных источников"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.categories_cache = {}
        self.imported_count = 0
        self.errors_count = 0
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
        
    def load_categories_cache(self):
        """Загрузка кеша категорий для быстрого поиска"""
        try:
            categories = self.db.execute(select(Category)).scalars().all()
            for category in categories:
                self.categories_cache[category.name.lower()] = category.id
                self.categories_cache[category.slug.lower()] = category.id
            logger.info(f"Загружено {len(categories)} категорий в кеш")
        except Exception as e:
            logger.error(f"Ошибка загрузки категорий: {e}")
            
    def get_category_id(self, category_name: str) -> Optional[int]:
        """Получение ID категории по названию"""
        if not category_name:
            return None
            
        category_key = category_name.lower().strip()
        return self.categories_cache.get(category_key)
        
    def create_category_if_not_exists(self, category_name: str) -> int:
        """Создание категории если она не существует"""
        try:
            category_id = self.get_category_id(category_name)
            if category_id:
                return category_id
                
            # Создаем новую категорию
            new_category = Category(
                name=category_name.strip(),
                slug=self._generate_slug(category_name),
                description=f"Категория {category_name}",
                is_active=True
            )
            
            self.db.add(new_category)
            self.db.commit()
            self.db.refresh(new_category)
            
            # Обновляем кеш
            self.categories_cache[category_name.lower()] = new_category.id
            
            logger.info(f"Создана новая категория: {category_name} (ID: {new_category.id})")
            return new_category.id
            
        except Exception as e:
            logger.error(f"Ошибка создания категории {category_name}: {e}")
            self.db.rollback()
            return None
            
    def _generate_slug(self, name: str) -> str:
        """Генерация slug из названия"""
        import re
        
        # Транслитерация русских букв
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        
        slug = name.lower()
        for ru, en in translit_map.items():
            slug = slug.replace(ru, en)
            
        slug = re.sub(r'[^a-z0-9-]', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        return slug[:50]  # Ограничиваем длину
        
    def parse_csv_row(self, row: pd.Series) -> Dict[str, Any]:
        """Парсинг строки CSV в данные товара"""
        try:
            # Маппинг полей CSV к полям модели
            product_data = {
                'name': str(row.get('name', row.get('название', ''))).strip(),
                'article': str(row.get('article', row.get('артикул', ''))).strip(),
                'description': str(row.get('description', row.get('описание', ''))).strip(),
                'category_name': str(row.get('category', row.get('категория', ''))).strip(),
                'price': self._parse_decimal(row.get('price', row.get('цена', 0))),
                'b2b_price': self._parse_decimal(row.get('b2b_price', row.get('цена_b2b', 0))),
                'cost_price': self._parse_decimal(row.get('cost_price', row.get('себестоимость', 0))),
                'stock_quantity': self._parse_int(row.get('stock_quantity', row.get('остаток', 0))),
                'min_order_quantity': self._parse_int(row.get('min_order_quantity', row.get('мин_заказ', 1))),
                'weight': self._parse_decimal(row.get('weight', row.get('вес', 0))),
                'dimensions': str(row.get('dimensions', row.get('размеры', ''))).strip(),
                'warranty_years': self._parse_int(row.get('warranty_years', row.get('гарантия', 3))),
                'is_active': self._parse_bool(row.get('is_active', row.get('активен', True))),
                'is_featured': self._parse_bool(row.get('is_featured', row.get('рекомендуемый', False))),
                'meta_title': str(row.get('meta_title', '')).strip(),
                'meta_description': str(row.get('meta_description', '')).strip(),
                'tags': str(row.get('tags', row.get('теги', ''))).strip(),
                
                # Технические характеристики LED
                'power': self._parse_decimal(row.get('power', row.get('мощность', 0))),
                'voltage': str(row.get('voltage', row.get('напряжение', '220В'))).strip(),
                'current': self._parse_decimal(row.get('current', row.get('ток', 0))),
                'luminous_flux': self._parse_int(row.get('luminous_flux', row.get('световой_поток', 0))),
                'luminous_efficacy': self._parse_int(row.get('luminous_efficacy', row.get('светоотдача', 0))),
                'color_temperature': self._parse_int(row.get('color_temperature', row.get('цвет_температура', 4000))),
                'color_rendering_index': self._parse_int(row.get('cri', row.get('cri', 80))),
                'beam_angle': self._parse_int(row.get('beam_angle', row.get('угол_свечения', 120))),
                'protection_rating': str(row.get('protection_rating', row.get('ip', 'IP20'))).strip(),
                'operating_temperature': str(row.get('operating_temperature', row.get('температура', '-20...+40°C'))).strip(),
                'lifespan_hours': self._parse_int(row.get('lifespan_hours', row.get('срок_службы', 50000))),
                'dimming_support': self._parse_bool(row.get('dimming_support', row.get('диммирование', False))),
                'led_chip_brand': str(row.get('led_chip_brand', row.get('чип', ''))).strip(),
                'driver_brand': str(row.get('driver_brand', row.get('драйвер', ''))).strip(),
                'housing_material': str(row.get('housing_material', row.get('материал', 'Алюминий'))).strip(),
                'diffuser_type': str(row.get('diffuser_type', row.get('рассеиватель', ''))).strip(),
                'mounting_type': str(row.get('mounting_type', row.get('монтаж', ''))).strip(),
                'installation_area': str(row.get('installation_area', row.get('область_применения', ''))).strip(),
            }
            
            # Обработка изображений
            image_url = str(row.get('image_url', row.get('изображение', ''))).strip()
            if image_url:
                product_data['image_urls'] = [image_url]
            
            return product_data
            
        except Exception as e:
            logger.error(f"Ошибка парсинга строки CSV: {e}")
            return None
            
    def _parse_decimal(self, value) -> Decimal:
        """Безопасное преобразование в Decimal"""
        try:
            if pd.isna(value):
                return Decimal('0')
            return Decimal(str(value).replace(',', '.').replace(' ', ''))
        except:
            return Decimal('0')
            
    def _parse_int(self, value) -> int:
        """Безопасное преобразование в int"""
        try:
            if pd.isna(value):
                return 0
            return int(float(str(value).replace(',', '.').replace(' ', '')))
        except:
            return 0
            
    def _parse_bool(self, value) -> bool:
        """Безопасное преобразование в bool"""
        if pd.isna(value):
            return False
        
        str_value = str(value).lower().strip()
        return str_value in ('true', 'да', 'yes', '1', 'истина', 'активен')
        
    def import_from_csv(self, file_path: str, update_existing: bool = False) -> Dict[str, int]:
        """
        Импорт товаров из CSV файла
        
        Args:
            file_path: Путь к CSV файлу
            update_existing: Обновлять ли существующие товары
            
        Returns:
            Статистика импорта
        """
        try:
            logger.info(f"Начало импорта из файла: {file_path}")
            
            # Загрузка кеша категорий
            self.load_categories_cache()
            
            # Чтение CSV файла
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            logger.info(f"Загружено {len(df)} строк из CSV")
            
            success_count = 0
            error_count = 0
            updated_count = 0
            
            for index, row in df.iterrows():
                try:
                    product_data = self.parse_csv_row(row)
                    if not product_data:
                        error_count += 1
                        continue
                        
                    # Проверка обязательных полей
                    if not product_data['name'] or not product_data['article']:
                        logger.warning(f"Строка {index + 1}: отсутствуют обязательные поля (название или артикул)")
                        error_count += 1
                        continue
                        
                    # Получение или создание категории
                    category_id = None
                    if product_data['category_name']:
                        category_id = self.create_category_if_not_exists(product_data['category_name'])
                        
                    # Проверка существования товара
                    existing_product = self.db.execute(
                        select(Product).where(Product.article == product_data['article'])
                    ).scalar_one_or_none()
                    
                    if existing_product:
                        if update_existing:
                            # Обновление существующего товара
                            self.update_product(existing_product, product_data, category_id)
                            updated_count += 1
                            logger.info(f"Обновлен товар: {product_data['article']}")
                        else:
                            logger.info(f"Товар {product_data['article']} уже существует, пропускаем")
                            continue
                    else:
                        # Создание нового товара
                        self.create_product(product_data, category_id)
                        success_count += 1
                        logger.info(f"Создан товар: {product_data['article']}")
                        
                except Exception as e:
                    logger.error(f"Ошибка обработки строки {index + 1}: {e}")
                    error_count += 1
                    continue
                    
            # Сохранение изменений
            self.db.commit()
            
            logger.info(f"Импорт завершен. Создано: {success_count}, обновлено: {updated_count}, ошибок: {error_count}")
            
            return {
                'created': success_count,
                'updated': updated_count,
                'errors': error_count,
                'total_processed': len(df)
            }
            
        except Exception as e:
            logger.error(f"Критическая ошибка импорта: {e}")
            self.db.rollback()
            raise
            
    def create_product(self, product_data: Dict[str, Any], category_id: Optional[int]):
        """Создание нового товара"""
        try:
            product = Product(
                name=product_data['name'],
                article=product_data['article'],
                description=product_data['description'],
                category_id=category_id,
                price=product_data['price'],
                b2b_price=product_data['b2b_price'],
                cost_price=product_data['cost_price'],
                stock_quantity=product_data['stock_quantity'],
                min_order_quantity=product_data['min_order_quantity'],
                weight=product_data['weight'],
                dimensions=product_data['dimensions'],
                warranty_years=product_data['warranty_years'],
                is_active=product_data['is_active'],
                is_featured=product_data['is_featured'],
                meta_title=product_data['meta_title'],
                meta_description=product_data['meta_description'],
                tags=product_data['tags'],
                image_urls=product_data.get('image_urls', []),
                
                # Технические характеристики
                power=product_data['power'],
                voltage=product_data['voltage'],
                current=product_data['current'],
                luminous_flux=product_data['luminous_flux'],
                luminous_efficacy=product_data['luminous_efficacy'],
                color_temperature=product_data['color_temperature'],
                color_rendering_index=product_data['color_rendering_index'],
                beam_angle=product_data['beam_angle'],
                protection_rating=product_data['protection_rating'],
                operating_temperature=product_data['operating_temperature'],
                lifespan_hours=product_data['lifespan_hours'],
                dimming_support=product_data['dimming_support'],
                led_chip_brand=product_data['led_chip_brand'],
                driver_brand=product_data['driver_brand'],
                housing_material=product_data['housing_material'],
                diffuser_type=product_data['diffuser_type'],
                mounting_type=product_data['mounting_type'],
                installation_area=product_data['installation_area'],
            )
            
            self.db.add(product)
            
        except Exception as e:
            logger.error(f"Ошибка создания товара {product_data.get('article', 'unknown')}: {e}")
            raise
            
    def update_product(self, product: Product, product_data: Dict[str, Any], category_id: Optional[int]):
        """Обновление существующего товара"""
        try:
            # Обновляем только не пустые поля
            for field, value in product_data.items():
                if field in ['category_name', 'image_urls']:
                    continue
                    
                if value is not None and value != '' and value != 0:
                    setattr(product, field, value)
                    
            if category_id:
                product.category_id = category_id
                
            if product_data.get('image_urls'):
                product.image_urls = product_data['image_urls']
                
        except Exception as e:
            logger.error(f"Ошибка обновления товара {product.article}: {e}")
            raise
            
    def update_prices_from_csv(self, file_path: str) -> Dict[str, int]:
        """Обновление только цен из CSV файла"""
        try:
            logger.info(f"Начало обновления цен из файла: {file_path}")
            
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            updated_count = 0
            not_found_count = 0
            
            for index, row in df.iterrows():
                try:
                    article = str(row.get('article', row.get('артикул', ''))).strip()
                    if not article:
                        continue
                        
                    price = self._parse_decimal(row.get('price', row.get('цена', 0)))
                    b2b_price = self._parse_decimal(row.get('b2b_price', row.get('цена_b2b', 0)))
                    
                    if price <= 0 and b2b_price <= 0:
                        continue
                        
                    # Поиск товара
                    product = self.db.execute(
                        select(Product).where(Product.article == article)
                    ).scalar_one_or_none()
                    
                    if product:
                        if price > 0:
                            product.price = price
                        if b2b_price > 0:
                            product.b2b_price = b2b_price
                            
                        updated_count += 1
                        logger.info(f"Обновлены цены для товара: {article}")
                    else:
                        not_found_count += 1
                        logger.warning(f"Товар не найден: {article}")
                        
                except Exception as e:
                    logger.error(f"Ошибка обновления цены в строке {index + 1}: {e}")
                    continue
                    
            self.db.commit()
            
            logger.info(f"Обновление цен завершено. Обновлено: {updated_count}, не найдено: {not_found_count}")
            
            return {
                'updated': updated_count,
                'not_found': not_found_count,
                'total_processed': len(df)
            }
            
        except Exception as e:
            logger.error(f"Критическая ошибка обновления цен: {e}")
            self.db.rollback()
            raise


def main():
    """Основная функция для запуска импорта"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Импорт товаров EMC3 из CSV файла')
    parser.add_argument('file_path', help='Путь к CSV файлу')
    parser.add_argument('--update', action='store_true', help='Обновлять существующие товары')
    parser.add_argument('--prices-only', action='store_true', help='Обновлять только цены')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        logger.error(f"Файл не найден: {args.file_path}")
        return
        
    try:
        with ProductImporter() as importer:
            if args.prices_only:
                result = importer.update_prices_from_csv(args.file_path)
                print(f"Результат обновления цен: {result}")
            else:
                result = importer.import_from_csv(args.file_path, args.update)
                print(f"Результат импорта: {result}")
                
    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())