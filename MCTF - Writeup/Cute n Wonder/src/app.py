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
