"""TicketQueryService – danh sách phiếu chờ phân công (US1, FR1, endpoint E1)."""
from datetime import datetime, timedelta, timezone

from .errors import ValidationFailed

STATUSES = {"MOI", "DA_PHAN_CONG", "DANG_XU_LY", "CHO_LINH_KIEN", "HOAN_TAT", "DA_DONG", "DA_HUY"}
PRIORITIES = {"CAO", "TRUNG_BINH", "THAP"}
DUE_SOON = timedelta(hours=24)   # "Phiếu sắp quá hạn": còn dưới 24 giờ tới hạn cam kết (bảng thuật ngữ SRS)


class TicketQueryService:
    def __init__(self, uow_factory):
        self.uow_factory = uow_factory

    def list_tickets(self, user, status="MOI", category_id=None, priority=None, page=1, size=20, now=None):
        fields = {}
        if status not in STATUSES:
            fields["status"] = "Trạng thái không hợp lệ"
        if priority is not None and priority not in PRIORITIES:
            fields["priority"] = "Mức ưu tiên không hợp lệ"
        if page < 1:
            fields["page"] = "Trang không hợp lệ"
        if not 1 <= size <= 100:
            fields["size"] = "Kích thước trang từ 1 đến 100"
        if fields:
            raise ValidationFailed("Dữ liệu không hợp lệ", fields=fields)
        now = now or datetime.now(timezone.utc)
        with self.uow_factory() as uow:
            # QT-14: trung tâm lấy theo người dùng, không nhận từ tham số
            rows, total = uow.tickets.list_by_center(user.center_id, status, category_id, priority, size, (page - 1) * size)
        items = []
        for r in rows:
            item = dict(r)
            item["is_overdue"] = r["due_date"] < now
            item["is_due_soon"] = not item["is_overdue"] and r["due_date"] - now < DUE_SOON
            items.append(item)
        return {"page": page, "size": size, "total": total, "items": items}
