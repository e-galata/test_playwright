# Базовый образ с Python 3.13 и Playwright 1.51
FROM python:3.13-slim-bookworm

# Установка Playwright и зависимостей
RUN apt-get update && \
    apt-get install -y \
    wget \
    xvfb \
    libgtk-3-0 \
    libnotify4 \
    libnss3 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Установка Playwright 1.51 через pip (не из системных пакетов)
RUN pip install playwright==1.51.0 && \
    playwright install chromium && \
    playwright install-deps

# Рабочая директория
WORKDIR /

# Копируем зависимости отдельно для кеширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Скрипт запуска Xvfb
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
