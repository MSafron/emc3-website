# 🚀 План развертывания сайта EMC3

**Дата:** 25 августа 2024  
**Версия:** 1.0  
**Цель:** Поэтапное развертывание интернет-магазина EMC3 на собственных серверах

---

## 📋 Обзор проекта

**Что разворачиваем:**
- Интернет-магазин LED светильников EMC3
- Frontend: React + TypeScript + Tailwind CSS
- Backend: Python FastAPI + PostgreSQL
- Интеграции: Битрикс24, 1С (опционально)

**Особенности:**
- Фирменный дизайн с логотипом и шрифтами EMC3
- B2B направленность
- Умный поиск товаров
- Система заявок и корзины

---

## 🏗️ Этап 1: Подготовка инфраструктуры (1-2 дня)

### 1.1 Требования к серверу

**Минимальные характеристики:**
- **CPU:** 4 ядра (Intel/AMD)
- **RAM:** 8 GB
- **Диск:** 100 GB SSD
- **ОС:** Ubuntu 20.04+ или CentOS 8+
- **Сеть:** Статический IP, домен

**Необходимое ПО:**
```bash
# Базовые компоненты
- Docker & Docker Compose
- Nginx (веб-сервер)
- PostgreSQL 14+
- Redis (кеширование)
- SSL сертификаты (Let's Encrypt)
```

### 1.2 Настройка домена и DNS

**Действия:**
1. Привязать домен к IP сервера
2. Настроить A-записи:
   ```
   example.com → IP_СЕРВЕРА
   www.example.com → IP_СЕРВЕРА
   api.example.com → IP_СЕРВЕРА (для API)
   ```
3. Настроить SSL сертификаты

### 1.3 Установка Docker

**Команды для Ubuntu:**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

---

## 🔧 Этап 2: Развертывание Backend (2-3 дня)

### 2.1 Подготовка файлов проекта

**Структура проекта на сервере:**
```
/opt/emc3/
├── backend/
├── frontend/
├── nginx/
├── docker-compose.production.yml
└── .env.production
```

### 2.2 Настройка переменных окружения

**Создание `.env.production`:**
```bash
# База данных
POSTGRES_DB=emc3_production
POSTGRES_USER=emc3_user
POSTGRES_PASSWORD=СГЕНЕРИРОВАТЬ_ПАРОЛЬ
DATABASE_URL=postgresql://emc3_user:ПАРОЛЬ@postgres:5432/emc3_production

# Приложение
ENVIRONMENT=production
SECRET_KEY=СГЕНЕРИРОВАТЬ_КЛЮЧ
DEBUG=false
ALLOWED_HOSTS=example.com,www.example.com,api.example.com

# Redis
REDIS_URL=redis://redis:6379/0

# Безопасность
CORS_ORIGINS=https://example.com,https://www.example.com

# Email (для уведомлений)
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=EMAIL_ПАРОЛЬ
```

### 2.3 Конфигурация Docker Compose

**`docker-compose.production.yml`:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    env_file: .env.production
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.production
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
```

### 2.4 Запуск Backend

**Команды развертывания:**
```bash
# Переход в директорию проекта
cd /opt/emc3

# Сборка и запуск контейнеров
docker-compose -f docker-compose.production.yml up -d --build

# Применение миграций БД
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head

# Проверка статуса
docker-compose -f docker-compose.production.yml ps
```

---

## 🎨 Этап 3: Развертывание Frontend (1-2 дня)

### 3.1 Подготовка шрифтов EMC3

**Загрузка фирменных шрифтов:**
```bash
# Создание директории для шрифтов
mkdir -p /opt/emc3/frontend/public/fonts

# Копирование шрифтов Helios из брендбука
# (файлы нужно получить у дизайнера или из EMC 3 Final/Segoue/)
```

### 3.2 Настройка переменных Frontend

**`.env.production` для Frontend:**
```bash
VITE_API_URL=https://api.example.com
VITE_APP_TITLE=EMC3 - Профессиональные решения освещения
VITE_APP_DESCRIPTION=Энергоэффективные LED светильники для бизнеса
VITE_ENVIRONMENT=production
```

### 3.3 Сборка Frontend

**`frontend/Dockerfile.production`:**
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

---

## 🌐 Этап 4: Настройка Nginx (1 день)

### 4.1 Конфигурация Nginx

**`nginx/nginx.conf`:**
```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;
    
    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/certs/privkey.pem;
    
    # Frontend
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Статические файлы
    location /static/ {
        alias /var/www/static/;
        expires 30d;
    }
}
```

### 4.2 Получение SSL сертификата

**Установка Certbot:**
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d example.com -d www.example.com

# Автообновление
sudo crontab -e
# Добавить строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 Этап 5: Настройка мониторинга (1 день)

### 5.1 Логирование

**Настройка логов:**
```bash
# Создание директории для логов
mkdir -p /opt/emc3/logs

# Настройка ротации логов
sudo nano /etc/logrotate.d/emc3
```

### 5.2 Мониторинг здоровья

**Health check скрипт:**
```bash
#!/bin/bash
# /opt/emc3/health-check.sh

echo "=== EMC3 Health Check $(date) ==="

# Проверка контейнеров
docker-compose -f /opt/emc3/docker-compose.production.yml ps

# Проверка доступности API
curl -f https://api.example.com/health || echo "API недоступно"

# Проверка Frontend
curl -f https://example.com || echo "Frontend недоступен"

# Проверка места на диске
df -h

echo "=== Проверка завершена ==="
```

---

## 🔄 Этап 6: Резервное копирование (1 день)

### 6.1 Настройка бэкапов БД

**Скрипт автоматического бэкапа:**
```bash
#!/bin/bash
# /opt/emc3/backup.sh

BACKUP_DIR="/opt/backups/emc3"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Бэкап PostgreSQL
docker-compose -f /opt/emc3/docker-compose.production.yml exec -T postgres pg_dump -U emc3_user emc3_production > $BACKUP_DIR/db_$DATE.sql

# Бэкап файлов проекта
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /opt/emc3

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Бэкап создан: $DATE"
```

**Добавление в crontab:**
```bash
# Ежедневный бэкап в 2:00
0 2 * * * /opt/emc3/backup.sh >> /var/log/emc3-backup.log 2>&1
```

---

## 🚀 Этап 7: Запуск и тестирование (1-2 дня)

### 7.1 Финальный запуск

**Команды запуска:**
```bash
# Переход в директорию проекта
cd /opt/emc3

# Остановка сервисов
docker-compose -f docker-compose.production.yml down

# Пересборка и запуск
docker-compose -f docker-compose.production.yml up -d --build

# Проверка логов
docker-compose -f docker-compose.production.yml logs -f
```

### 7.2 Тестирование функционала

**Чек-лист тестирования:**
- [ ] Открытие главной страницы
- [ ] Навигация по каталогу
- [ ] Поиск товаров
- [ ] Добавление в корзину
- [ ] Регистрация пользователя
- [ ] Оформление заявки
- [ ] Отправка email уведомлений
- [ ] Адаптивность на мобильных
- [ ] Скорость загрузки страниц
- [ ] SSL сертификат
- [ ] SEO мета-теги

### 7.3 Проверка производительности

**Инструменты для тестирования:**
```bash
# Проверка скорости загрузки
curl -w "@curl-format.txt" -o /dev/null -s "https://example.com"

# Нагрузочное тестирование (Apache Bench)
ab -n 1000 -c 10 https://example.com/

# Проверка безопасности
nmap -sS -A example.com
```

---

## 📋 Этап 8: Финальная настройка (1 день)

### 8.1 Оптимизация производительности

**Настройки:**
- Включение gzip сжатия в Nginx
- Настройка кеширования статических файлов
- Оптимизация размеров изображений
- Минификация CSS и JS

### 8.2 SEO настройки

**Добавление:**
- Robots.txt
- Sitemap.xml
- Google Analytics (если нужно)
- Яндекс.Метрика (если нужно)
- Open Graph мета-теги

### 8.3 Документация

**Создание документов:**
- Инструкция по управлению сайтом
- Контакты для технической поддержки
- Процедуры восстановления
- Руководство по обновлениям

---

## ⏱️ Общий timeline

| Этап | Время | Ответственный |
|------|-------|---------------|
| 1. Подготовка инфраструктуры | 1-2 дня | DevOps/Admin |
| 2. Развертывание Backend | 2-3 дня | Backend Developer |
| 3. Развертывание Frontend | 1-2 дня | Frontend Developer |
| 4. Настройка Nginx | 1 день | DevOps/Admin |
| 5. Настройка мониторинга | 1 день | DevOps/Admin |
| 6. Резервное копирование | 1 день | DevOps/Admin |
| 7. Запуск и тестирование | 1-2 дня | QA/Тестировщик |
| 8. Финальная настройка | 1 день | DevOps/Admin |

**Общее время: 8-12 дней**

---

## 🔧 Команды для быстрого развертывания

**Однострочное развертывание (после подготовки файлов):**
```bash
cd /opt/emc3 && \
docker-compose -f docker-compose.production.yml down && \
docker-compose -f docker-compose.production.yml up -d --build && \
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head
```

**Просмотр логов:**
```bash
# Все сервисы
docker-compose -f docker-compose.production.yml logs -f

# Только backend
docker-compose -f docker-compose.production.yml logs -f backend

# Только frontend
docker-compose -f docker-compose.production.yml logs -f frontend
```

**Обновление проекта:**
```bash
# Получение обновлений из git
git pull origin main

# Пересборка и перезапуск
docker-compose -f docker-compose.production.yml up -d --build

# Применение миграций
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head
```

---

## 📞 Поддержка после развертывания

**Рекомендуемые действия:**
1. **Мониторинг первую неделю** - ежедневная проверка логов и производительности
2. **Резервное копирование** - проверка работы автоматических бэкапов
3. **Обновления безопасности** - еженедельное обновление ОС и Docker образов
4. **Масштабирование** - мониторинг нагрузки для планирования расширения

**Контакты для поддержки:**
- Техническая поддержка проекта
- Документация в репозитории
- Мониторинг и алерты

---

**Готово к развертыванию!** 🚀

Этот план обеспечивает поэтапное и безопасное развертывание сайта EMC3 на ваших серверах с полным сохранением фирменного стиля и функционала.