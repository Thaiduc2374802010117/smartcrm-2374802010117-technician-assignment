"""Test tích hợp trên PostgreSQL thật – database RIÊNG smartcrm_test (không đụng dữ liệu trong smartcrm).
Tự bỏ qua (skip) nếu không kết nối được PostgreSQL. Chạy:  python -m pytest -v
TC07 – NFR3: 2 yêu cầu phân công cùng lúc → đúng 1 thành công, đúng 1 dòng lịch sử.
TC10 – QT-L4-02: ràng buộc EXCLUDE từ chối 09:15–09:45 khi đã có 09:00–09:30, kể cả khi bỏ qua lớp nghiệp vụ."""
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import psycopg
import pytest

from src.backend.db import ROOT, connect
from src.backend.repositories.unit_of_work import UnitOfWork
from src.backend.services.assignment_service import AssignmentService, SuggestionService
from src.backend.services.errors import InvalidState

TEST_DB = os.getenv("TEST_DB_NAME", "smartcrm_test")
VN = timezone(timedelta(hours=7))


@dataclass(frozen=True)
class User:
    employee_id: int = 3
    role: str = "QUAN_LY"
    center_id: int = 2


@pytest.fixture(scope="module")
def test_db():
    try:
        with connect("postgres") as c:
            c.autocommit = True
            if not c.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB,)).fetchone():
                c.execute(f'CREATE DATABASE "{TEST_DB}"')
    except psycopg.OperationalError as e:
        pytest.skip(f"Không kết nối được PostgreSQL: {e}")
    return TEST_DB


@pytest.fixture()
def fresh(test_db):
    """Tạo bảng theo migration và nạp lại dữ liệu mẫu trước mỗi test."""
    with connect(test_db) as c:
        for folder in ("migrations", "seed"):
            for f in sorted((ROOT / "db" / folder).glob("*.sql")):
                c.execute(f.read_text(encoding="utf-8"))
    return lambda: UnitOfWork(dbname=test_db)


def test_tc07_hai_yeu_cau_phan_cong_dong_thoi_chi_mot_thanh_cong(fresh):
    service, barrier, results = AssignmentService(fresh), threading.Barrier(2), []

    def worker(technician_id):
        barrier.wait()   # hai luồng bắt đầu cùng lúc
        try:
            service.assign(2, technician_id, User())
            results.append("ok")
        except InvalidState:
            results.append("409")

    threads = [threading.Thread(target=worker, args=(t,)) for t in (1, 3)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert sorted(results) == ["409", "ok"]
    with connect(TEST_DB) as c:
        assert c.execute("SELECT count(*) AS n FROM ticket_status_log WHERE ticket_id = 2").fetchone()["n"] == 1


def test_tc10_rang_buoc_exclude_tu_choi_lich_hen_trung(fresh):
    day = (datetime.now(VN) + timedelta(days=3)).replace(hour=9, minute=0, second=0, microsecond=0)
    with connect(TEST_DB) as c:
        c.execute("UPDATE ticket SET status = 'DA_PHAN_CONG', technician_id = 2 WHERE ticket_id = 1")
        c.execute("INSERT INTO appointment (ticket_id, technician_id, appointment_type, start_at, end_at, created_by) "
                  "VALUES (1, 2, 'TRA_MAY', %s, %s, 3)", (day, day + timedelta(minutes=30)))
        c.commit()
        with pytest.raises(psycopg.errors.ExclusionViolation):    # chèn thẳng vào CSDL, bỏ qua lớp nghiệp vụ
            c.execute("INSERT INTO appointment (ticket_id, technician_id, appointment_type, start_at, end_at, created_by) "
                      "VALUES (1, 2, 'GIAO_MAY', %s, %s, 3)", (day + timedelta(minutes=15), day + timedelta(minutes=45)))


def test_ac2_1_goi_y_sap_theo_khoi_luong_viec_roi_tay_nghe(fresh):
    r = SuggestionService(fresh).suggest(1, User())     # phiếu MAN_HINH; A tay nghề 4 / 2 phiếu, B 5 / 2, C 3 / 5, D 2
    assert [s["full_name"] for s in r["suggestions"]] == ["Trần Văn B", "Lê Thị A", "Phạm Văn C"]
