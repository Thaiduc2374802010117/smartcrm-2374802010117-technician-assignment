"""Endpoint lịch hẹn giao – nhận máy (US5, FR5, UC4).
E4  GET  /api/technicians/{technician_id}/appointments?from=&to= – lịch hẹn của kỹ thuật viên
E5  POST /api/tickets/{ticket_id}/appointments                   – tạo lịch hẹn, chặn trùng lịch"""
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
