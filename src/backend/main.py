"""Khởi động ứng dụng FastAPI – luồng L4 Phân công kỹ thuật viên và lịch hẹn.
Chạy (từ thư mục gốc repo):  uvicorn src.backend.main:app --reload --port 3000
Giao diện (cửa sổ khác): python -m http.server 5500 -d src/frontend → http://localhost:5500
Tài liệu API: http://localhost:3000/docs"""
import logging
import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from . import config, db
from .api import errors
from .api.appointments import router as appointments_router
from .api.technicians import router as technicians_router
from .api.tickets import router as tickets_router

config.check_env()      # dừng sớm nếu .env thiếu biến bắt buộc
app = FastAPI(title="Smart CRM – L4 Phân công kỹ thuật viên và lịch hẹn", version="1.0.0")
errors.register(app)
app.include_router(tickets_router)
app.include_router(appointments_router)
app.include_router(technicians_router)
# Giao diện web (① lớp trình bày – View) chạy riêng ở cổng 5500 → cho phép gọi API từ địa chỉ đó (TD-11)
app.add_middleware(CORSMiddleware,
                   allow_origins=os.getenv("FRONTEND_ORIGIN", "http://localhost:5500,http://127.0.0.1:5500").split(","),
                   allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type", "X-Employee-Id", "X-Role", "X-Center-Id"])


@app.get("/", include_in_schema=False)
def hello():
    return "Hello Smart CRM"


@app.get("/health", summary="Kiểm tra hệ thống: app và CSDL (healthcheck của docker compose)")
def health():
    """Chỉ trả TRẠNG THÁI – chi tiết lỗi kết nối (host, cổng, tên user) chỉ ghi vào log, không gửi cho người gọi (BUG-11)."""
    try:
        with db.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "db": "up"}
    except Exception as e:  # noqa: BLE001 – mọi lỗi kết nối đều là "db down"
        logging.getLogger("smartcrm").error("Health check: CSDL không phản hồi (%s)", type(e).__name__)
        return JSONResponse(status_code=503, content={"status": "degraded", "db": "down"})


@app.get("/db-check", include_in_schema=False)
def db_check():
    """Giữ đường dẫn cũ của buổi 2 cho tương thích – trả đúng như /health."""
    return health()
