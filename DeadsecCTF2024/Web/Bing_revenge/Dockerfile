FROM python:3.11-slim-buster

RUN echo "dead{fake_flag_for_test}" > /flag.txt

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y iputils-ping
COPY src/ .

RUN chmod 755 /app

RUN groupadd -r onsra -g 433 && \
    useradd -u 431 -r -g onsra -s /sbin/nologin -c "Docker image user" onsra
USER onsra

CMD ["python", "app.py"]