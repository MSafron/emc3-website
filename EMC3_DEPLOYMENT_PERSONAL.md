# 🚀 Развертывание EMC3.ru на российской инфраструктуре

**Персональное руководство с учетом вашей инфраструктуры**

## 📋 Ваши ресурсы

### ✅ Домен и DNS
- **Домен**: emc3.ru (REG.RU)
- **Премиум DNS**: REG.RU
- **Управление**: Панель REG.RU

### ✅ Серверы
- **Российский VPS**: REG.RU (для соответствия 152-ФЗ)
- **Зарубежный VPS**: my.adminvps.ru (база данных)
- **Nginx**: https://nginx.safronai.ru
- **Portainer**: https://188.214.107.67:9443/#!/3/docker/stacks

### ✅ Инструменты
- **GitHub** (репозиторий)
- **FileZilla Pro** (загрузка файлов)
- **Termius** (SSH доступ)
- **Cloudflare** (CDN и защита)

### ✅ Дополнительно
- **Конструктор сайтов REG.RU** (резерв)
- **Mail-1 хостинг** (корпоративная почта)
- **Битрикс24** (CRM для обработки заявок)
- **Supabase Vector DB**: https://sub.safronai.ru (умный поиск товаров)

---

## 🎯 ПЛАН РАЗВЕРТЫВАНИЯ

### Этап 1: База данных на my.adminvps.ru
### Этап 2: Настройка векторной базы Supabase
### Этап 3: Backend на REG.RU VPS
### Этап 4: Frontend на REG.RU VPS
### Этап 5: Интеграция с Битрикс24
### Этап 6: Настройка обслуживания

---

## 🗄️ ЭТАП 1: База данных PostgreSQL

### 1.1 Подключение к серверу my.adminvps.ru

```bash
# Через Termius подключитесь к серверу
ssh root@my.adminvps.ru
```

### 1.2 Установка PostgreSQL через Docker

```bash
# Создание папки проекта
mkdir -p /opt/emc3-db
cd /opt/emc3-db

# Создание docker-compose.yml для базы
nano docker-compose.yml
```

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: emc3_postgres
    environment:
      POSTGRES_DB: emc3_production
      POSTGRES_USER: emc3_user
      POSTGRES_PASSWORD: EMC3_SecurePass_2024!
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --locale=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    restart: unless-stopped
    command: >
      postgres 
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c work_mem=4MB

  pgadmin:
    image: dpage/pgadmin4
    container_name: emc3_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@emc3.ru
      PGADMIN_DEFAULT_PASSWORD: AdminEMC3_2024!
    ports:
      - "8080:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    restart: unless-stopped

volumes:
  postgres_data:
  pgadmin_data:
```

```bash
# Запуск базы данных
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### 1.3 Настройка безопасности PostgreSQL

```bash
# Создание файрвола
ufw allow 5432/tcp
ufw allow 8080/tcp

# Только для вашего IP и сервера REG.RU
ufw allow from ВАШ_IP to any port 5432
ufw allow from IP_REG_RU_VPS to any port 5432
```

---

## 🧠 ЭТАП 2: Настройка векторной базы Supabase

### 2.1 Подключение к существующей Supabase

У вас уже развернута Supabase по адресу: https://sub.safronai.ru

### 2.2 Создание таблиц для векторного поиска

Подключитесь к вашей Supabase и выполните SQL:

```sql
-- Включение расширения vector
CREATE EXTENSION IF NOT EXISTS vector;

-- Таблица для векторов товаров
CREATE TABLE product_embeddings (
    id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    article VARCHAR(100) NOT NULL,
    product_name TEXT NOT NULL,
    description TEXT,
    category_name VARCHAR(255),
    technical_specs JSONB,
    embedding vector(1536), -- OpenAI embeddings размерность
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для быстрого поиска
CREATE INDEX ON product_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON product_embeddings (product_id);
CREATE INDEX ON product_embeddings (article);
CREATE INDEX ON product_embeddings USING GIN (technical_specs);

-- Таблица для поисковых запросов пользователей
CREATE TABLE search_analytics (
    id BIGSERIAL PRIMARY KEY,
    user_session VARCHAR(255),
    search_query TEXT NOT NULL,
    search_embedding vector(1536),
    results_count INTEGER,
    clicked_products INTEGER[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индекс для аналитики поиска
CREATE INDEX ON search_analytics USING ivfflat (search_embedding vector_cosine_ops) WITH (lists = 50);

-- Функция для поиска похожих товаров
CREATE OR REPLACE FUNCTION search_similar_products(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.8,
    match_count int DEFAULT 20
)
RETURNS TABLE (
    product_id int,
    article varchar,
    product_name text,
    category_name varchar,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        pe.product_id,
        pe.article,
        pe.product_name,
        pe.category_name,
        1 - (pe.embedding <=> query_embedding) as similarity
    FROM product_embeddings pe
    WHERE 1 - (pe.embedding <=> query_embedding) > match_threshold
    ORDER BY pe.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Функция для рекомендаций на основе товара
CREATE OR REPLACE FUNCTION get_product_recommendations(
    target_product_id int,
    recommendation_count int DEFAULT 10
)
RETURNS TABLE (
    product_id int,
    article varchar,
    product_name text,
    similarity float
)
LANGUAGE plpgsql
AS $$
DECLARE
    target_embedding vector(1536);
BEGIN
    -- Получаем embedding целевого товара
    SELECT embedding INTO target_embedding
    FROM product_embeddings
    WHERE product_embeddings.product_id = target_product_id;
    
    IF target_embedding IS NULL THEN
        RETURN;
    END IF;
    
    RETURN QUERY
    SELECT
        pe.product_id,
        pe.article,
        pe.product_name,
        1 - (pe.embedding <=> target_embedding) as similarity
    FROM product_embeddings pe
    WHERE pe.product_id != target_product_id
    ORDER BY pe.embedding <=> target_embedding
    LIMIT recommendation_count;
END;
$$;
```

### 2.3 Настройка API ключей

1. В панели Supabase получите:
   - **Project URL**: https://sub.safronai.ru
   - **Anon Key**: ваш_публичный_ключ
   - **Service Role Key**: ваш_приватный_ключ

2. Добавьте в `.env` backend:

```bash
# Supabase Vector Database
SUPABASE_URL=https://sub.safronai.ru
SUPABASE_ANON_KEY=ваш_публичный_ключ
SUPABASE_SERVICE_KEY=ваш_приватный_ключ

# OpenAI для создания embeddings
OPENAI_API_KEY=ваш_openai_ключ
```

---

## 🖥️ ЭТАП 3: Российский VPS на REG.RU

### 2.1 Заказ и настройка VPS

1. **В панели REG.RU**:
   - Закажите VPS минимум 2GB RAM, 20GB SSD
   - Выберите Ubuntu 22.04 LTS
   - Получите IP адрес

2. **Первоначальная настройка**:
```bash
# Подключение через Termius
ssh root@IP_ВАШЕГО_REG_RU_VPS

# Обновление системы
apt update && apt upgrade -y

# Установка необходимого ПО
apt install -y curl wget git nano ufw fail2ban

# Настройка файрвола
ufw allow ssh
ufw allow 80
ufw allow 443
ufw enable
```

### 2.2 Установка Docker

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Проверка
docker --version
docker-compose --version
```

### 2.3 Установка Nginx

```bash
apt install nginx -y
systemctl enable nginx
systemctl start nginx
```

---

## 📂 ЭТАП 4: Развертывание приложения

### 4.1 Клонирование проекта с GitHub

```bash
# Создание рабочей директории
mkdir -p /opt/emc3
cd /opt/emc3

# Клонирование репозитория
git clone https://github.com/ВАШ_USERNAME/emc3-website.git .

# Настройка прав
chown -R www-data:www-data /opt/emc3
```

### 4.2 Конфигурация Backend

```bash
# Создание .env для production
cd /opt/emc3/backend
cp .env.example .env
nano .env
```

```bash
# .env для production
DATABASE_URL=postgresql://emc3_user:EMC3_SecurePass_2024!@my.adminvps.ru:5432/emc3_production
SECRET_KEY=ваш_уникальный_секретный_ключ_32_символа_минимум
DEBUG=False
CORS_ORIGINS=["https://emc3.ru", "https://www.emc3.ru"]

# Supabase Vector Database
SUPABASE_URL=https://sub.safronai.ru
SUPABASE_ANON_KEY=ваш_публичный_ключ
SUPABASE_SERVICE_KEY=ваш_приватный_ключ

# OpenAI для векторного поиска
OPENAI_API_KEY=ваш_openai_ключ

# Битрикс24 интеграция
BITRIX24_WEBHOOK_URL=https://ваш_домен.bitrix24.ru/rest/1/ваш_webhook_код/
BITRIX24_DOMAIN=ваш_домен.bitrix24.ru
BITRIX24_USER_ID=1

# Email настройки (Mail-1)
SMTP_HOST=smtp.mail.ru
SMTP_PORT=587
SMTP_USER=noreply@emc3.ru
SMTP_PASSWORD=ваш_пароль_почты
SMTP_FROM=noreply@emc3.ru

# Настройки безопасности
ALLOWED_HOSTS=emc3.ru,www.emc3.ru
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 4.3 Конфигурация Frontend

```bash
cd /opt/emc3/frontend
nano .env.production
```

```bash
# .env.production
VITE_API_URL=https://api.emc3.ru
VITE_APP_TITLE=EMC3 - LED освещение для бизнеса
VITE_BITRIX24_DOMAIN=ваш_домен.bitrix24.ru
```

### 4.4 Docker Compose для всего проекта

```bash
cd /opt/emc3
nano docker-compose.production.yml
```

```yaml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.production
    container_name: emc3_backend
    environment:
      - DATABASE_URL=postgresql://emc3_user:EMC3_SecurePass_2024!@my.adminvps.ru:5432/emc3_production
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/logs:/app/logs
    restart: unless-stopped
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.production
    container_name: emc3_frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    depends_on:
      - backend

  redis:
    image: redis:7-alpine
    container_name: emc3_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### 4.5 Создание Dockerfile для production

**Backend Dockerfile.production:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание пользователя
RUN useradd -m -u 1000 emc3user
RUN chown -R emc3user:emc3user /app
USER emc3user

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Frontend Dockerfile.production:**
```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

---

## 🌐 ЭТАП 5: Настройка Nginx и SSL

### 5.1 Конфигурация Nginx

```bash
nano /etc/nginx/sites-available/emc3.ru
```

```nginx
# /etc/nginx/sites-available/emc3.ru
server {
    listen 80;
    server_name emc3.ru www.emc3.ru;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name emc3.ru www.emc3.ru;

    # SSL сертификаты (будут созданы позже)
    ssl_certificate /etc/letsencrypt/live/emc3.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/emc3.ru/privkey.pem;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Безопасность
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # API проксирование
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # Кеширование статических файлов
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Ограничение размера загрузки
    client_max_body_size 10M;

    # Логи
    access_log /var/log/nginx/emc3.ru.access.log;
    error_log /var/log/nginx/emc3.ru.error.log;
}
```

```bash
# Активация конфига
ln -s /etc/nginx/sites-available/emc3.ru /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 5.2 SSL сертификат

```bash
# Установка Certbot
apt install certbot python3-certbot-nginx -y

# Получение сертификата
certbot --nginx -d emc3.ru -d www.emc3.ru --email admin@emc3.ru --agree-tos --non-interactive

# Автообновление
crontab -e
# Добавить: 0 3 * * * certbot renew --quiet
```

---

## 🔗 ЭТАП 6: Настройка DNS в REG.RU

### 6.1 DNS записи

В панели REG.RU → DNS-сервер:

```
Тип: A
Имя: @
Значение: IP_ВАШЕГО_REG_RU_VPS
TTL: 300

Тип: A
Имя: www
Значение: IP_ВАШЕГО_REG_RU_VPS
TTL: 300

Тип: A
Имя: api
Значение: IP_ВАШЕГО_REG_RU_VPS
TTL: 300

Тип: MX
Имя: @
Значение: mx1.mail.ru
Приоритет: 10

Тип: TXT
Имя: @
Значение: "v=spf1 include:_spf.mail.ru ~all"
```

---

## 📊 ЭТАП 6: Интеграция с Битрикс24

### 6.1 Настройка вебхука в Битрикс24

1. **В Битрикс24**:
   - Приложения → Разработчикам → Другое → Входящий вебхук
   - Скопируйте URL вебхука

2. **Создание обработчика заявок**:

```python
# backend/app/integrations/bitrix24.py
import httpx
from app.core.config import settings

class Bitrix24Integration:
    def __init__(self):
        self.webhook_url = settings.BITRIX24_WEBHOOK_URL
        
    async def create_lead(self, order_data: dict):
        """Создание лида в Битрикс24"""
        lead_data = {
            "fields": {
                "TITLE": f"Заявка на светильники #{order_data['id']}",
                "NAME": order_data['company_name'],
                "COMPANY_TITLE": order_data['company_name'],
                "PHONE": [{"VALUE": order_data['phone'], "VALUE_TYPE": "WORK"}],
                "EMAIL": [{"VALUE": order_data['email'], "VALUE_TYPE": "WORK"}],
                "COMMENTS": self._format_order_items(order_data['items']),
                "SOURCE_ID": "WEB",
                "STATUS_ID": "NEW",
                "CURRENCY_ID": "RUB",
                "OPPORTUNITY": order_data['total_amount']
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.webhook_url}crm.lead.add",
                json=lead_data
            )
            return response.json()
    
    def _format_order_items(self, items):
        """Форматирование товаров для комментария"""
        formatted = "Состав заказа:\n"
        for item in items:
            formatted += f"- {item['product_name']} (арт. {item['article']}) - {item['quantity']} шт. x {item['unit_price']} ₽\n"
        return formatted
```

### 6.2 Автоматическое выставление счетов

```python
# backend/app/integrations/invoice.py
async def create_invoice_in_bitrix(lead_id: int, order_data: dict):
    """Создание счета в Битрикс24"""
    invoice_data = {
        "fields": {
            "ORDER_TOPIC": f"Счет на оплату #{order_data['id']}",
            "LID_ID": lead_id,
            "STATUS_ID": "N",
            "PRICE": order_data['total_amount'],
            "CURRENCY": "RUB",
            "PERSON_TYPE_ID": 2,  # Юридическое лицо
            "PAY_SYSTEM_ID": 1,   # Банковский перевод
            "DELIVERY_ID": 1,     # Самовывоз
        }
    }
    
    # Добавление товаров в счет
    for item in order_data['items']:
        invoice_data["fields"][f"PRODUCT_{item['id']}"] = {
            "PRODUCT_ID": item['product_id'],
            "PRODUCT_NAME": item['product_name'],
            "PRICE": item['unit_price'],
            "QUANTITY": item['quantity']
        }
```

---

## 🚀 ЭТАП 7: Запуск проекта

### 7.1 Сборка и запуск

```bash
cd /opt/emc3

# Сборка образов
docker-compose -f docker-compose.production.yml build

# Запуск всех сервисов
docker-compose -f docker-compose.production.yml up -d

# Проверка статуса
docker-compose -f docker-compose.production.yml ps

# Просмотр логов
docker-compose -f docker-compose.production.yml logs -f
```

### 7.2 Инициализация базы данных

```bash
# Запуск миграций
docker-compose -f docker-compose.production.yml exec backend python -m alembic upgrade head

# Создание суперпользователя
docker-compose -f docker-compose.production.yml exec backend python -c "
from app.core.security import get_password_hash
from app.models.users import User
from app.database import SessionLocal

db = SessionLocal()
admin = User(
    email='admin@emc3.ru',
    company_name='EMC3 Admin',
    contact_person='Администратор',
    phone='+7 (999) 999-99-99',
    hashed_password=get_password_hash('AdminEMC3_2024!'),
    is_active=True,
    is_verified=True,
    user_type='company'
)
db.add(admin)
db.commit()
print('Админ создан!')
"
```

---

## 🔧 ОБСЛУЖИВАНИЕ И УПРАВЛЕНИЕ САЙТОМ

### 8.1 Добавление товаров

**Способ 1: Через API (рекомендуется)**

```bash
# Скрипт загрузки товаров из CSV
# backend/scripts/import_products.py

import pandas as pd
from app.database import SessionLocal
from app.models.products import Product

def import_from_csv(file_path):
    df = pd.read_csv(file_path, encoding='utf-8')
    db = SessionLocal()
    
    for _, row in df.iterrows():
        product = Product(
            name=row['name'],
            article=row['article'],
            category_id=row['category_id'],
            description=row['description'],
            price=row['price'],
            b2b_price=row['b2b_price'],
            power=row['power'],
            luminous_flux=row['luminous_flux'],
            color_temperature=row['color_temperature'],
            # ... другие поля
        )
        db.add(product)
    
    db.commit()
    print(f"Импортировано {len(df)} товаров")

# Запуск импорта
if __name__ == "__main__":
    import_from_csv("/path/to/products.csv")
```

**Способ 2: Админ-панель (простой)**

Создание простой админки:

```python
# backend/app/admin/products.py
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

@router.get("/products")
async def admin_products():
    """Страница управления товарами"""
    # HTML форма для добавления/редактирования товаров
    pass

@router.post("/products/upload")
async def upload_products_csv(file: UploadFile = File(...)):
    """Загрузка товаров из CSV"""
    # Обработка загруженного файла
    pass
```

### 8.2 Обновление цен

**Автоматическое обновление через файл:**

```bash
# Создание скрипта обновления цен
nano /opt/emc3/scripts/update_prices.py
```

```python
import pandas as pd
from sqlalchemy import create_engine
import os

def update_prices_from_csv(csv_file):
    """Обновление цен из CSV файла"""
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    # Загрузка новых цен
    df = pd.read_csv(csv_file)
    
    with engine.connect() as conn:
        for _, row in df.iterrows():
            conn.execute(
                "UPDATE products SET price = %s, b2b_price = %s WHERE article = %s",
                (row['price'], row['b2b_price'], row['article'])
            )
    
    print(f"Обновлено цен: {len(df)}")

# Автоматический запуск
if __name__ == "__main__":
    update_prices_from_csv("/opt/emc3/data/new_prices.csv")
```

**Настройка автоматического обновления:**

```bash
# Добавление в cron для ежедневного обновления
crontab -e

# Каждый день в 6:00 утра
0 6 * * * cd /opt/emc3 && python scripts/update_prices.py >> /var/log/emc3_price_update.log 2>&1
```

### 9.5 Мониторинг и логи

**Настройка мониторинга:**

```bash
# Создание скрипта мониторинга
nano /opt/emc3/scripts/monitor.sh
```

```bash
#!/bin/bash

# Проверка работы сервисов
check_service() {
    if ! docker-compose -f /opt/emc3/docker-compose.production.yml ps | grep -q "Up"; then
        echo "$(date): Сервис не работает!" >> /var/log/emc3_monitor.log
        # Перезапуск
        cd /opt/emc3
        docker-compose -f docker-compose.production.yml restart
    fi
}

# Проверка места на диске
check_disk_space() {
    USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $USAGE -gt 80 ]; then
        echo "$(date): Мало места на диске: ${USAGE}%" >> /var/log/emc3_monitor.log
    fi
}

# Проверка SSL сертификата
check_ssl() {
    DAYS=$(echo | openssl s_client -servername emc3.ru -connect emc3.ru:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2 | xargs -I {} date -d {} +%s)
    NOW=$(date +%s)
    DIFF=$(( ($DAYS - $NOW) / 86400 ))
    
    if [ $DIFF -lt 30 ]; then
        echo "$(date): SSL сертификат истекает через $DIFF дней!" >> /var/log/emc3_monitor.log
    fi
}

check_service
check_disk_space
check_ssl
```

```bash
# Автоматический мониторинг каждые 5 минут
chmod +x /opt/emc3/scripts/monitor.sh
crontab -e
# Добавить: */5 * * * * /opt/emc3/scripts/monitor.sh
```

### 9.6 Резервное копирование

```bash
# Скрипт резервного копирования
nano /opt/emc3/scripts/backup.sh
```

```bash
#!/bin/bash

BACKUP_DIR="/opt/emc3/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Создание папки для бэкапов
mkdir -p $BACKUP_DIR

# Бэкап базы данных
docker exec emc3_postgres pg_dump -U emc3_user emc3_production > $BACKUP_DIR/db_backup_$DATE.sql

# Бэкап загруженных файлов
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /opt/emc3/backend/uploads/

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "$(date): Бэкап создан: $DATE" >> /var/log/emc3_backup.log
```

```bash
# Автоматический бэкап каждый день в 2:00
chmod +x /opt/emc3/scripts/backup.sh
crontab -e
# Добавить: 0 2 * * * /opt/emc3/scripts/backup.sh
```

---

## 🔄 ОБНОВЛЕНИЕ САЙТА

### 10.1 Обновление кода

```bash
# Скрипт обновления
nano /opt/emc3/scripts/update_site.sh
```

```bash
#!/bin/bash

cd /opt/emc3

# Остановка сервисов
docker-compose -f docker-compose.production.yml down

# Бэкап перед обновлением
./scripts/backup.sh

# Получение новых изменений
git pull origin main

# Пересборка образов
docker-compose -f docker-compose.production.yml build --no-cache

# Запуск миграций
docker-compose -f docker-compose.production.yml up -d postgres
sleep 10
docker-compose -f docker-compose.production.yml run --rm backend python -m alembic upgrade head

# Запуск всех сервисов
docker-compose -f docker-compose.production.yml up -d

echo "$(date): Сайт обновлен" >> /var/log/emc3_updates.log
```

### 9.2 Загрузка через FileZilla Pro

**Настройка подключения:**
- Хост: IP_ВАШЕГО_REG_RU_VPS
- Порт: 22
- Протокол: SFTP
- Пользователь: root
- Пароль: ваш_пароль

**Загрузка файлов:**
1. Подключитесь к серверу
2. Перейдите в `/opt/emc3/`
3. Загрузите обновленные файлы
4. Выполните `docker-compose restart`

---

## 📧 НАСТРОЙКА КОРПОРАТИВНОЙ ПОЧТЫ

### 10.1 Настройка Mail-1 от REG.RU

```bash
# В .env добавить настройки почты
SMTP_HOST=smtp.mail.ru
SMTP_PORT=587
SMTP_USER=noreply@emc3.ru
SMTP_PASSWORD=ваш_пароль
SMTP_FROM=noreply@emc3.ru
SMTP_FROM_NAME=EMC3 - LED освещение

# Для уведомлений о заказах
NOTIFICATION_EMAIL=orders@emc3.ru
ADMIN_EMAIL=admin@emc3.ru
```

### 10.2 Настройка уведомлений

```python
# backend/app/utils/email.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True
)

async def send_order_notification(order_data: dict):
    """Отправка уведомления о новом заказе"""
    message = MessageSchema(
        subject=f"Новый заказ #{order_data['id']} на EMC3.ru",
        recipients=[settings.NOTIFICATION_EMAIL],
        body=f"""
        Новый заказ от {order_data['company_name']}
        
        Контакт: {order_data['contact_person']}
        Email: {order_data['email']}
        Телефон: {order_data['phone']}
        
        Сумма заказа: {order_data['total_amount']} ₽
        
        Заказ автоматически создан в Битрикс24.
        """,
        subtype="plain"
    )
    
    fm = FastMail(mail_config)
    await fm.send_message(message)
```

---

## 🎯 ФИНАЛЬНАЯ ПРОВЕРКА

### 11.1 Чек-лист запуска

- [ ] База данных PostgreSQL работает на my.adminvps.ru
- [ ] Backend развернут на REG.RU VPS
- [ ] Frontend работает и отображается
- [ ] SSL сертификат установлен
- [ ] DNS записи настроены
- [ ] Интеграция с Битрикс24 работает
- [ ] Почтовые уведомления настроены
- [ ] Мониторинг и бэкапы настроены

### 11.2 Тестирование

```bash
# Проверка API
curl https://emc3.ru/api/health

# Проверка сайта
curl -I https://emc3.ru

# Проверка SSL
openssl s_client -servername emc3.ru -connect emc3.ru:443
```

---

## 📞 ПОДДЕРЖКА И КОНТАКТЫ

### Ваши инструменты управления:
- **Portainer**: https://188.214.107.67:9443/#!/3/docker/stacks
- **Nginx Manager**: https://nginx.safronai.ru
- **PgAdmin**: http://my.adminvps.ru:8080
- **REG.RU**: Панель управления VPS и DNS

### Логи и мониторинг:
- Логи приложения: `/var/log/emc3_*.log`
- Логи Nginx: `/var/log/nginx/emc3.ru.*.log`
- Мониторинг через Portainer

### Экстренные контакты:
- REG.RU техподдержка: 8 (800) 505-06-00
- Ваш администратор: через Битрикс24

**Ваш сайт EMC3.ru готов к работе! 🚀**