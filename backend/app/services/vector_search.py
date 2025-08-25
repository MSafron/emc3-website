"""
Сервис векторного поиска для EMC3 с интеграцией Supabase
Обеспечивает умный поиск товаров и персональные рекомендации
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import json
import logging
from datetime import datetime

import openai
from supabase import create_client, Client
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorSearchService:
    """Сервис для работы с векторным поиском товаров"""
    
    def __init__(self):
        """Инициализация сервиса"""
        try:
            # Подключение к Supabase
            self.supabase: Client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
            
            # Настройка OpenAI
            openai.api_key = settings.OPENAI_API_KEY
            
            # Параметры embedding
            self.embedding_model = "text-embedding-ada-002"
            self.embedding_dimension = 1536
            
            logger.info("VectorSearchService успешно инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации VectorSearchService: {e}")
            raise

    async def create_product_embedding(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создание векторного представления товара
        
        Args:
            product_data: Данные товара
            
        Returns:
            Результат сохранения в векторную БД
        """
        try:
            # Формируем богатый текст для embedding
            text_for_embedding = self._prepare_text_for_embedding(product_data)
            
            # Создаем embedding через OpenAI
            embedding = await self._create_openai_embedding(text_for_embedding)
            
            # Подготавливаем технические характеристики
            technical_specs = self._extract_technical_specs(product_data)
            
            # Подготавливаем метаданные
            metadata = {
                'price': float(product_data.get('price', 0)),
                'b2b_price': float(product_data.get('b2b_price', 0)),
                'stock_quantity': product_data.get('stock_quantity', 0),
                'weight': float(product_data.get('weight', 0)),
                'dimensions': product_data.get('dimensions', ''),
                'warranty_years': product_data.get('warranty_years', 0),
                'is_featured': product_data.get('is_featured', False),
                'tags': product_data.get('tags', '').split(',') if product_data.get('tags') else []
            }
            
            # Сохраняем в Supabase
            result = self.supabase.table('product_embeddings').upsert({
                'product_id': product_data['id'],
                'article': product_data['article'],
                'product_name': product_data['name'],
                'description': product_data.get('description', ''),
                'category_name': product_data.get('category_name', ''),
                'technical_specs': technical_specs,
                'embedding': embedding,
                'metadata': metadata,
                'updated_at': datetime.now().isoformat()
            }, on_conflict='product_id').execute()
            
            logger.info(f"Создан embedding для товара {product_data['article']}")
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Ошибка создания embedding для товара {product_data.get('article', 'unknown')}: {e}")
            raise

    async def search_products(
        self, 
        query: str, 
        limit: int = 20,
        threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск товаров по текстовому запросу
        
        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
            threshold: Минимальный порог сходства
            filters: Дополнительные фильтры
            
        Returns:
            Список найденных товаров с показателями релевантности
        """
        try:
            # Создаем embedding для поискового запроса
            query_embedding = await self._create_openai_embedding(query)
            
            # Выполняем поиск в Supabase
            result = self.supabase.rpc('search_similar_products', {
                'query_embedding': query_embedding,
                'match_threshold': threshold,
                'match_count': limit
            }).execute()
            
            search_results = result.data or []
            
            # Применяем дополнительные фильтры если есть
            if filters:
                search_results = self._apply_filters(search_results, filters)
            
            # Логируем поисковый запрос для аналитики
            await self._log_search_query(query, query_embedding, len(search_results))
            
            logger.info(f"Найдено {len(search_results)} товаров по запросу: {query}")
            return search_results
            
        except Exception as e:
            logger.error(f"Ошибка поиска товаров по запросу '{query}': {e}")
            return []

    async def get_product_recommendations(
        self, 
        product_id: int, 
        limit: int = 10,
        exclude_same_category: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Получение рекомендаций для товара
        
        Args:
            product_id: ID товара
            limit: Количество рекомендаций
            exclude_same_category: Исключить товары той же категории
            
        Returns:
            Список рекомендованных товаров
        """
        try:
            result = self.supabase.rpc('get_product_recommendations', {
                'target_product_id': product_id,
                'recommendation_count': limit
            }).execute()
            
            recommendations = result.data or []
            
            # Фильтруем по категориям если нужно
            if exclude_same_category and recommendations:
                # Получаем категорию исходного товара
                target_product = self.supabase.table('product_embeddings').select('category_name').eq('product_id', product_id).execute()
                
                if target_product.data:
                    target_category = target_product.data[0]['category_name']
                    recommendations = [
                        rec for rec in recommendations 
                        if rec.get('category_name') != target_category
                    ]
            
            logger.info(f"Получено {len(recommendations)} рекомендаций для товара {product_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Ошибка получения рекомендаций для товара {product_id}: {e}")
            return []

    async def get_similar_by_specs(
        self, 
        technical_specs: Dict[str, Any], 
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Поиск товаров по техническим характеристикам
        
        Args:
            technical_specs: Технические характеристики
            limit: Количество результатов
            
        Returns:
            Список похожих товаров
        """
        try:
            # Формируем запрос для поиска по техническим характеристикам
            query_parts = []
            
            if technical_specs.get('power'):
                query_parts.append(f"мощность {technical_specs['power']} ватт")
            
            if technical_specs.get('luminous_flux'):
                query_parts.append(f"световой поток {technical_specs['luminous_flux']} люмен")
                
            if technical_specs.get('color_temperature'):
                query_parts.append(f"цветовая температура {technical_specs['color_temperature']} кельвин")
                
            if technical_specs.get('protection_rating'):
                query_parts.append(f"степень защиты {technical_specs['protection_rating']}")
                
            if technical_specs.get('installation_area'):
                query_parts.append(f"для {technical_specs['installation_area']}")
            
            query = " ".join(query_parts)
            
            if not query:
                return []
            
            # Выполняем поиск
            return await self.search_products(query, limit=limit, threshold=0.6)
            
        except Exception as e:
            logger.error(f"Ошибка поиска по техническим характеристикам: {e}")
            return []

    async def update_product_embedding(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """
        Обновление embedding существующего товара
        
        Args:
            product_id: ID товара
            product_data: Обновленные данные товара
            
        Returns:
            Успешность обновления
        """
        try:
            # Удаляем старый embedding
            self.supabase.table('product_embeddings').delete().eq('product_id', product_id).execute()
            
            # Создаем новый
            await self.create_product_embedding(product_data)
            
            logger.info(f"Обновлен embedding для товара {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления embedding для товара {product_id}: {e}")
            return False

    async def delete_product_embedding(self, product_id: int) -> bool:
        """
        Удаление embedding товара
        
        Args:
            product_id: ID товара
            
        Returns:
            Успешность удаления
        """
        try:
            result = self.supabase.table('product_embeddings').delete().eq('product_id', product_id).execute()
            
            logger.info(f"Удален embedding для товара {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления embedding для товара {product_id}: {e}")
            return False

    async def get_search_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Получение аналитики поисковых запросов
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Статистика поисковых запросов
        """
        try:
            # Получаем данные за период
            from_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            result = self.supabase.table('search_analytics').select('*').gte('created_at', from_date).execute()
            
            analytics_data = result.data or []
            
            # Анализируем данные
            total_searches = len(analytics_data)
            unique_queries = len(set(item['search_query'] for item in analytics_data))
            avg_results = sum(item['results_count'] for item in analytics_data) / total_searches if total_searches > 0 else 0
            
            # Топ запросы
            query_counts = {}
            for item in analytics_data:
                query = item['search_query']
                query_counts[query] = query_counts.get(query, 0) + 1
            
            top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'total_searches': total_searches,
                'unique_queries': unique_queries,
                'average_results': round(avg_results, 2),
                'top_queries': top_queries,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения аналитики поиска: {e}")
            return {}

    def _prepare_text_for_embedding(self, product_data: Dict[str, Any]) -> str:
        """Подготовка текста для создания embedding"""
        parts = []
        
        # Основная информация
        if product_data.get('name'):
            parts.append(f"Название: {product_data['name']}")
            
        if product_data.get('article'):
            parts.append(f"Артикул: {product_data['article']}")
            
        if product_data.get('description'):
            parts.append(f"Описание: {product_data['description']}")
            
        if product_data.get('category_name'):
            parts.append(f"Категория: {product_data['category_name']}")
        
        # Технические характеристики
        if product_data.get('power'):
            parts.append(f"Мощность: {product_data['power']} Вт")
            
        if product_data.get('voltage'):
            parts.append(f"Напряжение: {product_data['voltage']}")
            
        if product_data.get('luminous_flux'):
            parts.append(f"Световой поток: {product_data['luminous_flux']} лм")
            
        if product_data.get('luminous_efficacy'):
            parts.append(f"Светоотдача: {product_data['luminous_efficacy']} лм/Вт")
            
        if product_data.get('color_temperature'):
            parts.append(f"Цветовая температура: {product_data['color_temperature']} К")
            
        if product_data.get('color_rendering_index'):
            parts.append(f"Индекс цветопередачи: {product_data['color_rendering_index']} CRI")
            
        if product_data.get('beam_angle'):
            parts.append(f"Угол свечения: {product_data['beam_angle']}°")
            
        if product_data.get('protection_rating'):
            parts.append(f"Степень защиты: {product_data['protection_rating']}")
            
        if product_data.get('operating_temperature'):
            parts.append(f"Рабочая температура: {product_data['operating_temperature']}")
            
        if product_data.get('lifespan_hours'):
            parts.append(f"Срок службы: {product_data['lifespan_hours']} часов")
            
        if product_data.get('dimming_support'):
            parts.append("Поддержка диммирования")
            
        if product_data.get('led_chip_brand'):
            parts.append(f"LED чип: {product_data['led_chip_brand']}")
            
        if product_data.get('driver_brand'):
            parts.append(f"Драйвер: {product_data['driver_brand']}")
            
        if product_data.get('housing_material'):
            parts.append(f"Материал корпуса: {product_data['housing_material']}")
            
        if product_data.get('diffuser_type'):
            parts.append(f"Рассеиватель: {product_data['diffuser_type']}")
            
        if product_data.get('mounting_type'):
            parts.append(f"Тип монтажа: {product_data['mounting_type']}")
            
        if product_data.get('installation_area'):
            parts.append(f"Область применения: {product_data['installation_area']}")
            
        if product_data.get('dimensions'):
            parts.append(f"Размеры: {product_data['dimensions']}")
            
        if product_data.get('weight'):
            parts.append(f"Вес: {product_data['weight']} кг")
            
        if product_data.get('warranty_years'):
            parts.append(f"Гарантия: {product_data['warranty_years']} лет")
        
        # Теги
        if product_data.get('tags'):
            parts.append(f"Теги: {product_data['tags']}")
        
        return "\n".join(parts)

    def _extract_technical_specs(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлечение технических характеристик"""
        return {
            'power': product_data.get('power'),
            'voltage': product_data.get('voltage'),
            'current': product_data.get('current'),
            'luminous_flux': product_data.get('luminous_flux'),
            'luminous_efficacy': product_data.get('luminous_efficacy'),
            'color_temperature': product_data.get('color_temperature'),
            'color_rendering_index': product_data.get('color_rendering_index'),
            'beam_angle': product_data.get('beam_angle'),
            'protection_rating': product_data.get('protection_rating'),
            'operating_temperature': product_data.get('operating_temperature'),
            'lifespan_hours': product_data.get('lifespan_hours'),
            'dimming_support': product_data.get('dimming_support'),
            'led_chip_brand': product_data.get('led_chip_brand'),
            'driver_brand': product_data.get('driver_brand'),
            'housing_material': product_data.get('housing_material'),
            'diffuser_type': product_data.get('diffuser_type'),
            'mounting_type': product_data.get('mounting_type'),
            'installation_area': product_data.get('installation_area'),
        }

    async def _create_openai_embedding(self, text: str) -> List[float]:
        """Создание embedding через OpenAI API"""
        try:
            response = await openai.Embedding.acreate(
                model=self.embedding_model,
                input=text
            )
            
            return response['data'][0]['embedding']
            
        except Exception as e:
            logger.error(f"Ошибка создания OpenAI embedding: {e}")
            raise

    def _apply_filters(
        self, 
        search_results: List[Dict[str, Any]], 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Применение дополнительных фильтров к результатам поиска"""
        filtered_results = search_results
        
        # Фильтр по категории
        if filters.get('category'):
            filtered_results = [
                item for item in filtered_results 
                if item.get('category_name', '').lower() == filters['category'].lower()
            ]
        
        # Фильтр по мощности
        if filters.get('power_min') or filters.get('power_max'):
            power_min = filters.get('power_min', 0)
            power_max = filters.get('power_max', float('inf'))
            
            # Здесь нужно получить дополнительные данные из основной БД
            # Пока пропускаем этот фильтр
        
        return filtered_results

    async def _log_search_query(
        self, 
        query: str, 
        query_embedding: List[float], 
        results_count: int,
        user_session: Optional[str] = None
    ):
        """Логирование поискового запроса для аналитики"""
        try:
            self.supabase.table('search_analytics').insert({
                'user_session': user_session or 'anonymous',
                'search_query': query,
                'search_embedding': query_embedding,
                'results_count': results_count,
                'created_at': datetime.now().isoformat()
            }).execute()
            
        except Exception as e:
            logger.warning(f"Ошибка логирования поискового запроса: {e}")


# Глобальный экземпляр сервиса
vector_search_service = VectorSearchService()