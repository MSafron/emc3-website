# 🚀 Пошаговое развертывание EMC3.ru - СТАРТ!

**Дата начала:** 25 августа 2024  
**Статус:** 🟢 Готов к началу развертывания

---

## 📋 ЭТАП 1: Создание GitHub репозитория (5 минут)

### Шаг 1.1: Создание аккаунта GitHub (если нет)

1. **Перейдите на сайт:** https://github.com
2. **Нажмите "Sign up"** (если у вас нет аккаунта)
3. **Создайте аккаунт** с вашим email

### Шаг 1.2: Создание нового репозитория

1. **После входа в GitHub нажмите зеленую кнопку "New"** (справа от "Repositories")
2. **Заполните форму:**
   ```
   Repository name: emc3-website
   Description: EMC3.ru - LED освещение для бизнеса
   ☑️ Public (можно Private если хотите)
   ☑️ Add a README file
   ```
3. **Нажмите "Create repository"**

### Шаг 1.3: Получение ссылки репозитория

**После создания вы увидите экран с инструкциями. Скопируйте URL вида:**
```
https://github.com/ВАШ_USERNAME/emc3-website.git
```

### Шаг 1.4: Подготовка файлов к загрузке

**Сейчас нам нужно подготовить файлы проекта для загрузки в GitHub.**

#### Создаем .gitignore файл

**В корне папки проекта создайте файл `.gitignore` со следующим содержимым:**

```gitignore
# Environment variables
.env
.env.local
.env.production
.env.development

# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Build outputs
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Cache
.cache/
.npm/
.yarn/

# Coverage reports
coverage/
*.cover
.coverage

# Virtual environments
venv/
env/
ENV/

# Docker
.docker/

# Temporary files
*.tmp
*.temp
```

#### Создаем README.md файл

**В корне проекта создайте файл `README.md`:**

```markdown
# EMC3.ru - LED освещение для бизнеса

Интернет-магазин профессиональных LED светильников для корпоративных клиентов.

## 🏗️ Архитектура

- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Backend:** Python FastAPI + PostgreSQL
- **Deployment:** Docker + Nginx
- **Integrations:** Битрикс24, Supabase Vector DB

## 🚀 Развертывание

Следуйте инструкциям в `DEPLOYMENT_STEP_BY_STEP.md`

## 📞 Поддержка

- **Домен:** emc3.ru
- **CRM:** Битрикс24
- **Email:** admin@emc3.ru
```

### Шаг 1.5: Команды для загрузки в GitHub

**Откройте терминал (командную строку) в папке вашего проекта и выполните:**

```bash
# Инициализация Git репозитория
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: EMC3.ru LED website"

# Настройка основной ветки
git branch -M main

# Подключение к GitHub репозиторию
git remote add origin https://github.com/ВАШ_USERNAME/emc3-website.git

# Загрузка файлов в GitHub
git push -u origin main
```

**⚠️ ВАЖНО:** Замените `ВАШ_USERNAME` на ваш реальный username в GitHub!

### Шаг 1.6: Проверка загрузки

1. **Обновите страницу вашего репозитория на GitHub**
2. **Убедитесь, что видите папки:**
   - `backend/` (с Python кодом)
   - `frontend/` (с React кодом)
   - `EMC 3 Final/` (с логотипами)
   - Различные `.md` файлы

---

## ✅ Результат Этапа 1

**После выполнения у вас будет:**
- ✅ GitHub репозиторий с кодом проекта
- ✅ Все 200+ файлов проекта в облаке
- ✅ Готовность к развертыванию на сервер
- ✅ Возможность обновлений одной командой

---

## 🎯 Что дальше?

**После завершения Этапа 1 сообщите мне:**
1. ✅ "GitHub репозиторий создан" 
2. 📎 Пришлите ссылку на ваш репозиторий
3. 🚀 Начнем Этап 2: Настройка базы данных

---

## 📞 Нужна помощь?

**Если возникли проблемы:**
- Git не установлен? Скачайте с https://git-scm.com/
- Проблемы с командной строкой? Используйте GitHub Desktop
- Ошибки загрузки? Проверьте интернет соединение

**Готовы к Этапу 1? Начинайте! 🚀**