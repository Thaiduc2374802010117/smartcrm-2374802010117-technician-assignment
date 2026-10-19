"""Kiểm tra quyền dùng chung, chạy trước mọi endpoint (NFR4, QT-14).
Prototype giả lập người dùng bằng 3 header (W8 – chưa có đăng nhập thật):
X-Employee-Id, X-Role (QUAN_LY | KY_THUAT_VIEN), X-Center-Id."""
from dataclasses import dataclass

from fastapi import Header

from ..services.errors import Forbidden
from .errors import Unauthenticated

ROLES = {"QUAN_LY", "KY_THUAT_VIEN"}


@dataclass(frozen=True)
class CurrentUser:
    employee_id: int
    role: str
    center_id: int


def current_user(x_employee_id: str | None = Header(None), x_role: str | None = Header(None),
                 x_center_id: str | None = Header(None)) -> CurrentUser:
    try:
        user = CurrentUser(int(x_employee_id), x_role, int(x_center_id))
    except (TypeError, ValueError):
        raise Unauthenticated("Thiếu hoặc sai thông tin người dùng (X-Employee-Id, X-Role, X-Center-Id)")
    if user.role not in ROLES:
        raise Unauthenticated("Vai trò không hợp lệ")
    return user


def require_role(role: str):
    def dependency(x_employee_id: str | None = Header(None), x_role: str | None = Header(None),
                   x_center_id: str | None = Header(None)) -> CurrentUser:
        user = current_user(x_employee_id, x_role, x_center_id)
        if user.role != role:
            raise Forbidden("Chức năng này chỉ dành cho " + ("Quản lý trung tâm" if role == "QUAN_LY" else "Kỹ thuật viên"))
        return user
    return dependency
