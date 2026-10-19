"""AssignmentService – phân công kỹ thuật viên cho phiếu (US2, US3 · FR2, FR3 · UC2 · endpoint E3).

Quy tắc áp dụng: QT-06 (ghi lịch sử phiếu), QT-07 (tối đa 1 kỹ thuật viên),
QT-08 (cùng trung tâm, tay nghề >= 3 ở nhóm sự cố của phiếu), QT-L4-01 (chỉ phân công phiếu MOI), QT-14.
"""
from .errors import Forbidden, InvalidState, NotFound, RuleViolation

MIN_PROFICIENCY = 3   # QT-08


def is_eligible(technician: dict, ticket: dict, proficiency) -> bool:
    """QT-08: kỹ thuật viên đang làm việc, cùng trung tâm với phiếu, tay nghề >= 3 ở nhóm sự cố của phiếu."""
    return (technician["is_active"]
            and technician["center_id"] == ticket["center_id"]
            and proficiency is not None and proficiency >= MIN_PROFICIENCY)


class AssignmentService:
    def __init__(self, uow_factory):
        self.uow_factory = uow_factory

    def assign(self, ticket_id: int, technician_id: int, user):
        with self.uow_factory() as uow:   # một giao dịch: phân công + ghi lịch sử cùng thành công hoặc cùng hủy (NFR3)
            ticket = uow.tickets.get(ticket_id)
            if ticket is None:
                raise NotFound("Không tìm thấy phiếu", fields={"ticket_id": str(ticket_id)})
            if ticket["center_id"] != user.center_id:                       # QT-14
                raise Forbidden("Không có quyền với phiếu của trung tâm khác")
            if ticket["status"] != "MOI":                                   # QT-L4-01, UC2 ngoại lệ 5a
                raise InvalidState("Phiếu đã được phân công. Dùng chức năng đổi kỹ thuật viên.",
                                   fields={"current_status": ticket["status"]})
            if ticket["category_id"] is None:
                raise RuleViolation("Phiếu chưa có nhóm sự cố nên không phân công được", code="CATEGORY_REQUIRED")
            technician = uow.technicians.get(technician_id)
            if technician is None:
                raise NotFound("Không tìm thấy kỹ thuật viên", fields={"technician_id": str(technician_id)})
            proficiency = uow.technicians.proficiency(technician_id, ticket["category_id"])
            if not is_eligible(technician, ticket, proficiency):             # QT-08, UC2 ngoại lệ 5b
                raise RuleViolation("Kỹ thuật viên không đủ tay nghề (cần >= 3) hoặc không cùng trung tâm",
                                    code="TECHNICIAN_NOT_ELIGIBLE", fields={"technician_id": str(technician_id)})
            updated = uow.tickets.assign_if_new(ticket_id, technician_id)   # NFR3: UPDATE ... WHERE status = 'MOI'
            if updated is None:                                             # người khác vừa phân công trước
                raise InvalidState("Phiếu vừa được phân công bởi người khác", fields={"current_status": "DA_PHAN_CONG"})
            log = uow.logs.add(ticket_id, "MOI", "DA_PHAN_CONG", None, technician_id, user.employee_id)   # QT-06
        return {**dict(updated), "assigned_at": log["changed_at"], "status_log": dict(log)}
