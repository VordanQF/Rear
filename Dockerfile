FROM python:3.10-slim

# Установим рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app/




# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем gunicorn
RUN pip install gunicorn

# Команда для запуска проекта с использованием gunicorn
CMD ["gunicorn", "DjangoProject.wsgi:application", "--bind", "0.0.0.0:8000"]
