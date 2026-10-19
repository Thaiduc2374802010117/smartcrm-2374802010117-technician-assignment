"""StatusLogRepository – ghi lịch sử phiếu (QT-06)."""


class StatusLogRepository:
    def __init__(self, conn):
        self.conn = conn

    def add(self, ticket_id, from_status, to_status, from_technician_id, to_technician_id, changed_by, note=None):
        return self.conn.execute(
            "INSERT INTO ticket_status_log (ticket_id, from_status, to_status, from_technician_id, to_technician_id, "
            "changed_by, note) VALUES (%s, %s, %s, %s, %s, %s, %s) "
            "RETURNING log_id, from_status, to_status, to_technician_id, changed_at, changed_by",
            (ticket_id, from_status, to_status, from_technician_id, to_technician_id, changed_by, note)).fetchone()
