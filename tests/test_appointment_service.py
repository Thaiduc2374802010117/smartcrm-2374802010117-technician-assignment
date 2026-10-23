"""Unit test lớp nghiệp vụ AppointmentService (UC4 · QT-L4-02, QT-L4-03, QT-L4-04) – không cần CSDL.
Ba loại: luồng đúng · giá trị biên · dữ liệu sai. Chạy:  python -m pytest -v"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest

from src.backend.services.appointment_service import AppointmentService, check_time_slot
from src.backend.services.errors import InvalidState, RuleViolation, ValidationFailed

VN = timezone(timedelta(hours=7))
NOW = datetime(2026, 10, 9, 7, 0, tzinfo=VN)            # thứ Sáu 09/10/2026, 07:00
SAT = datetime(2026, 10, 10, tzinfo=VN)                 # thứ Bảy
SUN = datetime(2026, 10, 11, tzinfo=VN)                 # Chủ nhật


def at(day, h, m=0):
    return day.replace(hour=h, minute=m)


@dataclass(frozen=True)
class User:
    employee_id: int = 3
    role: str = "QUAN_LY"
    center_id: int = 4


class FakeUow:
    def __init__(self, technician_id=1, existing=()):
        self.ticket = {"ticket_id": 1, "center_id": 4, "status": "DA_PHAN_CONG", "technician_id": technician_id}
        self.existing, self.created = list(existing), []
        outer = self

        class Tickets:
            def get(self, ticket_id): return outer.ticket

        class Appointments:
            def find_conflict(self, technician_id, start, end):
                return next(({"appointment_id": 9, "start_at": s, "end_at": e} for s, e in outer.existing
                             if s < end and e > start), None)

            def create(self, ticket_id, technician_id, t, start, end, note, by):
                outer.created.append((start, end))
                return {"appointment_id": 10, "status": "DA_HEN", "start_at": start, "end_at": end}

        self.tickets, self.appointments = Tickets(), Appointments()

    def __call__(self): return self
    def __enter__(self): return self
    def __exit__(self, *exc): return False


def create(uow, start, end):
    return AppointmentService(uow).create(1, "TRA_MAY", start, end, None, User(), now=NOW)


# ---------- luồng đúng ----------
def test_tao_lich_hen_trong_khung_gio_con_trong():                       # AC5.2
    uow = FakeUow(existing=[(at(SAT, 9), at(SAT, 9, 30))])
    r = create(uow, at(SAT, 10), at(SAT, 10, 30))
    assert r["status"] == "DA_HEN" and len(uow.created) == 1


# ---------- dữ liệu sai / ngoại lệ ----------
def test_tu_choi_lich_hen_trung_0915_voi_lich_0900_0930():               # AC5.1 – QT-L4-02 (gợi ý của GV)
    uow = FakeUow(existing=[(at(SAT, 9), at(SAT, 9, 30))])
    with pytest.raises(InvalidState) as e:
        create(uow, at(SAT, 9, 15), at(SAT, 9, 45))
    assert e.value.code == "APPOINTMENT_CONFLICT"
    assert e.value.fields["suggested_start_at"] == at(SAT, 9, 30).isoformat()   # khung giờ trống gần nhất
    assert uow.created == []


def test_tu_choi_phieu_chua_co_ky_thuat_vien():                           # AC5.3 – QT-L4-04, UC4 ngoại lệ 1a
    with pytest.raises(RuleViolation) as e:
        create(FakeUow(technician_id=None), at(SAT, 10), at(SAT, 10, 30))
    assert e.value.code == "TICKET_NOT_ASSIGNED"


def test_tu_choi_lich_hen_vao_chu_nhat():                                  # QT-L4-03
    with pytest.raises(ValidationFailed) as e:
        create(FakeUow(), at(SUN, 10), at(SUN, 10, 30))
    assert "start_at" in e.value.fields


def test_tu_choi_lich_hen_trong_qua_khu():                                 # QT-L4-03
    assert "start_at" in check_time_slot(at(NOW, 6), at(NOW, 6, 30), NOW)


# ---------- giá trị biên ----------
@pytest.mark.parametrize("start, end, ok", [
    ((8, 0), (8, 15), True),      # đúng 15 phút, bắt đầu đúng 08:00
    ((8, 0), (8, 14), False),     # 14 phút – dưới mức tối thiểu
    ((16, 0), (18, 0), True),     # đúng 120 phút, kết thúc đúng 18:00
    ((16, 0), (18, 1), False),    # vượt 18:00
    ((7, 59), (8, 30), False),    # bắt đầu trước 08:00
    ((9, 0), (11, 1), False),     # 121 phút – vượt mức tối đa
])
def test_bien_khung_gio_qt_l4_03(start, end, ok):
    assert (check_time_slot(at(SAT, *start), at(SAT, *end), NOW) == {}) is ok


def test_lich_hen_ke_tiep_sat_nhau_khong_tinh_la_trung():                  # biên: 09:30 bắt đầu ngay khi lịch trước kết thúc
    uow = FakeUow(existing=[(at(SAT, 9), at(SAT, 9, 30))])
    assert create(uow, at(SAT, 9, 30), at(SAT, 10))["status"] == "DA_HEN"
