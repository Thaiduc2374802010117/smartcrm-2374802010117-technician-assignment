"""Endpoint phiếu bảo hành – module Phân công (buổi 8).
E1  GET  /api/tickets?status=MOI            – danh sách phiếu chờ phân công (US1, FR1)
E3  POST /api/tickets/{ticket_id}/assignment – phân công kỹ thuật viên (US3, FR3)
E2, E6, E7 sẽ bổ sung ở các buổi sau."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..repositories.unit_of_work import UnitOfWork
from ..services.assignment_service import AssignmentService
from ..services.ticket_query_service import TicketQueryService
from .auth import CurrentUser, require_role

router = APIRouter(prefix="/api/tickets", tags=["Phiếu bảo hành"])
query_service = TicketQueryService(UnitOfWork)
assignment_service = AssignmentService(UnitOfWork)


class AssignmentIn(BaseModel):
    technician_id: int = Field(gt=0, description="Kỹ thuật viên được chọn trong danh sách gợi ý")


@router.get("", summary="E1 – Danh sách phiếu chờ phân công")
def list_tickets(status: str = "MOI", category_id: int | None = None, priority: str | None = None,
                 page: int = 1, size: int = 20, user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return query_service.list_tickets(user, status, category_id, priority, page, size)


@router.post("/{ticket_id}/assignment", status_code=201, summary="E3 – Phân công kỹ thuật viên cho phiếu")
def assign(ticket_id: int, payload: AssignmentIn, user: CurrentUser = Depends(require_role("QUAN_LY"))):
    return assignment_service.assign(ticket_id, payload.technician_id, user)
