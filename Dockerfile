# Используем официальный легкий образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости для работы PostgreSQL (psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Запрещаем Python писать файлы .pyc и включаем небуферизованный вывод (для логов)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Обновляем pip и копируем requirements.txt
RUN pip install --upgrade pip
COPY requirements.txt .

# Устанавливаем зависимости Django
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Открываем порт 8000 (хотя внутри сети Docker это больше для документации)
EXPOSE 8000