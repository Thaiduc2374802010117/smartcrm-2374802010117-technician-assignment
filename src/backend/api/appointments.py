"""Endpoint lịch hẹn giao – nhận máy (US5, FR5, UC4).
E4  GET  /api/technicians/{technician_id}/appointments?from=&to= – lịch hẹn của kỹ thuật viên
E5  POST /api/tickets/{ticket_id}/appointments                   – tạo lịch hẹn, chặn trùng lịch
E14 GET    /api/appointments/{id}  – xem một lịch hẹn
E15 PUT    /api/appointments/{id}  – sửa giờ lịch hẹn (kiểm QT-L4-03, chống trùng)
E16 DELETE /api/appointments/{id}?reason=...  – hủy lịch hẹn kèm lý do (chuyển DA_HUY, không xoá – QT-13)"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from ..repositories.unit_of_work import UnitOfWork
from ..services.appointment_service import AppointmentService
from .auth import CurrentUser, require_role

router = APIRouter(tags=["Lịch hẹn"])
service = AppointmentService(UnitOfWork)


class AppointmentIn(BaseModel):
    appointment_type: str = Field(description="GIAO_MAY hoặc TRA_MAY")
    start_at: datetime
    end_at: datetime
    note: str | None = None


@router.get("/api/technicians/{technician_id}/appointments", summary="E4 – Lịch hẹn của kỹ thuật viên")
def list_appointments(technician_id: int, from_: datetime = Query(alias="from"), to: datetime = Query(),
                      user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return service.list_for_technician(technician_id, from_, to, user)


@router.post("/api/tickets/{ticket_id}/appointments", status_code=201, summary="E5 – Tạo lịch hẹn giao – nhận máy")
def create_appointment(ticket_id: int, payload: AppointmentIn, user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return service.create(ticket_id, payload.appointment_type, payload.start_at, payload.end_at, payload.note, user)


class RescheduleIn(BaseModel):
    start_at: datetime
    end_at: datetime
    note: str | None = None


@router.get("/api/appointments/{appointment_id}", summary="E14 – Xem một lịch hẹn")
def get_appointment(appointment_id: int, user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return service.get(appointment_id, user)


@router.put("/api/appointments/{appointment_id}", summary="E15 – Sửa giờ lịch hẹn")
def reschedule_appointment(appointment_id: int, payload: RescheduleIn, user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return service.reschedule(appointment_id, payload.start_at, payload.end_at, payload.note, user)


@router.delete("/api/appointments/{appointment_id}", summary="E16 – Hủy lịch hẹn")
def cancel_appointment(appointment_id: int, reason: str = Query(description="Lý do hủy, 10–255 ký tự"),
                       user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return service.cancel(appointment_id, reason, user)
