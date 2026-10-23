"""Khởi động ứng dụng FastAPI – luồng L4 Phân công kỹ thuật viên và lịch hẹn.
Chạy (từ thư mục gốc repo):  uvicorn src.backend.main:app --reload --port 3000
Giao diện (cửa sổ khác): python -m http.server 5500 -d src/frontend → http://localhost:5500
Tài liệu API: http://localhost:3000/docs"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import db
from .api import errors
from .api.appointments import router as appointments_router
from .api.tickets import router as tickets_router

app = FastAPI(title="Smart CRM – L4 Phân công kỹ thuật viên và lịch hẹn", version="0.3.0")
errors.register(app)
app.include_router(tickets_router)
app.include_router(appointments_router)
# Giao diện web (① lớp trình bày – View) chạy riêng ở cổng 5500 → cho phép gọi API từ địa chỉ đó (TD-11)
app.add_middleware(CORSMiddleware,
                   allow_origins=os.getenv("FRONTEND_ORIGIN", "http://localhost:5500,http://127.0.0.1:5500").split(","),
                   allow_methods=["GET", "POST", "PUT"], allow_headers=["Content-Type", "X-Employee-Id", "X-Role", "X-Center-Id"])


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
