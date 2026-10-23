"""④ LỚP LƯU TRỮ – kết nối PostgreSQL 16 (đọc cấu hình từ .env, không ghi mật khẩu trong mã)."""
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def connect(dbname: str | None = None):
    """Mở một kết nối mới; múi giờ +07:00 để thời gian trả về đúng quy ước ISO 8601 của API contract."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=dbname or os.getenv("DB_NAME", "smartcrm"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=3,
        row_factory=dict_row,
        options="-c timezone=Asia/Ho_Chi_Minh",
    )
