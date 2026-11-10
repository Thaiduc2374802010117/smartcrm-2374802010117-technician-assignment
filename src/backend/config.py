"""Kiểm biến môi trường MỘT lần khi khởi động – thiếu thì dừng sớm, báo TÊN biến (không bao giờ in GIÁ TRỊ)."""
import os
import sys

REQUIRED = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]


def check_env() -> None:
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        print("Thiếu biến môi trường: " + ", ".join(missing) + " – xem .env.example", file=sys.stderr)
        sys.exit(1)
