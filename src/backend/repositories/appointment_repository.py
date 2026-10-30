"""AppointmentRepository – truy cập bảng appointment (US5, FR5)."""
import psycopg


class AppointmentConflict(Exception):
    """CSDL từ chối vì trùng lịch (ràng buộc EXCLUDE ex_appt_no_overlap – QT-L4-02)."""


class AppointmentRepository:
    def __init__(self, conn):
        self.conn = conn

    def list_for_technician(self, technician_id: int, start, end):
        return self.conn.execute(
            "SELECT a.appointment_id, a.ticket_id, k.ticket_code, a.appointment_type, a.start_at, a.end_at, a.status "
            "FROM appointment a JOIN ticket k ON k.ticket_id = a.ticket_id "
            "WHERE a.technician_id = %s AND a.status = 'DA_HEN' AND a.start_at < %s AND a.end_at > %s "
            "ORDER BY a.start_at", (technician_id, end, start)).fetchall()

    def find_conflict(self, technician_id: int, start, end, exclude_id: int | None = None):
        """Lịch hẹn DA_HEN của cùng kỹ thuật viên giao nhau với khoảng [start, end) (bỏ qua chính lịch hẹn đang sửa)."""
        return self.conn.execute(
            "SELECT appointment_id, start_at, end_at FROM appointment "
            "WHERE technician_id = %s AND status = 'DA_HEN' AND start_at < %s AND end_at > %s "
            "AND appointment_id IS DISTINCT FROM %s ORDER BY start_at LIMIT 1",
            (technician_id, end, start, exclude_id)).fetchone()

    def get(self, appointment_id: int):
        return self.conn.execute(
            "SELECT a.appointment_id, a.ticket_id, k.ticket_code, k.center_id, a.technician_id, a.appointment_type, "
            "a.start_at, a.end_at, a.status, a.note, a.created_by FROM appointment a "
            "JOIN ticket k ON k.ticket_id = a.ticket_id WHERE a.appointment_id = %s", (appointment_id,)).fetchone()

    def update_time(self, appointment_id: int, start, end, note):
        try:
            with self.conn.transaction():
                return self.conn.execute(
                    "UPDATE appointment SET start_at = %s, end_at = %s, note = %s "
                    "WHERE appointment_id = %s AND status = 'DA_HEN' RETURNING appointment_id, ticket_id, technician_id, "
                    "appointment_type, start_at, end_at, status, note", (start, end, note, appointment_id)).fetchone()
        except psycopg.errors.ExclusionViolation as e:
            raise AppointmentConflict() from e

    def cancel(self, appointment_id: int, note):
        """Không xoá vật lý (QT-13): chỉ chuyển DA_HEN → DA_HUY."""
        return self.conn.execute(
            "UPDATE appointment SET status = 'DA_HUY', note = %s WHERE appointment_id = %s AND status = 'DA_HEN' "
            "RETURNING appointment_id, ticket_id, technician_id, appointment_type, start_at, end_at, status, note",
            (note, appointment_id)).fetchone()

    def create(self, ticket_id, technician_id, appointment_type, start, end, note, created_by):
        try:
            with self.conn.transaction():   # savepoint: nếu EXCLUDE từ chối thì không làm hỏng giao dịch ngoài
                return self.conn.execute(
                    "INSERT INTO appointment (ticket_id, technician_id, appointment_type, start_at, end_at, note, created_by) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING appointment_id, ticket_id, technician_id, "
                    "appointment_type, start_at, end_at, status, note, created_by",
                    (ticket_id, technician_id, appointment_type, start, end, note, created_by)).fetchone()
        except psycopg.errors.ExclusionViolation as e:
            raise AppointmentConflict() from e
