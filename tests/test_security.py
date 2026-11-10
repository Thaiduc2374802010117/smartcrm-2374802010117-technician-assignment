"""Checklist bảo mật mục 2 và 5: dữ liệu vào được kiểm ở tầng ứng dụng; thông báo lỗi không lộ cấu trúc bên trong."""
from fastapi.testclient import TestClient

from src.backend.main import app

H = {"X-Employee-Id": "3", "X-Role": "QUAN_LY", "X-Center-Id": "2"}
c = TestClient(app, raise_server_exceptions=False)


def test_chuoi_injection_bi_tu_choi_400_khong_tra_danh_sach():                       # A05 Injection
    for params in ({"priority": "' OR '1'='1"}, {"category_id": "1 OR 1=1"}, {"status": "MOI'; DROP TABLE ticket;--"}):
        r = c.get("/api/tickets", params=params, headers=H)
        assert r.status_code == 400 and "items" not in r.json()


def test_json_hong_tra_400_khong_lo_stack_hay_ten_bang():                               # A10 / A02
    r = c.post("/api/tickets/1/assignment", content=b'{"technician_id": 2', headers={**H, "Content-Type": "application/json"})
    assert r.status_code == 400 and r.json()["error"]["fields"] == {"body": "JSON không hợp lệ"}
    for leak in ("Traceback", "psycopg", "ticket_status_log", "SELECT", "File \""):
        assert leak not in r.text
