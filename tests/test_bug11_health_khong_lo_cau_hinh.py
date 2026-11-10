"""Hồi quy BUG-11: kiểm tra sức khoẻ không được lộ host, cổng, tên user CSDL và phải trả 503 khi CSDL hỏng (checklist bảo mật mục 5)."""
from fastapi.testclient import TestClient

from src.backend.main import app


def test_bug11_csdl_hong_tra_503_khong_lo_chi_tiet(monkeypatch):
    monkeypatch.setenv("DB_PORT", "1")                       # cổng không có CSDL
    monkeypatch.setenv("DB_PASSWORD", "mat-khau-sai-de-thu")
    c = TestClient(app, raise_server_exceptions=False)
    for path in ("/health", "/db-check"):
        r = c.get(path)
        assert r.status_code == 503 and r.json() == {"status": "degraded", "db": "down"}
        for leak in ("127.0.0.1", "localhost", "5432", "port", "user", "password", "mat-khau-sai-de-thu"):
            assert leak not in r.text.lower()
