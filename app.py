import os
import time
import psycopg2
from flask import Flask

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )

def init_db():
    for _ in range(10):
        try:
            conn = get_conn()
            with conn, conn.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS visits (id SERIAL PRIMARY KEY, ts TIMESTAMP DEFAULT NOW())")
            conn.close()
            return
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("database not reachable")

@app.route("/")
def index():
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("INSERT INTO visits DEFAULT VALUES")
        cur.execute("SELECT COUNT(*) FROM visits")
        count = cur.fetchone()[0]
    conn.close()
    return f"Hello from Docker on AWS! This page has been visited {count} times.\n"

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
