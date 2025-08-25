#!/usr/bin/env python3
"""
Скрипт для импорта данных из CSV файла в базу данных EMC3
"""

import sys
import os
from pathlib import Path

# Добавляем директорию app в Python path
current_dir = Path(__file__).resolve().parent
app_dir = current_dir / "app"
sys.path.insert(0, str(current_dir))

from app.utils.import_data import import_categories_and_products
from app.database import engine, Base

def main():
    """Основная функция для запуска импорта"""
    print("=== Импорт данных EMC3 Lighting ===")
    
    # Путь к CSV файлу
    csv_path = "../import_b24.csv"
    
    if not os.path.exists(csv_path):
        print(f"Ошибка: Файл {csv_path} не найден!")
        print("Убедитесь, что файл import_b24.csv находится в корневой директории проекта.")
        return 1
    
    try:
        # Создание таблиц если их нет
        print("Создание таблиц в базе данных...")
        Base.metadata.create_all(bind=engine)
        print("✓ Таблицы созданы")
        
        # Запуск импорта
        print(f"Начинаем импорт из файла: {csv_path}")
        result = import_categories_and_products(csv_path)
        
        print("\n=== Результаты импорта ===")
        print(f"✓ Создано категорий: {result['categories_created']}")
        print(f"✓ Создано товаров: {result['products_created']}")
        print(f"✓ Обновлено товаров: {result['products_updated']}")
        print("\n🎉 Импорт успешно завершен!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Ошибка при импорте: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)