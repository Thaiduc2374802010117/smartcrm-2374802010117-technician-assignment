"""12 test case của Test Report BT3 dưới dạng pytest – cùng định nghĩa với scripts/run_tc.py (tests/tc_bt3.py)."""
import psycopg
import pytest

from tests.tc_bt3 import CASES, execute, reset_db


@pytest.fixture(scope="module", autouse=True)
def need_db():
    try:
        reset_db()
    except psycopg.OperationalError as e:
        pytest.skip(f"Không kết nối được PostgreSQL: {e}")


@pytest.mark.parametrize("case", CASES, ids=[c.id for c in CASES])
def test_bt3(case, monkeypatch):
    monkeypatch.setenv("DB_NAME", "smartcrm_test")
    actual, ok = execute(case)
    assert ok, f"{case.id} – mong đợi: {case.mong_doi} | thực tế: {actual}"
