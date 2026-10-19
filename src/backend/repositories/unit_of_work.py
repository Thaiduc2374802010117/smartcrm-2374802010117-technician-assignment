"""Unit of Work: các repository dùng chung MỘT kết nối, commit hoặc rollback cùng nhau (NFR3)."""
from ..db import connect
from .status_log_repository import StatusLogRepository
from .technician_repository import TechnicianRepository
from .ticket_repository import TicketRepository


class UnitOfWork:
    def __init__(self, connect_fn=connect):
        self._connect = connect_fn

    def __enter__(self):
        self.conn = self._connect()
        self.tickets = TicketRepository(self.conn)
        self.technicians = TechnicianRepository(self.conn)
        self.logs = StatusLogRepository(self.conn)
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()
        return False
