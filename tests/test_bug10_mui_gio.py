"""Hồi quy BUG-10: E4 nhận `from` có múi giờ và `to` không có múi giờ phải trả 200, không lỗi 500 (TypeError)."""
import psycopg
import pytest

from tests.tc_bt3 import QL_TAN_BINH, Ctx


@pytest.fixture()
def x():
    try:
        return Ctx()
    except psycopg.OperationalError as e:
        pytest.skip(f"Không kết nối được PostgreSQL: {e}")


def test_bug10_tron_thoi_gian_co_va_khong_co_mui_gio(x):
    r = x.api.get("/api/technicians/2/appointments", headers=QL_TAN_BINH,
                  params={"from": "2026-11-07T08:00:00+07:00", "to": "2026-11-08T08:00:00"})
    assert r.status_code == 200 and r.json()["items"] == []


def test_bug10_ca_hai_khong_co_mui_gio_van_hop_le(x):
    r = x.api.get("/api/technicians/2/appointments", headers=QL_TAN_BINH,
                  params={"from": "2026-11-07T08:00:00", "to": "2026-11-08T08:00:00"})
    assert r.status_code == 200
