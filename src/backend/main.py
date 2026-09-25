import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI

# Đọc file .env ở thư mục gốc repo
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(title="Smart CRM - L4 Phan cong ky thuat vien")


@app.get("/")
def hello():
    return "Hello Smart CRM"


@app.get("/db-check")
def db_check():
    try:
        with psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            connect_timeout=3,
        ) as conn:
            server_time = conn.execute("SELECT NOW()").fetchone()[0]
        return {"status": "OK", "database": os.getenv("DB_NAME"), "server_time": str(server_time)}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
