FROM openjdk:17-jdk-slim

WORKDIR /app

RUN apt-get update && apt-get install -y iptables && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /app/entrypoint.sh
COPY app.jar app.jar
COPY flag.txt flag.txt

EXPOSE 8080
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ] 
