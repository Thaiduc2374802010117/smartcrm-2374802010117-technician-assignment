"""Unit test lớp nghiệp vụ AssignmentService (UC2, QT-08, QT-L4-01) – không cần CSDL.
Chạy:  python -m pytest -v"""
from dataclasses import dataclass

import pytest

from src.backend.services.assignment_service import AssignmentService
from src.backend.services.errors import Forbidden, InvalidState, RuleViolation


@dataclass(frozen=True)
class User:
    employee_id: int = 3
    role: str = "QUAN_LY"
    center_id: int = 4


class FakeUow:
    """Thay cho UnitOfWork thật: dữ liệu giữ trong bộ nhớ."""
    def __init__(self, ticket, technicians, skills, race=False):
        self.ticket, self.techs, self.skills, self.race, self.logged = ticket, technicians, skills, race, []
        outer = self

        class Tickets:
            def get(self, ticket_id): return outer.ticket
            def assign_if_new(self, ticket_id, technician_id):
                if outer.race or outer.ticket["status"] != "MOI":
                    return None   # người khác đã phân công trước (NFR3)
                outer.ticket = {**outer.ticket, "status": "DA_PHAN_CONG", "technician_id": technician_id}
                return {"ticket_id": ticket_id, "ticket_code": outer.ticket["ticket_code"],
                        "status": "DA_PHAN_CONG", "technician_id": technician_id}

        class Technicians:
            def get(self, technician_id): return outer.techs.get(technician_id)
            def proficiency(self, technician_id, category_id): return outer.skills.get((technician_id, category_id))

        class Logs:
            def add(self, *args, **kwargs):
                outer.logged.append(args)
                return {"log_id": len(outer.logged), "changed_at": "2026-10-10T08:00:00+07:00"}

        self.tickets, self.technicians, self.logs = Tickets(), Technicians(), Logs()

    def __call__(self): return self
    def __enter__(self): return self
    def __exit__(self, *exc): return False


def make(status="MOI", race=False):
    ticket = {"ticket_id": 1, "ticket_code": "BH000231/2026", "center_id": 4, "category_id": 1, "status": status}
    techs = {1: {"technician_id": 1, "center_id": 4, "is_active": True},    # Lê Thị A – tay nghề 4
             4: {"technician_id": 4, "center_id": 4, "is_active": True},    # Ngô Văn D – tay nghề 2
             5: {"technician_id": 5, "center_id": 1, "is_active": True}}    # Võ Thị E – khác trung tâm
    skills = {(1, 1): 4, (4, 1): 2, (5, 1): 5}
    return FakeUow(ticket, techs, skills, race)


def test_phan_cong_thanh_cong_ghi_dung_mot_dong_lich_su():   # AC3.1
    uow = make()
    result = AssignmentService(uow).assign(1, 1, User())
    assert result["status"] == "DA_PHAN_CONG" and result["technician_id"] == 1
    assert len(uow.logged) == 1 and uow.logged[0][1:3] == ("MOI", "DA_PHAN_CONG")


def test_tu_choi_ky_thuat_vien_tay_nghe_duoi_3():            # AC3.3 – QT-08
    uow = make()
    with pytest.raises(RuleViolation) as e:
        AssignmentService(uow).assign(1, 4, User())
    assert e.value.code == "TECHNICIAN_NOT_ELIGIBLE" and uow.logged == []


def test_tu_choi_ky_thuat_vien_khac_trung_tam():             # QT-08
    with pytest.raises(RuleViolation):
        AssignmentService(make()).assign(1, 5, User())


def test_tu_choi_phieu_da_phan_cong():                       # AC3.2 – QT-L4-01
    with pytest.raises(InvalidState):
        AssignmentService(make(status="DA_PHAN_CONG")).assign(1, 1, User())


def test_tu_choi_phieu_cua_trung_tam_khac():                 # QT-14
    with pytest.raises(Forbidden):
        AssignmentService(make()).assign(1, 1, User(center_id=1))


def test_hai_yeu_cau_dong_thoi_yeu_cau_sau_bi_tu_choi_va_khong_ghi_lich_su():   # UC2 ngoại lệ 5a – NFR3
    uow = make(race=True)
    with pytest.raises(InvalidState):
        AssignmentService(uow).assign(1, 1, User())
    assert uow.logged == []
