# --- ЭТАП 1: "СБОРЩИК" (Builder) ---
# На этом этапе мы устанавливаем все зависимости, включая те, что нужны для компиляции.
# Все "грязные" слои и кеш останутся здесь.
FROM python:3.13-slim as builder

# Устанавливаем переменные окружения, чтобы pip не жаловался и работал быстрее
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# 1. Устанавливаем системные зависимости (unrar)
# Делаем это в одном слое, чтобы уменьшить размер, и сразу чистим кеш apt.
RUN apt-get update && \
    echo "deb http://deb.debian.org/debian bookworm non-free" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install --no-install-recommends -y unrar && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. Копируем только файл с зависимостями, чтобы кешировать этот слой.
# Сборка будет переиспользовать этот слой, если requirements.txt не изменился.
COPY requirements.txt .

# 3. Устанавливаем Python-зависимости
RUN pip install -r requirements.txt


# --- ЭТАП 2: "ФИНАЛЬНЫЙ ОБРАЗ" (Final Image) ---
# Здесь мы собираем чистый, легкий и безопасный образ для запуска.
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# 1. Создаем пользователя без root-прав для безопасности
# Запуск от имени root в контейнере — плохая практика.
RUN addgroup --system app && adduser --system --group app

# 2. Копируем установленные Python-пакеты И ИСПОЛНЯЕМЫЕ ФАЙЛЫ из "сборщика"
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 3. Копируем системную утилиту unrar из "сборщика"
COPY --from=builder /usr/bin/unrar /usr/bin/unrar

# 4. Копируем код нашего приложения.
# Благодаря .dockerignore, сюда попадет только то, что нужно.
COPY . .

# 5. Устанавливаем владельцем всех файлов нашего пользователя
RUN chown -R app:app /app

# 6. Переключаемся на пользователя без root-прав
USER app

# 7. Указываем порт, который слушает наше приложение внутри контейнера.
# Это больше для документации и автоматизации.
EXPOSE 19789

# 8. Команда для запуска приложения.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "19789"]