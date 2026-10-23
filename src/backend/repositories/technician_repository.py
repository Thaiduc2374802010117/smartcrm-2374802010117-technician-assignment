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
