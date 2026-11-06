"""Kiểm tra tệp khoá thư viện (mục C6 của BT2): requirements.txt phải đọc được bằng UTF-8
và MỌI dòng thư viện đều ghi phiên bản cố định bằng '=='. Chạy:  python -m pytest -v"""
from pathlib import Path

REQ = Path(__file__).resolve().parents[1] / "requirements.txt"


def lines():
    raw = REQ.read_bytes()
    assert not raw.startswith((b"\xff\xfe", b"\xfe\xff")), "requirements.txt đang là UTF-16 – tạo lại bằng cmd, không dùng PowerShell"
    text = raw.decode("utf-8-sig")                      # lỗi nếu không phải UTF-8
    return [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]


def test_moi_thu_vien_deu_khoa_phien_ban_bang_dau_bang_kep():
    chua_khoa = [l for l in lines() if "==" not in l]
    assert chua_khoa == [], f"Các dòng chưa khoá phiên bản: {chua_khoa}"


def test_co_du_thu_vien_ma_du_an_dung():
    names = {l.split("==")[0].lower().replace("_", "-") for l in lines()}
    for pkg in ["fastapi", "uvicorn", "psycopg", "psycopg-binary", "python-dotenv", "pytest", "httpx"]:
        assert pkg in names, f"Thiếu {pkg} trong requirements.txt"
