"""Unit test TechnicianService (CRUD kỹ thuật viên – TD-13) – không cần CSDL."""
from dataclasses import dataclass

import pytest

from src.backend.services.errors import Forbidden, InvalidState, ValidationFailed
from src.backend.services.technician_service import TechnicianService


@dataclass(frozen=True)
class User:
    employee_id: int = 3
    role: str = "QUAN_LY"
    center_id: int = 2


class FakeUow:
    def __init__(self, open_tickets=0):
        self.rows = {1: {"technician_id": 1, "full_name": "Lê Thị A", "center_id": 2, "level": "TRUNG_CAP", "is_active": True},
                     5: {"technician_id": 5, "full_name": "Võ Thị E", "center_id": 1, "level": "CAO_CAP", "is_active": True}}
        self.open = open_tickets
        outer = self

        class Techs:
            def get(self, i): return outer.rows.get(i)
            def create(self, name, center, level):
                r = {"technician_id": 9, "full_name": name, "center_id": center, "level": level, "is_active": True}
                outer.rows[9] = r
                return r
            def update(self, i, name, level, active):
                outer.rows[i] = {**outer.rows[i], "full_name": name, "level": level, "is_active": active}
                return outer.rows[i]
            def count_open_tickets(self, i): return outer.open

        self.technicians = Techs()

    def __call__(self): return self
    def __enter__(self): return self
    def __exit__(self, *e): return False


def test_them_ky_thuat_vien_gan_dung_trung_tam_nguoi_dung():                 # luồng đúng – QT-14
    r = TechnicianService(FakeUow()).create("  Trần Văn Mới ", "SO_CAP", User())
    assert r["center_id"] == 2 and r["full_name"] == "Trần Văn Mới"


@pytest.mark.parametrize("name, level", [("A", "SO_CAP"), ("x" * 121, "SO_CAP"), ("Trần Văn B", "CHUYEN_GIA")])
def test_tu_choi_ho_ten_hoac_bac_khong_hop_le(name, level):                   # biên 2/120 ký tự, dữ liệu sai
    with pytest.raises(ValidationFailed):
        TechnicianService(FakeUow()).create(name, level, User())


def test_khong_ngung_hoat_dong_ky_thuat_vien_dang_giu_phieu_mo():              # ngoại lệ – QT-07
    with pytest.raises(InvalidState) as e:
        TechnicianService(FakeUow(open_tickets=2)).deactivate(1, User())
    assert e.value.code == "TECHNICIAN_HAS_OPEN_TICKETS"


def test_ngung_hoat_dong_la_xoa_mem():                                        # QT-13
    uow = FakeUow()
    assert TechnicianService(uow).deactivate(1, User())["is_active"] is False
    assert 1 in uow.rows                                                      # vẫn còn trong CSDL


def test_khong_sua_ky_thuat_vien_trung_tam_khac():                            # QT-14
    with pytest.raises(Forbidden):
        TechnicianService(FakeUow()).update(5, "Võ Thị E", "CAO_CAP", True, User())
