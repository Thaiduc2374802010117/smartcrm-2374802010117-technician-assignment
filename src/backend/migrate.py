"""Chạy migration tạo bảng theo DDL BT1, tùy chọn nạp dữ liệu mẫu.

Cách dùng (từ thư mục gốc repo):
    python -m src.backend.migrate          # chỉ tạo bảng
    python -m src.backend.migrate --seed   # tạo bảng + nạp dữ liệu mẫu
"""
import sys

from .db import ROOT, connect


def run(folder: str) -> None:
    files = sorted((ROOT / "db" / folder).glob("*.sql"))
    with connect() as conn:
        for f in files:
            conn.execute(f.read_text(encoding="utf-8"))
            print(f"  ✓ {folder}/{f.name}")


if __name__ == "__main__":
    print("Migration:")
    run("migrations")
    if "--seed" in sys.argv:
        print("Dữ liệu mẫu:")
        run("seed")
    with connect() as conn:
        for t in ["issue_category", "technician", "technician_skill", "ticket", "appointment", "ticket_status_log"]:
            n = conn.execute(f"SELECT count(*) AS n FROM {t}").fetchone()["n"]
            print(f"  {t:<18} {n} dòng")
