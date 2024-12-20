FROM python:3.12.0

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y gettext

COPY . .
RUN python manage.py collectstatic --noinput --clear

EXPOSE 443

CMD ["gunicorn", "--certfile=/usr/src/app/cert/fullchain.pem", "--keyfile=/usr/src/app/cert/privkey.pem", "-b", "0.0.0.0:443", "--access-logfile", "-", "--error-logfile", "-", "chronocast.wsgi:application"]
