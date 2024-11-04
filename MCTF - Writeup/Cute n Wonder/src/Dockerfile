FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get -y update; apt-get -y install curl
RUN pip install --no-cache-dir -r requirements.txt

COPY templates/ templates/
COPY static/ static/
COPY app.py app.py
EXPOSE 5000

ARG FLAG="MCTF%7Bexample_flag%7D" # <-- This value will be used as default, if argument is not specified explicitly (via --build-args or args in docker-compose)
ENV FLAG=$FLAG
COPY docker-entrypoint.sh docker-entrypoint.sh

ENTRYPOINT ["/bin/sh", "/app/docker-entrypoint.sh"]
