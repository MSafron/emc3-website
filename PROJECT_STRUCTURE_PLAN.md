# План модульной архитектуры проекта

## 📁 Предлагаемая структура каталогов

```
lighting_data_processor/
├── README.md
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # Точка входа приложения
│   ├── api/                       # REST API
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── products.py    # API для работы с товарами
│   │   │   │   ├── import.py      # API для импорта данных
│   │   │   │   └── export.py     # API для экспорта
│   │   │   └── dependencies.py   # Зависимости FastAPI
│   │   └── middleware.py          # Middleware для логирования и CORS
│   │
│   ├── core/                      # Основная бизнес-логика
│   │   ├── __init__.py
│   │   ├── processor.py           # Главный процессор данных
│   │   ├── extractors/            # Извлечение характеристик
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Базовый класс экстрактора
│   │   │   ├── power_extractor.py
│   │   │   ├── flux_extractor.py
│   │   │   ├── temperature_extractor.py
│   │   │   └── category_extractor.py
│   │   ├── validators/             # Валидация данных
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── product_validator.py
│   │   │   └── price_validator.py
│   │   └── transformers/          # Преобразование данных
│   │       ├── __init__.py
│       │   ├── base.py
│       │   ├── seo_generator.py
│       │   └── text_cleaner.py
│   │
│   ├── parsers/                   # Парсеры разных форматов
│   │   ├── __init__.py
│   │   ├── base.py               # Базовый интерфейс парсера
│   │   ├── csv_parser.py         # CSV парсер
│   │   ├── excel_parser.py       # Excel парсер (будущее)
│   │   └── xml_parser.py         # XML парсер (будущее)
│   │
│   ├── exporters/                 # Экспортеры в разные форматы
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── csv_exporter.py       # Экспорт в CSV
│   │   ├── excel_exporter.py     # Экспорт в Excel
│   │   └── json_exporter.py      # Экспорт в JSON
│   │
│   ├── integrations/             # Интеграции с внешними системами
│   │   ├── __init__.py
│   │   ├── bitrix24/
│   │   │   ├── __init__.py
│   │   │   ├── client.py         # API клиент Битрикс24
│   │   │   ├── mapper.py         # Маппинг данных
│   │   │   └── uploader.py       # Загрузчик данных
│   │   └── image_services/
│   │       ├── __init__.py
│   │       ├── downloader.py     # Загрузка изображений
│   │       ├── processor.py      # Обработка изображений
│   │       └── uploader.py       # Загрузка в хранилище
│   │
│   ├── models/                   # Модели данных
│   │   ├── __init__.py
│   │   ├── product.py           # Модель товара
│   │   ├── category.py          # Модель категории
│   │   └── import_session.py    # Модель сессии импорта
│   │
│   ├── database/                # База данных
│   │   ├── __init__.py
│   │   ├── connection.py        # Подключение к БД
│   │   ├── migrations/          # Миграции
│   │   └── repositories/        # Репозитории для работы с данными
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── product_repository.py
│   │       └── import_repository.py
│   │
│   ├── services/                # Сервисы бизнес-логики
│   │   ├── __init__.py
│   │   ├── product_service.py   # Сервис работы с товарами
│   │   ├── import_service.py    # Сервис импорта
│   │   ├── export_service.py    # Сервис экспорта
│   │   └── image_service.py     # Сервис работы с изображениями
│   │
│   ├── utils/                   # Утилиты
│   │   ├── __init__.py
│   │   ├── logger.py           # Настройка логирования
│   │   ├── cache.py            # Кэширование
│   │   ├── helpers.py          # Вспомогательные функции
│   │   └── decorators.py       # Декораторы
│   │
│   └── web/                    # Веб-интерфейс
│       ├── __init__.py
│       ├── static/             # Статические файлы
│       ├── templates/          # HTML шаблоны
│       └── routes.py           # Веб-маршруты
│
├── config/                     # Конфигурация
│   ├── __init__.py
│   ├── settings.py            # Основные настройки
│   ├── categories.json        # Настройки категорий
│   ├── extraction_rules.json  # Правила извлечения
│   └── export_templates.json  # Шаблоны экспорта
│
├── tests/                     # Тесты
│   ├── __init__.py
│   ├── conftest.py           # Настройки pytest
│   ├── fixtures/             # Тестовые данные
│   │   ├── sample_data.csv
│   │   └── expected_results.json
│   ├── unit/                 # Модульные тесты
│   │   ├── test_extractors.py
│   │   ├── test_validators.py
│   │   └── test_transformers.py
│   ├── integration/          # Интеграционные тесты
│   │   ├── test_processor.py
│   │   └── test_api.py
│   └── e2e/                  # End-to-end тесты
│       └── test_full_cycle.py
│
├── scripts/                   # Скрипты для развертывания и утилит
│   ├── migrate.py            # Миграции БД
│   ├── seed_data.py          # Наполнение тестовыми данными
│   └── backup.py             # Резервное копирование
│
├── docs/                     # Документация
│   ├── api.md               # Документация API
│   ├── configuration.md     # Настройка системы
│   ├── deployment.md        # Развертывание
│   └── examples/            # Примеры использования
│       ├── basic_usage.py
│       └── advanced_usage.py
│
└── data/                    # Директория для данных
    ├── input/               # Входные файлы
    ├── output/              # Выходные файлы
    ├── cache/               # Кэш
    └── logs/                # Логи
```

## 🔧 Ключевые компоненты архитектуры

### 1. Core Layer (Основной слой)

#### ProductProcessor
```python
class ProductProcessor:
    """Главный процессор для обработки данных товаров"""
    
    def __init__(self, config: Config):
        self.extractors = ExtractorFactory.create_all()
        self.validators = ValidatorFactory.create_all()
        self.transformers = TransformerFactory.create_all()
    
    async def process_batch(self, products: List[RawProduct]) -> List[ProcessedProduct]:
        """Обработка батча товаров"""
        pass
    
    async def process_file(self, file_path: str) -> ProcessingResult:
        """Обработка целого файла"""
        pass
```

#### ExtractorFactory
```python
class ExtractorFactory:
    """Фабрика для создания экстракторов характеристик"""
    
    @staticmethod
    def create_power_extractor() -> PowerExtractor:
        pass
    
    @staticmethod
    def create_flux_extractor() -> FluxExtractor:
        pass
```

### 2. Parser Layer (Слой парсинга)

#### BaseParser
```python
from abc import ABC, abstractmethod

class BaseParser(ABC):
    """Базовый интерфейс для всех парсеров"""
    
    @abstractmethod
    async def parse(self, file_path: str) -> Iterator[RawProduct]:
        """Парсинг файла с возвращением итератора"""
        pass
    
    @abstractmethod
    def validate_format(self, file_path: str) -> bool:
        """Проверка формата файла"""
        pass
```

### 3. Service Layer (Слой сервисов)

#### ImportService
```python
class ImportService:
    """Сервис для управления процессом импорта"""
    
    def __init__(self, 
                 processor: ProductProcessor,
                 repository: ProductRepository,
                 bitrix_client: Bitrix24Client):
        pass
    
    async def import_from_file(self, file_path: str) -> ImportResult:
        """Полный цикл импорта из файла"""
        pass
    
    async def get_import_status(self, session_id: str) -> ImportStatus:
        """Получение статуса импорта"""
        pass
```

### 4. Integration Layer (Слой интеграций)

#### Bitrix24Client
```python
class Bitrix24Client:
    """Клиент для работы с API Битрикс24"""
    
    async def upload_product(self, product: ProcessedProduct) -> str:
        """Загрузка товара в Битрикс24"""
        pass
    
    async def upload_batch(self, products: List[ProcessedProduct]) -> BatchResult:
        """Пакетная загрузка товаров"""
        pass
    
    async def upload_images(self, product_id: str, images: List[str]) -> bool:
        """Загрузка изображений товара"""
        pass
```

## 🔄 Паттерны проектирования

### 1. Factory Pattern
- `ExtractorFactory` - создание экстракторов характеристик
- `ParserFactory` - создание парсеров для разных форматов
- `ExporterFactory` - создание экспортеров

### 2. Strategy Pattern
- `ExtractionStrategy` - разные стратегии извлечения данных
- `ValidationStrategy` - разные стратегии валидации
- `ExportStrategy` - разные форматы экспорта

### 3. Repository Pattern
- `ProductRepository` - работа с данными товаров
- `ImportSessionRepository` - работа с сессиями импорта

### 4. Observer Pattern
- `ProcessingObserver` - отслеживание прогресса обработки
- `ErrorObserver` - отслеживание ошибок

## 📦 Модели данных

### RawProduct
```python
@dataclass
class RawProduct:
    """Необработанные данные товара из источника"""
    name: str
    description: str
    price: str
    sku: str
    category: str
    manufacturer: str
    country: str
    raw_properties: Dict[str, str]
```

### ProcessedProduct
```python
@dataclass
class ProcessedProduct:
    """Обработанные данные товара"""
    id: Optional[str]
    name: str
    description: str
    price: Decimal
    sku: str
    category_level1: str
    category_level2: str
    manufacturer: str
    country: str
    power: Optional[int]
    luminous_flux: Optional[int]
    color_temperature: Optional[int]
    manufacturing_time: str
    seo_title: str
    seo_description: str
    seo_keywords: str
    images: List[str]
    created_at: datetime
    updated_at: datetime
```

## 🔧 Конфигурация

### settings.py
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:pass@localhost/lighting"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Bitrix24
    bitrix24_webhook_url: str
    bitrix24_access_token: str
    
    # File processing
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    batch_size: int = 100
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
```

## 🚀 Этапы миграции

### Этап 1: Создание базовой структуры
1. Создание директорий и базовых файлов
2. Настройка зависимостей и окружения
3. Реализация базовых моделей данных

### Этап 2: Миграция парсинга
1. Перенос логики парсинга CSV в `CSVParser`
2. Создание базового интерфейса `BaseParser`
3. Тестирование совместимости с существующими данными

### Этап 3: Миграция извлечения характеристик
1. Разделение методов извлечения на отдельные классы
2. Создание фабрики экстракторов
3. Настройка через конфигурацию

### Этап 4: Добавление API и веб-интерфейса
1. Реализация REST API с FastAPI
2. Создание простого веб-интерфейса
3. Интеграция с очередями задач

### Этап 5: Интеграция с Битрикс24
1. Реализация API клиента
2. Автоматическая загрузка данных
3. Обработка изображений

---
*План создан: 2025-08-20*
*Статус: Готов к реализации*