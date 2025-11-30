# filename: infra/proxy_lambda/source/Dockerfile
FROM gcr.io/google.com/cloudsdktool/cloud-sdk:latest

# Установка Playwright и зависимостей браузеров
RUN pip install --upgrade pip && \
    pip install playwright==1.56.0 && \
    playwright install --with-deps

WORKDIR /app
COPY . .

# Устанавливаем зависимости проекта
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Определяем точку входа функции
CMD ["python3", "main.py"]