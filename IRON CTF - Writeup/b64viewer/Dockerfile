FROM python:3.9.7

COPY /challenge /chall

WORKDIR /chall

RUN mv flag.sh /usr/local/bin/flag

RUN pip install -r requirements.txt

ENV flag ironCTF{redacted}

EXPOSE 5000

CMD ["python","-m","app"]