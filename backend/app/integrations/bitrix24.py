"""
Интеграция с Битрикс24 для EMC3
Автоматическое создание лидов и счетов при оформлении заказов
"""

import httpx
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class Bitrix24Integration:
    """Класс для работы с API Битрикс24"""
    
    def __init__(self):
        self.webhook_url = settings.BITRIX24_WEBHOOK_URL
        self.domain = settings.BITRIX24_DOMAIN
        self.user_id = settings.BITRIX24_USER_ID
        self.timeout = 30
        
    async def _make_request(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Базовый метод для выполнения запросов к API Битрикс24"""
        url = f"{self.webhook_url}{method}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                
                result = response.json()
                
                if "error" in result:
                    logger.error(f"Ошибка Битрикс24 API: {result['error']}")
                    raise Exception(f"Битрикс24 API ошибка: {result['error']}")
                
                return result
                
        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса к Битрикс24: {e}")
            raise Exception(f"Ошибка подключения к Битрикс24: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка Битрикс24: {e.response.status_code}")
            raise Exception(f"HTTP ошибка Битрикс24: {e.response.status_code}")

    async def create_lead(self, order_data: Dict[str, Any]) -> int:
        """
        Создание лида в Битрикс24 на основе заказа
        
        Args:
            order_data: Данные заказа
            
        Returns:
            ID созданного лида
        """
        try:
            # Подготовка данных лида
            lead_fields = {
                "TITLE": f"Заявка на LED светильники #{order_data['id']}",
                "NAME": order_data.get('contact_person', ''),
                "COMPANY_TITLE": order_data.get('company_name', ''),
                "PHONE": [{"VALUE": order_data.get('phone', ''), "VALUE_TYPE": "WORK"}] if order_data.get('phone') else [],
                "EMAIL": [{"VALUE": order_data.get('email', ''), "VALUE_TYPE": "WORK"}] if order_data.get('email') else [],
                "COMMENTS": self._format_order_details(order_data),
                "SOURCE_ID": "WEB",
                "STATUS_ID": "NEW",
                "CURRENCY_ID": "RUB",
                "OPPORTUNITY": order_data.get('total_amount', 0),
                "ASSIGNED_BY_ID": self.user_id,
                "OPENED": "Y",
                "UF_CRM_1234567890123": order_data.get('inn', ''),  # Пользовательское поле ИНН
                "UF_CRM_1234567890124": order_data.get('kpp', ''),  # Пользовательское поле КПП
            }
            
            # Добавление адреса если есть
            if order_data.get('address'):
                lead_fields["ADDRESS"] = order_data['address']
            
            data = {"fields": lead_fields}
            
            # Создание лида
            result = await self._make_request("crm.lead.add", data)
            
            lead_id = result.get("result")
            if not lead_id:
                raise Exception("Не удалось получить ID созданного лида")
            
            logger.info(f"Создан лид #{lead_id} для заказа #{order_data['id']}")
            
            # Добавление товаров как продукты к лиду
            await self._add_products_to_lead(lead_id, order_data.get('items', []))
            
            return lead_id
            
        except Exception as e:
            logger.error(f"Ошибка создания лида: {e}")
            raise

    async def _add_products_to_lead(self, lead_id: int, items: List[Dict[str, Any]]):
        """Добавление товаров к лиду"""
        try:
            products = []
            
            for item in items:
                product = {
                    "PRODUCT_NAME": item.get('product_name', ''),
                    "PRICE": item.get('unit_price', 0),
                    "QUANTITY": item.get('quantity', 1),
                    "MEASURE_CODE": "796",  # Код единицы измерения "штука"
                    "MEASURE_NAME": "шт",
                    "PRODUCT_DESCRIPTION": self._format_product_specs(item),
                }
                products.append(product)
            
            if products:
                data = {
                    "id": lead_id,
                    "rows": products
                }
                
                await self._make_request("crm.lead.productrows.set", data)
                logger.info(f"Добавлено {len(products)} товаров к лиду #{lead_id}")
                
        except Exception as e:
            logger.error(f"Ошибка добавления товаров к лиду {lead_id}: {e}")

    async def create_deal_from_lead(self, lead_id: int, order_data: Dict[str, Any]) -> int:
        """
        Создание сделки из лида при подтверждении заказа
        
        Args:
            lead_id: ID лида
            order_data: Данные заказа
            
        Returns:
            ID созданной сделки
        """
        try:
            deal_fields = {
                "TITLE": f"Заказ LED светильников #{order_data['id']}",
                "TYPE_ID": "SALE",
                "STAGE_ID": "NEW",
                "CURRENCY_ID": "RUB",
                "OPPORTUNITY": order_data.get('total_amount', 0),
                "PROBABILITY": 90,
                "ASSIGNED_BY_ID": self.user_id,
                "OPENED": "Y",
                "COMMENTS": f"Сделка создана из лида #{lead_id}",
                "LEAD_ID": lead_id,
                "COMPANY_TITLE": order_data.get('company_name', ''),
                "CONTACT_ID": order_data.get('contact_id'),  # Если есть контакт
            }
            
            data = {"fields": deal_fields}
            
            result = await self._make_request("crm.deal.add", data)
            
            deal_id = result.get("result")
            if not deal_id:
                raise Exception("Не удалось получить ID созданной сделки")
                
            logger.info(f"Создана сделка #{deal_id} из лида #{lead_id}")
            
            # Добавление товаров к сделке
            await self._add_products_to_deal(deal_id, order_data.get('items', []))
            
            return deal_id
            
        except Exception as e:
            logger.error(f"Ошибка создания сделки из лида {lead_id}: {e}")
            raise

    async def _add_products_to_deal(self, deal_id: int, items: List[Dict[str, Any]]):
        """Добавление товаров к сделке"""
        try:
            products = []
            
            for item in items:
                product = {
                    "PRODUCT_NAME": item.get('product_name', ''),
                    "PRICE": item.get('unit_price', 0),
                    "QUANTITY": item.get('quantity', 1),
                    "MEASURE_CODE": "796",
                    "MEASURE_NAME": "шт",
                    "PRODUCT_DESCRIPTION": self._format_product_specs(item),
                }
                products.append(product)
            
            if products:
                data = {
                    "id": deal_id,
                    "rows": products
                }
                
                await self._make_request("crm.deal.productrows.set", data)
                logger.info(f"Добавлено {len(products)} товаров к сделке #{deal_id}")
                
        except Exception as e:
            logger.error(f"Ошибка добавления товаров к сделке {deal_id}: {e}")

    async def create_invoice(self, deal_id: int, order_data: Dict[str, Any]) -> int:
        """
        Создание счета на оплату
        
        Args:
            deal_id: ID сделки
            order_data: Данные заказа
            
        Returns:
            ID созданного счета
        """
        try:
            # Счет в Битрикс24 создается через универсальный документ
            invoice_fields = {
                "TITLE": f"Счет на оплату #{order_data['id']}",
                "DEAL_ID": deal_id,
                "STATUS_ID": "N",  # Новый
                "PRICE": order_data.get('total_amount', 0),
                "CURRENCY": "RUB",
                "PERSON_TYPE_ID": 2,  # Юридическое лицо
                "PAY_SYSTEM_ID": 1,   # Банковский перевод
                "DELIVERY_ID": 1,     # Самовывоз/доставка
                "USER_DESCRIPTION": f"Счет по заказу #{order_data['id']} для {order_data.get('company_name', '')}",
                "COMMENTS": "Оплата по безналичному расчету. НДС включен в стоимость.",
            }
            
            # Добавление реквизитов плательщика
            if order_data.get('inn'):
                invoice_fields["UF_COMPANY_NAME"] = order_data.get('company_name', '')
                invoice_fields["UF_COMPANY_INN"] = order_data.get('inn', '')
                invoice_fields["UF_COMPANY_KPP"] = order_data.get('kpp', '')
                invoice_fields["UF_COMPANY_ADDRESS"] = order_data.get('address', '')
            
            data = {"fields": invoice_fields}
            
            # В Битрикс24 может отличаться метод создания счета в зависимости от версии
            # Используем универсальный подход
            result = await self._make_request("crm.invoice.add", data)
            
            invoice_id = result.get("result")
            if not invoice_id:
                raise Exception("Не удалось получить ID созданного счета")
                
            logger.info(f"Создан счет #{invoice_id} для сделки #{deal_id}")
            
            return invoice_id
            
        except Exception as e:
            logger.error(f"Ошибка создания счета для сделки {deal_id}: {e}")
            raise

    async def update_lead_status(self, lead_id: int, status: str, comment: str = ""):
        """
        Обновление статуса лида
        
        Args:
            lead_id: ID лида
            status: Новый статус (NEW, IN_PROCESS, PROCESSED, JUNK, etc.)
            comment: Комментарий к изменению
        """
        try:
            fields = {
                "STATUS_ID": status,
            }
            
            if comment:
                fields["COMMENTS"] = comment
            
            data = {
                "id": lead_id,
                "fields": fields
            }
            
            await self._make_request("crm.lead.update", data)
            logger.info(f"Обновлен статус лида #{lead_id} на {status}")
            
        except Exception as e:
            logger.error(f"Ошибка обновления статуса лида {lead_id}: {e}")

    async def add_activity(self, entity_type: str, entity_id: int, subject: str, description: str):
        """
        Добавление активности (звонок, встреча, задача) к лиду/сделке
        
        Args:
            entity_type: Тип сущности (LEAD, DEAL, CONTACT, COMPANY)
            entity_id: ID сущности
            subject: Тема активности
            description: Описание активности
        """
        try:
            activity_fields = {
                "OWNER_TYPE_ID": self._get_entity_type_id(entity_type),
                "OWNER_ID": entity_id,
                "TYPE_ID": 1,  # Тип активности: звонок
                "SUBJECT": subject,
                "DESCRIPTION": description,
                "START_TIME": datetime.now().isoformat(),
                "END_TIME": datetime.now().isoformat(),
                "COMPLETED": "Y",
                "RESPONSIBLE_ID": self.user_id,
            }
            
            data = {"fields": activity_fields}
            
            result = await self._make_request("crm.activity.add", data)
            
            activity_id = result.get("result")
            logger.info(f"Добавлена активность #{activity_id} к {entity_type} #{entity_id}")
            
            return activity_id
            
        except Exception as e:
            logger.error(f"Ошибка добавления активности к {entity_type} {entity_id}: {e}")

    def _get_entity_type_id(self, entity_type: str) -> int:
        """Получение числового ID типа сущности"""
        entity_map = {
            "LEAD": 1,
            "DEAL": 2,
            "CONTACT": 3,
            "COMPANY": 4,
        }
        return entity_map.get(entity_type, 1)

    def _format_order_details(self, order_data: Dict[str, Any]) -> str:
        """Форматирование деталей заказа для комментария"""
        details = [
            f"💼 Заказ #{order_data['id']} с сайта EMC3.ru",
            f"📅 Дата заказа: {order_data.get('created_at', datetime.now().strftime('%d.%m.%Y %H:%M'))}",
            "",
            "🏢 Информация о компании:",
            f"  • Название: {order_data.get('company_name', 'Не указано')}",
            f"  • ИНН: {order_data.get('inn', 'Не указан')}",
            f"  • КПП: {order_data.get('kpp', 'Не указан')}",
            f"  • Адрес: {order_data.get('address', 'Не указан')}",
            "",
            "👤 Контактное лицо:",
            f"  • ФИО: {order_data.get('contact_person', 'Не указано')}",
            f"  • Email: {order_data.get('email', 'Не указан')}",
            f"  • Телефон: {order_data.get('phone', 'Не указан')}",
            "",
            "💰 Сумма заказа:",
            f"  • Общая стоимость: {order_data.get('total_amount', 0):,.2f} ₽",
            "",
            "📦 Состав заказа:",
        ]
        
        # Добавление товаров
        for i, item in enumerate(order_data.get('items', []), 1):
            details.extend([
                f"  {i}. {item.get('product_name', 'Товар')}",
                f"     • Артикул: {item.get('article', 'Не указан')}",
                f"     • Количество: {item.get('quantity', 1)} шт.",
                f"     • Цена: {item.get('unit_price', 0):,.2f} ₽",
                f"     • Сумма: {item.get('total_price', 0):,.2f} ₽",
                "",
            ])
        
        # Добавление комментария клиента
        if order_data.get('comment'):
            details.extend([
                "💬 Комментарий клиента:",
                f"  {order_data['comment']}",
                "",
            ])
        
        details.append("🔗 Заказ создан автоматически через сайт EMC3.ru")
        
        return "\n".join(details)

    def _format_product_specs(self, item: Dict[str, Any]) -> str:
        """Форматирование технических характеристик товара"""
        specs = []
        
        if item.get('article'):
            specs.append(f"Артикул: {item['article']}")
        
        if item.get('power'):
            specs.append(f"Мощность: {item['power']} Вт")
            
        if item.get('luminous_flux'):
            specs.append(f"Световой поток: {item['luminous_flux']} лм")
            
        if item.get('color_temperature'):
            specs.append(f"Цветовая температура: {item['color_temperature']} К")
            
        if item.get('protection_rating'):
            specs.append(f"Степень защиты: {item['protection_rating']}")
            
        if item.get('dimensions'):
            specs.append(f"Размеры: {item['dimensions']}")
            
        if item.get('warranty_years'):
            specs.append(f"Гарантия: {item['warranty_years']} лет")
        
        return " | ".join(specs) if specs else ""


# Глобальный экземпляр для использования в приложении
bitrix24 = Bitrix24Integration()