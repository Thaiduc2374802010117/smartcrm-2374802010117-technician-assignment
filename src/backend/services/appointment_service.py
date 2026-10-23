"""AppointmentService – đặt lịch hẹn giao – nhận máy, chặn trùng lịch (US5, FR5, UC4 · E4, E5).

Quy tắc: QT-L4-02 (không trùng lịch DA_HEN của cùng kỹ thuật viên), QT-L4-03 (15–120 phút, 08:00–18:00,
thứ Hai – thứ Bảy, bắt đầu sau hiện tại), QT-L4-04 (chỉ cho phiếu đã có kỹ thuật viên), QT-14.
"""
from datetime import datetime, time, timedelta, timezone

from ..repositories.appointment_repository import AppointmentConflict
from .errors import Forbidden, InvalidState, NotFound, RuleViolation, ValidationFailed

VN = timezone(timedelta(hours=7))            # giờ Việt Nam, không có giờ mùa hè
OPEN = {"DA_PHAN_CONG", "DANG_XU_LY", "CHO_LINH_KIEN"}
TYPES = {"GIAO_MAY", "TRA_MAY"}
WORK_START, WORK_END = time(8, 0), time(18, 0)
MIN_LEN, MAX_LEN = timedelta(minutes=15), timedelta(minutes=120)
MAX_RANGE = timedelta(days=7)


def _vn(dt: datetime) -> datetime:
    return (dt if dt.tzinfo else dt.replace(tzinfo=VN)).astimezone(VN)


def check_time_slot(start: datetime, end: datetime, now: datetime) -> dict:
    """QT-L4-03. Trả về {tên trường: lý do} – rỗng nghĩa là khung giờ hợp lệ."""
    s, e, n = _vn(start), _vn(end), _vn(now)
    errors = {}
    if s <= n:
        errors["start_at"] = "Lịch hẹn phải bắt đầu sau thời điểm hiện tại"
    elif s.weekday() == 6:
        errors["start_at"] = "Lịch hẹn phải trong thứ Hai đến thứ Bảy"
    elif s.time() < WORK_START:
        errors["start_at"] = "Lịch hẹn phải bắt đầu từ 08:00"
    elif s.time() >= WORK_END:
        errors["start_at"] = "Lịch hẹn phải bắt đầu trước 18:00"
    if e <= s:
        errors["end_at"] = "Thời gian kết thúc phải sau thời gian bắt đầu"
    elif e.date() != s.date() or e.time() > WORK_END:
        errors["end_at"] = "Lịch hẹn phải kết thúc trước hoặc đúng 18:00 cùng ngày"
    elif not MIN_LEN <= e - s <= MAX_LEN:
        errors["end_at"] = "Lịch hẹn phải dài từ 15 đến 120 phút"
    return errors


class AppointmentService:
    def __init__(self, uow_factory):
        self.uow_factory = uow_factory

    def list_for_technician(self, technician_id: int, start: datetime, end: datetime, user):
        if end <= start or end - start > MAX_RANGE:
            raise ValidationFailed("Dữ liệu không hợp lệ", fields={"to": "Khoảng thời gian phải từ 1 phút đến 7 ngày"})
        with self.uow_factory() as uow:
            technician = uow.technicians.get(technician_id)
            if technician is None:
                raise NotFound("Không tìm thấy kỹ thuật viên", fields={"technician_id": str(technician_id)})
            if technician["center_id"] != user.center_id:                    # QT-14
                raise Forbidden("Không có quyền xem lịch của kỹ thuật viên trung tâm khác")
            rows = uow.appointments.list_for_technician(technician_id, start, end)
        return {"technician_id": technician_id, "full_name": technician["full_name"], "items": [dict(r) for r in rows]}

    def create(self, ticket_id: int, appointment_type: str, start: datetime, end: datetime, note, user, now=None):
        now = now or datetime.now(VN)
        fields = check_time_slot(start, end, now)
        if appointment_type not in TYPES:
            fields["appointment_type"] = "Loại lịch hẹn không hợp lệ"
        if note is not None and len(note) > 255:
            fields["note"] = "Ghi chú tối đa 255 ký tự"
        if fields:                                                          # UC4 ngoại lệ 4a
            raise ValidationFailed("Khung giờ không hợp lệ", fields=fields)
        with self.uow_factory() as uow:
            ticket = uow.tickets.get(ticket_id)
            if ticket is None:
                raise NotFound("Không tìm thấy phiếu", fields={"ticket_id": str(ticket_id)})
            if ticket["center_id"] != user.center_id:                       # QT-14
                raise Forbidden("Không có quyền với phiếu của trung tâm khác")
            if ticket["technician_id"] is None:                             # QT-L4-04, UC4 ngoại lệ 1a
                raise RuleViolation("Phiếu chưa được phân công", code="TICKET_NOT_ASSIGNED")
            if ticket["status"] not in OPEN:
                raise InvalidState("Chỉ đặt lịch hẹn cho phiếu đang mở", fields={"current_status": ticket["status"]})
            technician_id = ticket["technician_id"]                         # lịch hẹn gắn với KTV đang giữ phiếu
            conflict = uow.appointments.find_conflict(technician_id, start, end)
            if conflict is None:
                try:
                    return dict(uow.appointments.create(ticket_id, technician_id, appointment_type, start, end,
                                                        note, user.employee_id))
                except AppointmentConflict:   # hai yêu cầu đặt cùng lúc: EXCLUDE ở CSDL là chốt chặn cuối
                    conflict = uow.appointments.find_conflict(technician_id, start, end)
        raise InvalidState("Kỹ thuật viên đã có lịch hẹn trong khung giờ này", code="APPOINTMENT_CONFLICT",   # UC4 – 5a
                           fields={"conflict_appointment_id": str(conflict["appointment_id"]) if conflict else "",
                                   "conflict_start_at": conflict["start_at"].isoformat() if conflict else "",
                                   "conflict_end_at": conflict["end_at"].isoformat() if conflict else "",
                                   "suggested_start_at": conflict["end_at"].isoformat() if conflict else ""})
