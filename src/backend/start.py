"""Điểm khởi động của container: (tuỳ chọn) chuẩn bị CSDL, rồi chạy uvicorn ở cổng $PORT (mặc định 3000).

- Chạy bằng docker compose: không đặt AUTO_MIGRATE → không đụng CSDL (bảng và dữ liệu mẫu do docker-entrypoint-initdb.d tạo).
- Chạy trên nền tảng cloud (Render, xem docs/deployment-guide.md mục 8): AUTO_MIGRATE=1 → tạo bảng nếu chưa có
  (migration chạy lại không lỗi) và nạp dữ liệu mẫu CHỈ KHI bảng ticket còn trống – khởi động lại không xoá, không nhân đôi (C8).
"""
import os

import uvicorn

from . import config
from .db import ROOT, connect


def prepare_database() -> str:
    """Tạo bảng (idempotent); nạp dữ liệu mẫu nếu CSDL chưa có phiếu nào. Trả về mô tả việc đã làm."""
    with connect() as conn:
        for f in sorted((ROOT / "db" / "migrations").glob("*.sql")):
            conn.execute(f.read_text(encoding="utf-8"))
        if conn.execute("SELECT count(*) AS n FROM ticket").fetchone()["n"] > 0:
            return "bảng đã có dữ liệu – giữ nguyên"
        for f in sorted((ROOT / "db" / "seed").glob("*.sql")):
            conn.execute(f.read_text(encoding="utf-8"))
        return "đã nạp dữ liệu mẫu"


def main() -> None:
    config.check_env()
    if os.getenv("AUTO_MIGRATE") == "1":
        print("Chuẩn bị CSDL:", prepare_database(), flush=True)
    uvicorn.run("src.backend.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "3000")))


if __name__ == "__main__":
    main()
