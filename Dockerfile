FROM python:3.12.0


WORKDIR /usr/src/app

# Скопируйте файл зависимостей в контейнер
COPY requirements.txt ./

# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y gettext

# Скопируйте файлы проекта в контейнер
# COPY . .

EXPOSE 443
#EXPOSE 8000


RUN python manage.py collectstatic --noinput --clear

# CMD ["python", "manage.py", "runserver", "0.0.0.0:443"]

CMD ["gunicorn", "--certfile=/usr/src/app/cert/fullchain.pem", "--keyfile=/usr/src/app/cert/privkey.pem", "-b", "0.0.0.0:443", "--access-logfile", "-", "--error-logfile", "-", "chronocast.wsgi:application"]
# The same, without certs
# CMD ["gunicorn", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "chronocast.wsgi:application"]
