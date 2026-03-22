# 🚪 PRO Монтаж — Платформа управления заявками на монтаж дверей

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.x-green?logo=django)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.x-red)](https://www.django-rest-framework.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)](https://postgresql.org)
[![AWS](https://img.shields.io/badge/AWS-EC2-orange?logo=amazonaws)](https://aws.amazon.com)
[![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-black?logo=github)](https://github.com/features/actions)

---

## 📋 О проекте

**PRO Монтаж** — это REST API платформа для автоматизации процесса заказа монтажа дверей. Магазины создают заявки, менеджеры обрабатывают их и назначают специалистов.

### Проблема которую решает проект:
> Раньше магазины и монтажная компания общались по телефону — теряли заявки, забывали даты, не отслеживали статусы. Теперь всё в одной системе.

---

## 🔄 Как работает система

```
Магазин создаёт заявку
        ↓
Менеджер принимает и назначает специалиста + дату
        ↓
Магазин получает уведомление
        ↓
Специалист выполняет монтаж
        ↓
Статус заявки → Завершён ✅
```

---

## 👥 Роли пользователей

| Роль | Возможности |
|------|------------|
| **Магазин** | Создание заявок, просмотр статусов, загрузка файлов, уведомления |
| **Менеджер** | Управление всеми заявками, назначение специалистов, управление прайсом |

---

## 🛠 Технологии

| Категория | Технологии |
|-----------|-----------|
| **Backend** | Python 3.12, Django 5.x, Django REST Framework |
| **База данных** | PostgreSQL 15 |
| **Аутентификация** | JWT (djangorestframework-simplejwt) |
| **Документация API** | Swagger (drf-yasg) |
| **Контейнеризация** | Docker, Docker Compose |
| **Веб-сервер** | Nginx + Gunicorn |
| **Облако** | AWS EC2 |
| **CI/CD** | GitHub Actions |
| **PDF генерация** | ReportLab |

---

## 📡 API Endpoints

### Авторизация
```
POST   /api/auth/register/        — Регистрация магазина
POST   /api/auth/login/           — Авторизация (JWT)
POST   /api/auth/login/refresh/   — Обновление токена
GET    /api/auth/profile/         — Просмотр профиля
PUT    /api/auth/profile/         — Обновление профиля
```

### Заявки (Магазин)
```
GET    /api/orders/               — Список своих заявок
POST   /api/orders/               — Создать заявку
GET    /api/orders/{id}/          — Детали заявки
GET    /api/orders/{id}/files/    — Файлы заявки
POST   /api/orders/{id}/files/    — Загрузить файл
GET    /api/orders/notifications/ — Уведомления
GET    /api/orders/services/      — Прайс-лист
GET    /api/orders/services/pdf/  — Скачать прайс PDF
```

### Панель менеджера
```
GET    /api/manager/orders/           — Все заявки
GET    /api/manager/orders/{id}/      — Детали заявки
PATCH  /api/manager/orders/{id}/      — Изменить статус/специалиста/дату
POST   /api/manager/orders/{id}/files/ — Загрузить файл
POST   /api/manager/services/        — Добавить услугу
DELETE /api/manager/services/{id}/   — Удалить услугу
```

---

## 🚀 Быстрый старт

### Требования
- Docker
- Docker Compose

### Установка

```bash
# 1. Клонируй репозиторий
git clone https://github.com/Nurbol46/door_app.git
cd door_app

# 2. Создай .env файл
cp .env.example .env
# Заполни переменные окружения

# 3. Запусти проект
docker-compose up --build

# 4. Открой Swagger
http://localhost/swagger/
```

---

## ⚙️ Переменные окружения

Создай файл `.env` в корне проекта:

```env
SECRET_KEY=твой_секретный_ключ
DEBUG=True

DB_NAME=doors_db
DB_USER=postgres
DB_PASSWORD=пароль
DB_HOST=db
DB_PORT=5432

ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 🏗 Архитектура проекта

```
door_app/
├── app/
│   ├── users/          # Пользователи, магазины
│   ├── orders/         # Заявки, файлы, уведомления, прайс
│   └── manager/        # Панель менеджера
├── config/             # Настройки Django
├── nginx/              # Конфигурация Nginx
├── .github/workflows/  # CI/CD pipeline
├── Dockerfile
└── docker-compose.yml
```

---

## 🔐 Безопасность

- JWT аутентификация с refresh токенами
- Разграничение доступа по ролям (магазин / менеджер)
- Пользователи видят только свои заявки
- Менеджерские эндпоинты защищены `IsManager` permission
- Секреты через переменные окружения

---

## 📊 Модели данных

```
User (AbstractUser)
├── role: user | manager
├── full_name, number, email
└── Shop (OneToOne)
    ├── name, city, street, house_number

Order (Заявка)
├── order_number (АД0001)
├── status: awaiting_call | awaiting_service | paused | completed | cancelled
├── user, manager, specialist (ForeignKey → User)
├── city, street, house
├── work_date_start, work_date_end, work_date
└── OrderFile (файлы)

Notification
├── user, order
└── is_read

Service (Прайс-лист)
├── name
└── price
```

---

## 🚢 Деплой

Проект задеплоен на **AWS EC2** с автоматическим деплоем через **GitHub Actions**.

При каждом `git push origin main`:
1. GitHub Actions подключается к серверу
2. Выполняет `git pull`
3. Перезапускает Docker контейнеры

**Live demo:** `http://13.60.189.218/swagger/`

---

## 📝 Лицензия

MIT License

---

## 👨‍💻 Автор

**Nurbol** — [@Nurbol46](https://github.com/Nurbol46)
