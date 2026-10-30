"""Test tích hợp qua HTTP (FastAPI TestClient) trên database RIÊNG smartcrm_test:
CRUD đủ cho 2 thực thể (kỹ thuật viên, lịch hẹn) và suy giảm có kiểm soát khi CSDL tắt (C7).
Tự bỏ qua nếu không kết nối được PostgreSQL. Chạy:  python -m pytest -v"""
import os
from datetime import datetime, timedelta, timezone

import psycopg
import pytest
from fastapi.testclient import TestClient

from src.backend.db import ROOT, connect
from src.backend.main import app

TEST_DB = os.getenv("TEST_DB_NAME", "smartcrm_test")
H = {"X-Employee-Id": "3", "X-Role": "QUAN_LY", "X-Center-Id": "2"}
VN = timezone(timedelta(hours=7))


def next_weekday_9h(days=2):
    d = datetime.now(VN) + timedelta(days=days)
    if d.weekday() == 6:
        d += timedelta(days=1)
    return d.replace(hour=9, minute=0, second=0, microsecond=0)


@pytest.fixture()
def client(monkeypatch):
    try:
        with connect("postgres") as c:
            c.autocommit = True
            if not c.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB,)).fetchone():
                c.execute(f'CREATE DATABASE "{TEST_DB}"')
        with connect(TEST_DB) as c:
            for folder in ("migrations", "seed"):
                for f in sorted((ROOT / "db" / folder).glob("*.sql")):
                    c.execute(f.read_text(encoding="utf-8"))
    except psycopg.OperationalError as e:
        pytest.skip(f"Không kết nối được PostgreSQL: {e}")
    monkeypatch.setenv("DB_NAME", TEST_DB)
    return TestClient(app, raise_server_exceptions=False)


def test_crud_ky_thuat_vien(client):
    r = client.post("/api/technicians", json={"full_name": "Trần Văn Mới", "level": "SO_CAP"}, headers=H)   # CREATE
    assert r.status_code == 201
    tid = r.json()["technician_id"]
    assert client.get(f"/api/technicians/{tid}", headers=H).json()["full_name"] == "Trần Văn Mới"         # READ
    assert any(t["technician_id"] == tid for t in client.get("/api/technicians", headers=H).json()["items"])
    r = client.put(f"/api/technicians/{tid}", json={"full_name": "Trần Văn Mới", "level": "TRUNG_CAP"}, headers=H)  # UPDATE
    assert r.status_code == 200 and r.json()["level"] == "TRUNG_CAP"
    r = client.delete(f"/api/technicians/{tid}", headers=H)                                                 # DELETE (mềm)
    assert r.status_code == 200 and r.json()["is_active"] is False
    r = client.delete("/api/technicians/3", headers=H)          # Phạm Văn C đang giữ 5 phiếu mở
    assert r.status_code == 409 and r.json()["error"]["code"] == "TECHNICIAN_HAS_OPEN_TICKETS"


def test_crud_lich_hen(client):
    assert client.post("/api/tickets/1/assignment", json={"technician_id": 2}, headers=H).status_code == 201
    start = next_weekday_9h()
    r = client.post("/api/tickets/1/appointments", headers=H, json={                                      # CREATE
        "appointment_type": "TRA_MAY", "start_at": start.isoformat(), "end_at": (start + timedelta(minutes=30)).isoformat()})
    assert r.status_code == 201
    aid = r.json()["appointment_id"]
    assert client.get(f"/api/appointments/{aid}", headers=H).json()["status"] == "DA_HEN"                  # READ
    new = start + timedelta(hours=1)
    r = client.put(f"/api/appointments/{aid}", headers=H, json={                                          # UPDATE
        "start_at": new.isoformat(), "end_at": (new + timedelta(minutes=45)).isoformat()})
    assert r.status_code == 200
    r = client.delete(f"/api/appointments/{aid}", headers=H, params={"reason": "Khách báo bận, hẹn lại sau"})  # DELETE
    assert r.status_code == 200 and r.json()["status"] == "DA_HUY"
    r = client.delete(f"/api/appointments/{aid}", headers=H, params={"reason": "Hủy lần thứ hai do nhầm"})
    assert r.status_code == 409                                                                         # đã hủy rồi


def test_du_lieu_sai_bi_tu_choi_co_thong_bao_ro(client):                                                 # C7
    r = client.post("/api/technicians", json={"full_name": "A", "level": "XYZ"}, headers=H)
    assert r.status_code == 400 and set(r.json()["error"]["fields"]) == {"full_name", "level"}


def test_csdl_tat_tra_503_ro_rang_khong_treo(client, monkeypatch):                                     # C7 suy giảm có kiểm soát
    monkeypatch.setenv("DB_PORT", "1")                                                                  # cổng không có CSDL
    r = client.get("/api/tickets?status=MOI", headers=H)
    assert r.status_code == 503 and r.json()["error"]["code"] == "DATABASE_UNAVAILABLE"
