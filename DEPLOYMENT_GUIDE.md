# 🚀 Пошаговое руководство по развертыванию сайта EMC3.ru

Это руководство поможет вам развернуть ваш интернет-магазин освещения на домене emc3.ru "с нуля".

## 📋 Что вам понадобится

- ✅ Домен emc3.ru (у вас уже есть)
- 💻 VPS/сервер (рекомендуется минимум 2GB RAM)
- 🔧 Базовые навыки работы с терминалом

## 🎯 Варианты развертывания

### Вариант 1: Простое развертывание (рекомендуется для начинающих)
**Платформа: Vercel + PlanetScale/Railway**
- ✅ Простота настройки
- ✅ Автоматические обновления
- ✅ Высокая надежность
- 💰 Бесплатно для старта

### Вариант 2: Собственный сервер (для продвинутых)
**VPS с Docker**
- ✅ Полный контроль
- ✅ Можно масштабировать
- 🔧 Требует технических знаний

---

## 🚀 ВАРИАНТ 1: Простое развертывание (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Подготовка репозитория

1. **Создайте аккаунт на GitHub** (если нет):
   - Перейдите на https://github.com
   - Нажмите "Sign up"
   - Создайте аккаунт

2. **Создайте новый репозиторий**:
   - Нажмите "New repository"
   - Название: `emc3-website`
   - Сделайте публичным
   - Нажмите "Create repository"

3. **Загрузите код**:
   ```bash
   # В папке с проектом
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/ВАШ_USERNAME/emc3-website.git
   git push -u origin main
   ```

### Шаг 2: Развертывание Backend (База данных + API)

#### Вариант A: Railway (проще)

1. **Зарегистрируйтесь на Railway**:
   - Перейдите на https://railway.app
   - Войдите через GitHub

2. **Создайте новый проект**:
   - Нажмите "New Project"
   - Выберите "Deploy from GitHub repo"
   - Выберите ваш репозиторий `emc3-website`

3. **Настройте переменные окружения**:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/db (Railway создаст автоматически)
   SECRET_KEY=ваш_секретный_ключ_32_символа
   CORS_ORIGINS=["https://emc3.ru", "https://www.emc3.ru"]
   ```

4. **Добавьте PostgreSQL**:
   - В проекте нажмите "New"
   - Выберите "Database" → "PostgreSQL"
   - Railway автоматически свяжет с вашим приложением

#### Вариант B: PlanetScale + Vercel

1. **База данных на PlanetScale**:
   - Зарегистрируйтесь на https://planetscale.com
   - Создайте новую базу данных `emc3-db`
   - Получите connection string

2. **API на Vercel**:
   - Зарегистрируйтесь на https://vercel.com
   - Подключите GitHub репозиторий
   - Настройте переменные окружения

### Шаг 3: Развертывание Frontend

1. **Создайте аккаунт на Vercel**:
   - Перейдите на https://vercel.com
   - Войдите через GitHub

2. **Импортируйте проект**:
   - Нажмите "New Project"
   - Выберите репозиторий `emc3-website`
   - Vercel автоматически определит Vite проект

3. **Настройте build settings**:
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```

4. **Добавьте переменные окружения**:
   ```
   VITE_API_URL=https://ваш-backend.railway.app
   ```

### Шаг 4: Настройка домена

1. **В панели Vercel**:
   - Перейдите в настройки проекта
   - Вкладка "Domains"
   - Добавьте `emc3.ru` и `www.emc3.ru`

2. **Настройте DNS у регистратора домена**:
   ```
   Тип: CNAME
   Имя: www
   Значение: cname.vercel-dns.com

   Тип: A
   Имя: @
   Значение: 76.76.19.61
   ```

3. **Дождитесь применения** (может занять до 24 часов)

---

## 🖥️ ВАРИАНТ 2: Собственный сервер

### Шаг 1: Аренда VPS

**Рекомендуемые провайдеры в России:**
- **Timeweb** - от 200₽/мес
- **REG.RU** - от 300₽/мес  
- **Beget** - от 250₽/мес

**Минимальные требования:**
- 2GB RAM
- 20GB SSD
- Ubuntu 20.04/22.04

### Шаг 2: Подключение к серверу

```bash
# Подключение по SSH
ssh root@ВАШ_IP_СЕРВЕРА

# Обновление системы
apt update && apt upgrade -y
```

### Шаг 3: Установка необходимого ПО

```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Git
apt install git -y

# Nginx
apt install nginx -y
```

### Шаг 4: Клонирование и настройка проекта

```bash
# Клонирование
cd /var/www
git clone https://github.com/ВАШ_USERNAME/emc3-website.git
cd emc3-website

# Создание .env файлов
cp backend/.env.example backend/.env
# Отредактируйте backend/.env с вашими настройками
```

### Шаг 5: Создание docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: emc3_db
      POSTGRES_USER: emc3_user
      POSTGRES_PASSWORD: ваш_пароль
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://emc3_user:ваш_пароль@postgres:5432/emc3_db
      SECRET_KEY: ваш_секретный_ключ
    depends_on:
      - postgres
    restart: unless-stopped

  frontend:
    build: ./frontend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
```

### Шаг 6: Настройка Nginx

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name emc3.ru www.emc3.ru;

        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location / {
            proxy_pass http://frontend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### Шаг 7: SSL сертификат (HTTPS)

```bash
# Установка Certbot
apt install certbot python3-certbot-nginx -y

# Получение сертификата
certbot --nginx -d emc3.ru -d www.emc3.ru
```

### Шаг 8: Запуск проекта

```bash
# Сборка и запуск
docker-compose up -d --build

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### Шаг 9: Настройка автообновления

```bash
# Создание скрипта автообновления
nano /home/update-emc3.sh
```

```bash
#!/bin/bash
cd /var/www/emc3-website
git pull origin main
docker-compose up -d --build
```

```bash
# Права на выполнение
chmod +x /home/update-emc3.sh

# Добавление в cron для автообновления
crontab -e
# Добавить строку:
# 0 3 * * * /home/update-emc3.sh
```

---

## 🔧 Настройка DNS

У вашего регистратора домена (где вы купили emc3.ru):

```
Тип записи: A
Имя: @
Значение: IP_ВАШЕГО_СЕРВЕРА

Тип записи: A  
Имя: www
Значение: IP_ВАШЕГО_СЕРВЕРА
```

---

## ✅ Проверка работоспособности

1. **Откройте браузер** и перейдите на https://emc3.ru
2. **Проверьте основные функции**:
   - Загрузка главной страницы
   - Переход в каталог
   - Регистрация/авторизация
   - Добавление товаров в корзину

---

## 🚨 Решение проблем

### Сайт не открывается
- Проверьте DNS настройки (может занять до 24 часов)
- Убедитесь, что сервер запущен: `docker-compose ps`

### Ошибки API
- Проверьте логи backend: `docker-compose logs backend`
- Убедитесь, что база данных подключена

### SSL не работает
- Перезапустите Certbot: `certbot renew`
- Проверьте настройки Nginx

---

## 💡 Рекомендации

1. **Начните с Варианта 1** (Vercel) - это проще и надежнее
2. **Сделайте бэкап** базы данных регулярно
3. **Мониторьте** работу сайта
4. **Обновляйте** код регулярно через Git

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `docker-compose logs`
2. Перезапустите контейнеры: `docker-compose restart`
3. Обратитесь за помощью к разработчику

**Удачи с запуском вашего интернет-магазина! 🚀**