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

    OPEN_STATUSES = ("DA_PHAN_CONG", "DANG_XU_LY", "CHO_LINH_KIEN")   # "phiếu đang mở" theo bảng thuật ngữ SRS

    def suggest(self, center_id: int, category_id: int, min_proficiency: int, limit: int = 3):
        """Lọc, đếm và sắp xếp ngay trong CSDL (lập luận kiến trúc số 3 – NFR2):
        cùng trung tâm, đang làm việc, tay nghề >= min_proficiency ở nhóm sự cố;
        sắp theo số phiếu đang mở tăng dần, bằng nhau thì tay nghề giảm dần."""
        return self.conn.execute(
            "SELECT t.technician_id, t.full_name, t.level, s.proficiency, "
            "  (SELECT count(*) FROM ticket k WHERE k.technician_id = t.technician_id "
            "     AND k.is_deleted = false AND k.status = ANY(%s)) AS open_ticket_count "
            "FROM technician t JOIN technician_skill s ON s.technician_id = t.technician_id "
            "WHERE t.center_id = %s AND t.is_active AND s.category_id = %s AND s.proficiency >= %s "
            "ORDER BY open_ticket_count ASC, s.proficiency DESC, t.technician_id ASC LIMIT %s",
            (list(self.OPEN_STATUSES), center_id, category_id, min_proficiency, limit)).fetchall()

    COLUMNS = "technician_id, full_name, center_id, level, is_active"

    def list_by_center(self, center_id: int, include_inactive: bool = False):
        rows = self.conn.execute(
            f"SELECT t.technician_id, t.full_name, t.center_id, t.level, t.is_active, "
            f"  (SELECT count(*) FROM ticket k WHERE k.technician_id = t.technician_id AND k.is_deleted = false "
            f"     AND k.status = ANY(%s)) AS open_ticket_count "
            f"FROM technician t WHERE t.center_id = %s AND (t.is_active OR %s) ORDER BY t.full_name",
            (list(self.OPEN_STATUSES), center_id, include_inactive)).fetchall()
        return rows

    def create(self, full_name: str, center_id: int, level: str):
        return self.conn.execute(
            f"INSERT INTO technician (full_name, center_id, level) VALUES (%s, %s, %s) RETURNING {self.COLUMNS}",
            (full_name, center_id, level)).fetchone()

    def update(self, technician_id: int, full_name: str, level: str, is_active: bool):
        return self.conn.execute(
            f"UPDATE technician SET full_name = %s, level = %s, is_active = %s WHERE technician_id = %s "
            f"RETURNING {self.COLUMNS}", (full_name, level, is_active, technician_id)).fetchone()

    def count_open_tickets(self, technician_id: int) -> int:
        return self.conn.execute(
            "SELECT count(*) AS n FROM ticket WHERE technician_id = %s AND is_deleted = false AND status = ANY(%s)",
            (technician_id, list(self.OPEN_STATUSES))).fetchone()["n"]
