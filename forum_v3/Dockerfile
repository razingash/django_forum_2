FROM python:3.9-slim

RUN apt-get update && apt-get install -y libpq-dev

WORKDIR /app

COPY requirements.txt requirements.txt
COPY dockerfill.txt dockerfill.txt
COPY . /app/

RUN pip install -r requirements.txt

CMD python manage.py collectstatic