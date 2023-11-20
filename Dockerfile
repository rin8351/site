# Используйте официальный образ Python
FROM python:3.12.0

# Установите рабочую директорию в контейнере
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y gettext

# Скопируйте файлы проекта в контейнер
COPY . .

# Установите зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Определите порт, на котором будет работать приложение
EXPOSE 443

# Collect static files
RUN python manage.py collectstatic --noinput

# Запустите сервер разработки Django
# CMD ["python", "manage.py", "runserver", "0.0.0.0:443"]
CMD ["gunicorn", "--certfile=/usr/src/app/cert/fullchain.pem", "--keyfile=/usr/src/app/cert/privkey.pem", "-b", "0.0.0.0:443", "--access-logfile", "-", "--error-logfile", "-", "chronocast.wsgi:application"]

