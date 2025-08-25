# EMC3 Lighting Store Backend

MVP Backend для интернет-магазина освещения EMC3, построенный на FastAPI + PostgreSQL + SQLAlchemy.

## Возможности

- ✅ FastAPI приложение с автоматической документацией
- ✅ PostgreSQL база данных с Docker Compose
- ✅ SQLAlchemy модели для товаров, категорий, пользователей и заказов
- ✅ Pydantic схемы для валидации данных
- ✅ JWT авторизация для B2B клиентов
- ✅ B2B ценообразование со скидками (5+, 10+, 50+ шт)
- ✅ API эндпоинты для CRUD операций
- ✅ Фильтрация товаров по мощности, световому потоку, цветовой температуре
- ✅ Поиск по артикулу и названию
- ✅ Пагинация для каталога
- ✅ Импорт данных из CSV файла (1,150 LED-светильников)
- ✅ Alembic миграции для управления схемой БД
- ✅ CORS настройки для фронтенда React

## Структура проекта

```
backend/
├── app/
│   ├── main.py              # FastAPI приложение
│   ├── database.py          # Подключение к БД
│   ├── models/             # SQLAlchemy модели
│   │   ├── products.py     # Модель товаров
│   │   ├── categories.py   # Модель категорий
│   │   ├── users.py        # Модель пользователей
│   │   └── orders.py       # Модель заказов
│   ├── schemas/            # Pydantic схемы
│   │   ├── products.py
│   │   ├── categories.py
│   │   ├── users.py
│   │   └── orders.py
│   ├── api/                # API роуты
│   │   ├── products.py     # CRUD товаров
│   │   ├── categories.py   # Управление категориями
│   │   ├── users.py        # Авторизация
│   │   └── orders.py       # Заказы
│   └── utils/
│       ├── auth.py         # JWT авторизация
│       ├── import_data.py  # Импорт из CSV
│       └── pricing.py      # B2B ценообразование
├── migrations/             # Alembic миграции
├── requirements.txt
├── docker-compose.yml      # PostgreSQL + pgAdmin
├── alembic.ini
├── import_script.py        # Скрипт импорта данных
└── .env                    # Переменные окружения
```

## Быстрый старт

### 1. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Запуск PostgreSQL

```bash
docker-compose up -d postgres
```

### 3. Настройка переменных окружения

Отредактируйте файл `.env` при необходимости:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/emc3_lighting
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Создание таблиц и импорт данных

```bash
# Автоматическое создание таблиц и импорт данных
python import_script.py
```

### 5. Запуск API сервера

```bash
# Запуск в режиме разработки
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступно по адресу: http://localhost:8000

## API Документация

После запуска сервера документация доступна по адресам:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Основные API эндпоинты

### Товары
- `GET /api/products` - список товаров с фильтрацией и пагинацией
- `GET /api/products/{id}` - детали товара
- `GET /api/products/{id}/price?quantity=N` - цена с B2B скидкой
- `POST /api/products` - создание товара
- `PUT /api/products/{id}` - обновление товара
- `DELETE /api/products/{id}` - удаление товара

### Категории
- `GET /api/categories` - иерархия категорий
- `GET /api/categories/flat` - плоский список категорий
- `GET /api/categories/{id}` - категория по ID
- `POST /api/categories` - создание категории
- `PUT /api/categories/{id}` - обновление категории
- `DELETE /api/categories/{id}` - удаление категории

### Авторизация
- `POST /api/auth/register` - регистрация B2B клиента
- `POST /api/auth/login` - авторизация (form-data)
- `POST /api/auth/login/json` - авторизация (JSON)
- `GET /api/auth/me` - информация о текущем пользователе
- `PUT /api/auth/me` - обновление профиля

### Заказы
- `POST /api/orders/calculate` - расчет корзины с B2B скидками
- `POST /api/orders` - создание заказа
- `GET /api/orders` - история заказов пользователя
- `GET /api/orders/{id}` - детали заказа
- `PUT /api/orders/{id}` - обновление заказа
- `DELETE /api/orders/{id}` - отмена заказа

## B2B Ценообразование

Система автоматических скидок:
- **5+ штук**: скидка 5%
- **10+ штук**: скидка 10%
- **50+ штук**: скидка 15%

## Фильтрация товаров

Доступные фильтры:
- `category_id` - ID категории
- `min_price` / `max_price` - диапазон цен
- `min_power` / `max_power` - диапазон мощности (Вт)
- `min_flux` / `max_flux` - диапазон светового потока (Лм)
- `color_temperature` - цветовая температура (К)
- `manufacturer` - производитель
- `search` - поиск по названию и артикулу

Пример запроса:
```
GET /api/products?category_id=1&min_power=80&max_power=150&search=highway&skip=0&limit=20
```

## Миграции базы данных

```bash
# Создание новой миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## Мониторинг базы данных

pgAdmin доступен по адресу: http://localhost:5050
- **Email**: admin@emc3.com
- **Password**: admin

## Модели данных

### Product (Товар)
- id, name, sku, price, description
- manufacturer, country
- power_watts, luminous_flux, color_temperature
- manufacturing_time
- seo_title, seo_description, seo_keywords
- images, category_id
- created_at, updated_at

### Category (Категория)
- id, name, slug, description
- parent_id (для иерархии)

### User (Пользователь)
- id, email, hashed_password
- company_name, first_name, last_name, phone
- user_type (wholesale/retail)
- is_active, is_verified
- created_at, updated_at

### Order (Заказ)
- id, user_id, total_amount, status
- delivery_address, delivery_city, delivery_postal_code
- contact_phone, contact_email, notes
- created_at, updated_at

### OrderItem (Позиция заказа)
- id, order_id, product_id
- quantity, unit_price, discount_percent

## Разработка

### Запуск в режиме разработки

```bash
# Установка зависимостей для разработки
pip install -r requirements.txt

# Запуск с автоперезагрузкой
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Тестирование API

Используйте Swagger UI по адресу http://localhost:8000/docs для интерактивного тестирования API.

### Логирование

Все операции импорта и критические ошибки логируются. Логи выводятся в консоль.

## Безопасность

- JWT токены для авторизации
- Хеширование паролей с помощью bcrypt
- Валидация данных через Pydantic
- CORS настройки для фронтенда
- Обработка ошибок и исключений

## Производительность

- Индексы на часто используемые поля (email, sku, category_id)
- Пагинация для больших списков
- Оптимизированные SQL запросы через SQLAlchemy
- Connection pooling для базы данных

## Поддержка

Для вопросов по API обращайтесь к документации Swagger UI или изучайте код в директории `app/`.