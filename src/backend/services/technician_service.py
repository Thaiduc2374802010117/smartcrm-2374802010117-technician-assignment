"""TechnicianService – quản lý danh mục kỹ thuật viên của trung tâm (CRUD thực thể thứ hai cho BT2 – TD-13).

Quy tắc: QT-14 (chỉ trung tâm của quản lý), QT-13 (không xoá vật lý – "xoá" là ngừng hoạt động is_active = false),
không ngừng hoạt động kỹ thuật viên đang giữ phiếu mở (phải đổi kỹ thuật viên trước – QT-07).
"""
from .errors import Forbidden, InvalidState, NotFound, ValidationFailed

LEVELS = {"SO_CAP", "TRUNG_CAP", "CAO_CAP"}


def validate(full_name, level) -> dict:
    fields = {}
    if not isinstance(full_name, str) or not 2 <= len(full_name.strip()) <= 120:
        fields["full_name"] = "Họ tên từ 2 đến 120 ký tự"
    if level not in LEVELS:
        fields["level"] = "Bậc phải là SO_CAP, TRUNG_CAP hoặc CAO_CAP"
    return fields


class TechnicianService:
    def __init__(self, uow_factory):
        self.uow_factory = uow_factory

    def _own(self, uow, technician_id, user):
        technician = uow.technicians.get(technician_id)
        if technician is None:
            raise NotFound("Không tìm thấy kỹ thuật viên", fields={"technician_id": str(technician_id)})
        if technician["center_id"] != user.center_id:                       # QT-14
            raise Forbidden("Không có quyền với kỹ thuật viên của trung tâm khác")
        return technician

    def list(self, user, include_inactive=False):
        with self.uow_factory() as uow:
            return {"center_id": user.center_id,
                    "items": [dict(r) for r in uow.technicians.list_by_center(user.center_id, include_inactive)]}

    def get(self, technician_id, user):
        with self.uow_factory() as uow:
            return dict(self._own(uow, technician_id, user))

    def create(self, full_name, level, user):
        fields = validate(full_name, level)
        if fields:
            raise ValidationFailed("Dữ liệu không hợp lệ", fields=fields)
        with self.uow_factory() as uow:                                     # trung tâm lấy theo người dùng (QT-14)
            return dict(uow.technicians.create(full_name.strip(), user.center_id, level))

    def update(self, technician_id, full_name, level, is_active, user):
        fields = validate(full_name, level)
        if fields:
            raise ValidationFailed("Dữ liệu không hợp lệ", fields=fields)
        with self.uow_factory() as uow:
            self._own(uow, technician_id, user)
            if not is_active and uow.technicians.count_open_tickets(technician_id) > 0:
                raise InvalidState("Kỹ thuật viên đang giữ phiếu mở – đổi kỹ thuật viên cho các phiếu đó trước",
                                   code="TECHNICIAN_HAS_OPEN_TICKETS")
            return dict(uow.technicians.update(technician_id, full_name.strip(), level, is_active))

    def deactivate(self, technician_id, user):
        """DELETE = ngừng hoạt động (không xoá vật lý – còn lịch sử phiếu tham chiếu)."""
        with self.uow_factory() as uow:
            t = self._own(uow, technician_id, user)
            if uow.technicians.count_open_tickets(technician_id) > 0:
                raise InvalidState("Kỹ thuật viên đang giữ phiếu mở – đổi kỹ thuật viên cho các phiếu đó trước",
                                   code="TECHNICIAN_HAS_OPEN_TICKETS")
            return dict(uow.technicians.update(technician_id, t["full_name"], t["level"], False))
