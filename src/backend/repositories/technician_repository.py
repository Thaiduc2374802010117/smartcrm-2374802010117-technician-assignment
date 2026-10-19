"""TechnicianRepository – truy cập bảng technician và technician_skill."""


class TechnicianRepository:
    def __init__(self, conn):
        self.conn = conn

    def get(self, technician_id: int):
        return self.conn.execute(
            "SELECT technician_id, full_name, center_id, level, is_active FROM technician WHERE technician_id = %s",
            (technician_id,)).fetchone()

    def proficiency(self, technician_id: int, category_id: int):
        row = self.conn.execute(
            "SELECT proficiency FROM technician_skill WHERE technician_id = %s AND category_id = %s",
            (technician_id, category_id)).fetchone()
        return row["proficiency"] if row else None
