"""Deploy thử (TD-20): chuẩn bị CSDL khi khởi động phải chạy lại được không lỗi, không xoá và không nhân đôi dữ liệu (C8)."""
import psycopg
import pytest

from tests.tc_bt3 import QL_TAN_BINH, TEST_DB, Ctx


@pytest.fixture()
def x(monkeypatch):
    try:
        c = Ctx()
    except psycopg.OperationalError as e:
        pytest.skip(f"Không kết nối được PostgreSQL: {e}")
    monkeypatch.setenv("DB_NAME", TEST_DB)
    return c


def test_khoi_dong_lai_khong_xoa_khong_nhan_doi(x):
    from src.backend.start import prepare_database
    assert prepare_database() == "bảng đã có dữ liệu – giữ nguyên"            # CSDL đã có dữ liệu mẫu
    x.api.post("/api/tickets/1/assignment", json={"technician_id": 2}, headers=QL_TAN_BINH)
    assert prepare_database() == "bảng đã có dữ liệu – giữ nguyên"            # khởi động lại lần hai
    assert x.count("ticket") == 13 and x.count("ticket_status_log") == 1         # không nhân đôi, không mất thao tác


def test_csdl_trong_thi_nap_du_lieu_mau(x):
    from src.backend.db import connect
    from src.backend.start import prepare_database
    with connect(TEST_DB) as c:
        c.execute("TRUNCATE ticket_status_log, appointment, ticket, technician_skill, technician, issue_category RESTART IDENTITY CASCADE")
    assert prepare_database() == "đã nạp dữ liệu mẫu"
    assert (x.count("technician"), x.count("ticket")) == (6, 13)
