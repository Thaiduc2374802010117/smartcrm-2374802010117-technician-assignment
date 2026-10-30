"""Endpoint danh mục kỹ thuật viên – CRUD thực thể thứ hai cho BT2 (TD-13).
E9  GET    /api/technicians              – danh sách kỹ thuật viên của trung tâm
E10 POST   /api/technicians              – thêm kỹ thuật viên
E11 GET    /api/technicians/{id}         – xem một kỹ thuật viên
E12 PUT    /api/technicians/{id}         – sửa họ tên, bậc, trạng thái làm việc
E13 DELETE /api/technicians/{id}         – ngừng hoạt động (is_active = false, không xoá vật lý – QT-13)"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..repositories.unit_of_work import UnitOfWork
from ..services.technician_service import TechnicianService
from .auth import CurrentUser, require_role

router = APIRouter(prefix="/api/technicians", tags=["Kỹ thuật viên"])
service = TechnicianService(UnitOfWork)


class TechnicianIn(BaseModel):
    full_name: str
    level: str


class TechnicianUpdate(TechnicianIn):
    is_active: bool = True


@router.get("", summary="E9 – Danh sách kỹ thuật viên của trung tâm")
def list_technicians(include_inactive: bool = False, user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return service.list(user, include_inactive)


@router.post("", status_code=201, summary="E10 – Thêm kỹ thuật viên")
def create_technician(payload: TechnicianIn, user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return service.create(payload.full_name, payload.level, user)


@router.get("/{technician_id}", summary="E11 – Xem một kỹ thuật viên")
def get_technician(technician_id: int, user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return service.get(technician_id, user)


@router.put("/{technician_id}", summary="E12 – Sửa kỹ thuật viên")
def update_technician(technician_id: int, payload: TechnicianUpdate, user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return service.update(technician_id, payload.full_name, payload.level, payload.is_active, user)


@router.delete("/{technician_id}", summary="E13 – Ngừng hoạt động kỹ thuật viên")
def deactivate_technician(technician_id: int, user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return service.deactivate(technician_id, user)
