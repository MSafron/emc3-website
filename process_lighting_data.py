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
            'авиор': ('Уличное освещение', 'Консольные светильники')  # серия АВИОР для уличного освещения
        }
    
    def extract_power(self, name: str) -> Optional[str]:
        """Извлекает мощность из названия товара"""
        match = re.search(r'(\d+)\s*[Вв][тт]', name)
        return match.group(1) if match else None
    
    def extract_luminous_flux(self, description: str, properties: str) -> Optional[str]:
        """Извлекает световой поток из описания или свойств"""
        text = f"{description} {properties}"
        # Ищем значения в люменах
        match = re.search(r'(\d+[\s,]*\d*)\s*[Лл][мм]', text)
        if match:
            return match.group(1).replace(' ', '').replace(',', '')
        return None
    
    def extract_color_temperature(self, description: str, properties: str) -> Optional[str]:
        """Извлекает цветовую температуру"""
        text = f"{description} {properties}"
        # Ищем значения в Кельвинах
        match = re.search(r'(\d+)\s*[КкKk]', text)
        return match.group(1) if match else None
    
    def determine_category(self, name: str, description: str) -> tuple:
        """Определяет категорию товара"""
        text = f"{name} {description}".lower()
        
        if 'авиор' in text or 'магистральн' in text or 'улич' in text:
            return self.categories_mapping['уличное']
        elif 'промышленн' in text:
            return self.categories_mapping['промышленное']
        else:
            # По умолчанию уличное освещение
            return self.categories_mapping['уличное']
    
    def clean_text(self, text: str) -> str:
        """Очищает текст от HTML тегов и лишних символов"""
        if not text:
            return ""
        
        # Удаляем HTML теги
        text = re.sub(r'<[^>]+>', '', text)
        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text).strip()
        # Удаляем специальные символы
        text = text.replace('&nbsp;', ' ').replace('&quot;', '"')
        
        return text
    
    def process_csv_file(self, input_file: str) -> List[Dict]:
        """Обрабатывает CSV файл и извлекает нужные данные"""
        processed_items = []
        
        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                # Читаем первую строку как заголовки
                headers = file.readline().strip().split('\t')
                
                # Находим индексы нужных колонок
                name_idx = self._find_column_index(headers, ['IE_NAME'])
                description_idx = self._find_column_index(headers, ['IE_DETAIL_TEXT', 'IE_PREVIEW_TEXT'])
                price_idx = self._find_column_index(headers, ['CV_PRICE_1'])
                sku_idx = self._find_column_index(headers, ['IP_PROP1'])  # Артикул
                power_idx = self._find_column_index(headers, ['IP_PROP2'])  # Мощность
                manufacturer_idx = self._find_column_index(headers, ['IP_PROP3'])  # Производитель
                country_idx = self._find_column_index(headers, ['IP_PROP4'])  # Страна
                flux_idx = self._find_column_index(headers, ['IP_PROP5'])  # Световой поток
                
                for line_num, line in enumerate(file, 2):
                    try:
                        fields = line.strip().split('\t')
                        
                        if len(fields) < max(name_idx, description_idx, price_idx) + 1:
                            continue
                        
                        name = fields[name_idx] if name_idx < len(fields) else ""
                        description = fields[description_idx] if description_idx < len(fields) else ""
                        price = fields[price_idx] if price_idx < len(fields) else ""
                        sku = fields[sku_idx] if sku_idx < len(fields) else ""
                        power = fields[power_idx] if power_idx < len(fields) else ""
                        manufacturer = fields[manufacturer_idx] if manufacturer_idx < len(fields) else ""
                        country = fields[country_idx] if country_idx < len(fields) else ""
                        flux = fields[flux_idx] if flux_idx < len(fields) else ""
                        
                        # Пропускаем пустые записи
                        if not name.strip():
                            continue
                        
                        # Определяем категории
                        cat_level1, cat_level2 = self.determine_category(name, description)
                        
                        # Извлекаем характеристики
                        extracted_power = self.extract_power(name) or power
                        extracted_flux = self.extract_luminous_flux(description, flux) or flux
                        extracted_temp = self.extract_color_temperature(description, "")
                        
                        # Очищаем текст
                        clean_name = self.clean_text(name)
                        clean_description = self.clean_text(description)
                        
                        item = {
                            'category_level1': cat_level1,
                            'category_level2': cat_level2,
                            'name': clean_name,
                            'sku': sku,
                            'price': price.replace(',', '.') if price else "",
                            'description': clean_description,
                            'manufacturer': manufacturer or "MLight",
                            'country': country or "Россия",
                            'power': extracted_power,
                            'luminous_flux': extracted_flux,
                            'color_temperature': extracted_temp or "4000/5000",
                            'manufacturing_time': "5-10 рабочих дней",
                            'seo_title': f"{clean_name} - купить в интернет-магазине",
                            'seo_description': f"Купить {clean_name} по выгодной цене. Доставка по России. Гарантия качества.",
                            'seo_keywords': f"{clean_name}, светодиодный светильник, освещение",
                            'images': "Требуется загрузка изображений"
                        }
                        
                        processed_items.append(item)
                        
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
    for i, item in enumerate(processed_data[:3]):
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