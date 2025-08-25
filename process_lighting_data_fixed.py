#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обработки данных освещения из stock.csv и создания файла для импорта в Битрикс24
"""

import csv
import re
import os
from typing import Dict, List, Optional

class LightingDataProcessor:
    def __init__(self):
        self.processed_data = []
        self.categories_mapping = {
            'уличное': ('Уличное освещение', 'Консольные светильники'),
            'магистральное': ('Уличное освещение', 'Консольные светильники'),
            'промышленное': ('Промышленное освещение', 'Подвесные светильники'),
            'highway': ('Уличное освещение', 'Консольные светильники'),  # серия Highway для уличного освещения
            'econex': ('Уличное освещение', 'Консольные светильники')
        }
    
    def extract_power(self, name: str) -> Optional[str]:
        """Извлекает мощность из названия товара"""
        # Ищем паттерны типа "80 W", "80W", "80 Вт"
        match = re.search(r'(\d+)\s*[WВ][тt]*', name, re.IGNORECASE)
        return match.group(1) if match else None
    
    def extract_luminous_flux(self, description: str) -> Optional[str]:
        """Извлекает световой поток из описания"""
        if not description:
            return None
        # Ищем значения в люменах
        match = re.search(r'(\d+[\s,]*\d*)\s*[Лл][мм]', description)
        if match:
            return match.group(1).replace(' ', '').replace(',', '')
        
        # Если не найдено, попробуем извлечь из других паттернов
        match = re.search(r'(\d+)\s*lm', description, re.IGNORECASE)
        if match:
            return match.group(1)
            
        return None
    
    def extract_color_temperature(self, name: str, description: str) -> Optional[str]:
        """Извлекает цветовую температуру"""
        text = f"{name} {description}".lower()
        # Ищем значения в Кельвинах
        match = re.search(r'(\d+)\s*к', text)
        if match:
            return match.group(1)
        return None
    
    def determine_category(self, name: str, description: str, category: str) -> tuple:
        """Определяет категорию товара"""
        text = f"{name} {description} {category}".lower()
        
        if any(word in text for word in ['highway', 'улич', 'консольн', 'дку', 'econex']):
            return self.categories_mapping['уличное']
        elif 'промышленн' in text:
            return self.categories_mapping['промышленное']
        else:
            # По умолчанию уличное освещение
            return self.categories_mapping['уличное']
    
    def clean_text(self, text: str) -> str:
        """Очищает текст от лишних символов"""
        if not text:
            return ""
        
        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text).strip()
        # Удаляем кавычки в начале и конце
        text = text.strip('"')
        
        return text
    
    def estimate_luminous_flux_by_power(self, power: str) -> str:
        """Оценивает световой поток по мощности (для LED светильников)"""
        try:
            power_int = int(power)
            # Примерная эффективность LED светильников 120-150 лм/Вт
            estimated_flux = power_int * 130  # Берем среднее значение
            return str(estimated_flux)
        except:
            return ""
    
    def process_csv_file(self, input_file: str) -> List[Dict]:
        """Обрабатывает CSV файл и извлекает нужные данные"""
        processed_items = []
        
        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                
                # Пропускаем первые две строки (stock и пустая строка)
                next(reader)  # пропускаем "stock"
                next(reader)  # пропускаем "stock;;;;;;;;;;"
                headers = next(reader)  # читаем настоящие заголовки
                
                print(f"Найденные заголовки: {headers}")
                
                # Находим индексы нужных колонок
                name_idx = self._find_column_index(headers, ['name'])
                description_idx = self._find_column_index(headers, ['description'])
                price_idx = self._find_column_index(headers, ['price'])
                sku_idx = self._find_column_index(headers, ['sku'])
                manufacturer_idx = self._find_column_index(headers, ['manufacturer'])
                country_idx = self._find_column_index(headers, ['country'])
                category_idx = self._find_column_index(headers, ['category'])
                
                print(f"Индексы колонок: name={name_idx}, desc={description_idx}, price={price_idx}")
                
                for line_num, fields in enumerate(reader, 2):
                    try:
                        if len(fields) < len(headers):
                            continue
                        
                        name = fields[name_idx] if name_idx != -1 else ""
                        description = fields[description_idx] if description_idx != -1 else ""
                        price = fields[price_idx] if price_idx != -1 else ""
                        sku = fields[sku_idx] if sku_idx != -1 else ""
                        manufacturer = fields[manufacturer_idx] if manufacturer_idx != -1 else ""
                        country = fields[country_idx] if country_idx != -1 else ""
                        category = fields[category_idx] if category_idx != -1 else ""
                        
                        # Пропускаем пустые записи
                        if not name.strip() or name.strip().lower() in ['name', 'название']:
                            continue
                        
                        # Определяем категории
                        cat_level1, cat_level2 = self.determine_category(name, description, category)
                        
                        # Извлекаем характеристики
                        extracted_power = self.extract_power(name)
                        extracted_flux = self.extract_luminous_flux(description)
                        
                        # Если световой поток не найден, оцениваем по мощности
                        if not extracted_flux and extracted_power:
                            extracted_flux = self.estimate_luminous_flux_by_power(extracted_power)
                        
                        extracted_temp = self.extract_color_temperature(name, description)
                        
                        # Очищаем текст
                        clean_name = self.clean_text(name)
                        clean_description = self.clean_text(description)
                        
                        # Генерируем артикул если отсутствует
                        if not sku.strip():
                            sku = f"LED-{extracted_power}W-{extracted_temp}K" if extracted_power and extracted_temp else f"ITEM-{line_num}"
                        
                        item = {
                            'category_level1': cat_level1,
                            'category_level2': cat_level2,
                            'name': clean_name,
                            'sku': sku,
                            'price': price.replace(',', '.') if price else "",
                            'description': clean_description,
                            'manufacturer': manufacturer or "Эконекс",
                            'country': country or "Россия",
                            'power': extracted_power or "",
                            'luminous_flux': extracted_flux or "",
                            'color_temperature': extracted_temp or "4000",
                            'manufacturing_time': "5-10 рабочих дней",
                            'seo_title': f"{clean_name} - купить в интернет-магазине",
                            'seo_description': f"Купить {clean_name} по выгодной цене. Доставка по России. Гарантия качества.",
                            'seo_keywords': f"{clean_name}, светодиодный светильник, освещение",
                            'images': "Требуется загрузка изображений"
                        }
                        
                        processed_items.append(item)
                        
                        if len(processed_items) % 100 == 0:
                            print(f"Обработано {len(processed_items)} товаров...")
                        
                    except Exception as e:
                        print(f"Ошибка обработки строки {line_num}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
            return []
        
        return processed_items
    
    def _find_column_index(self, headers: List[str], possible_names: List[str]) -> int:
        """Находит индекс колонки по возможным названиям"""
        for name in possible_names:
            try:
                return headers.index(name)
            except ValueError:
                continue
        return -1
    
    def create_import_csv(self, processed_data: List[Dict], output_file: str):
        """Создает CSV файл для импорта в Битрикс24"""
        headers = [
            'Категория уровень 1',
            'Категория уровень 2', 
            'Название',
            'Артикул',
            'Цена',
            'Описание',
            'Производитель',
            'Страна',
            'Мощность (Вт)',
            'Световой поток (Лм)',
            'Цветовая температура (К)',
            'Срок изготовления',
            'SEO заголовок',
            'SEO описание',
            'SEO ключевые слова',
            'Изображения'
        ]
        
        with open(output_file, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(headers)
            
            for item in processed_data:
                row = [
                    item['category_level1'],
                    item['category_level2'],
                    item['name'],
                    item['sku'],
                    item['price'],
                    item['description'][:500] + '...' if len(item['description']) > 500 else item['description'],
                    item['manufacturer'],
                    item['country'],
                    item['power'],
                    item['luminous_flux'],
                    item['color_temperature'],
                    item['manufacturing_time'],
                    item['seo_title'],
                    item['seo_description'],
                    item['seo_keywords'],
                    item['images']
                ]
                writer.writerow(row)

def main():
    processor = LightingDataProcessor()
    
    # Обрабатываем исходный файл
    print("Обработка файла stock.csv...")
    processed_data = processor.process_csv_file('stock.csv')
    
    if not processed_data:
        print("Не удалось обработать данные")
        return
    
    print(f"Обработано товаров: {len(processed_data)}")
    
    # Создаем файл для импорта
    output_file = 'import_b24.csv'
    processor.create_import_csv(processed_data, output_file)
    
    print(f"Файл для импорта создан: {output_file}")
    
    # Выводим примеры обработанных записей
    print("\nПримеры обработанных записей:")
    for i, item in enumerate(processed_data[:5]):
        print(f"\nТовар {i+1}:")
        print(f"  Категория: {item['category_level1']} -> {item['category_level2']}")
        print(f"  Название: {item['name']}")
        print(f"  Артикул: {item['sku']}")
        print(f"  Цена: {item['price']} руб.")
        print(f"  Мощность: {item['power']} Вт")
        print(f"  Световой поток: {item['luminous_flux']} Лм")
        print(f"  Цветовая температура: {item['color_temperature']} К")

if __name__ == "__main__":
    main()