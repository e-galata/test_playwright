# Используем минимальный официальный образ Playwright
FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy

# Устанавливаем только необходимые пакеты (без рекомендованных)
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    openjdk-17-jdk-headless \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Allure одной командой
RUN curl -sSL https://github.com/allure-framework/allure2/releases/download/2.33.0/allure-2.33.0.tgz | \
    tar -xz -C /opt/ && \
    ln -s /opt/allure-2.33.0/bin/allure /usr/bin/allure

# Копируем только requirements.txt сначала для кэширования
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Настройка переменных окружения
RUN JAVA_PATH=$(dirname $(dirname $(readlink -f $(which java)))) && \
    echo "export JAVA_HOME=${JAVA_PATH}" \
    echo "export PATH=\${JAVA_HOME}/bin:\${PATH}"

# Точка входа с разделением команд
CMD ["sh", "-c", "pytest -s -v ./tests --alluredir=./allureres --browser=chromium --browser=firefox --browser=webkit && allure serve --host 0.0.0.0 -p 8080 ./allureres"]
