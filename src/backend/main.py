"""Khởi động ứng dụng FastAPI – luồng L4 Phân công kỹ thuật viên và lịch hẹn.
Chạy (từ thư mục gốc repo):  uvicorn src.backend.main:app --reload --port 3000"""
import os

from fastapi import FastAPI

from . import db
from .api import errors
from .api.tickets import router as tickets_router

app = FastAPI(title="Smart CRM – L4 Phân công kỹ thuật viên và lịch hẹn", version="0.2.0")
errors.register(app)
app.include_router(tickets_router)


@app.get("/", include_in_schema=False)
def hello():
    return "Hello Smart CRM"


@app.get("/db-check", summary="Kiểm tra kết nối CSDL (smoke test buổi 2)")
def db_check():
    try:
        with db.connect() as conn:
            row = conn.execute("SELECT now() AS server_time").fetchone()
        return {"status": "OK", "database": os.getenv("DB_NAME"), "server_time": str(row["server_time"])}
    except Exception as e:  # noqa: BLE001 – smoke test cần báo mọi lỗi kết nối
        return {"status": "ERROR", "message": str(e)}
