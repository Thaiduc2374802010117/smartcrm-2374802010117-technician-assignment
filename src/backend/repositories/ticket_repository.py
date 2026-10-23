"""TicketRepository – truy cập bảng ticket."""


class TicketRepository:
    def __init__(self, conn):
        self.conn = conn

    def get(self, ticket_id: int):
        return self.conn.execute(
            "SELECT ticket_id, ticket_code, center_id, category_id, priority, status, technician_id, due_date "
            "FROM ticket WHERE ticket_id = %s AND is_deleted = false", (ticket_id,)).fetchone()

    def list_by_center(self, center_id: int, status: str, category_id, priority, limit: int, offset: int):
        """Danh sách phiếu của một trung tâm, sắp theo hạn cam kết tăng dần (index center_id, status, due_date – NFR1)."""
        where = "t.center_id = %s AND t.status = %s AND t.is_deleted = false"
        params = [center_id, status]
        if category_id is not None:
            where += " AND t.category_id = %s"
            params.append(category_id)
        if priority is not None:
            where += " AND t.priority = %s"
            params.append(priority)
        total = self.conn.execute(f"SELECT count(*) AS n FROM ticket t WHERE {where}", params).fetchone()["n"]
        rows = self.conn.execute(
            "SELECT t.ticket_id, t.ticket_code, t.category_id, c.category_name, t.priority, t.status, "
            "t.received_at, t.due_date FROM ticket t LEFT JOIN issue_category c ON c.category_id = t.category_id "
            f"WHERE {where} ORDER BY t.due_date ASC LIMIT %s OFFSET %s", params + [limit, offset]).fetchall()
        return rows, total

    def assign_if_new(self, ticket_id: int, technician_id: int):
        """UPDATE có điều kiện (NFR3): chỉ một yêu cầu đồng thời đổi được phiếu từ MOI sang DA_PHAN_CONG.
        Trả về None nếu phiếu không còn ở trạng thái MOI."""
        return self.conn.execute(
            "UPDATE ticket SET technician_id = %s, status = 'DA_PHAN_CONG' "
            "WHERE ticket_id = %s AND status = 'MOI' AND is_deleted = false "
            "RETURNING ticket_id, ticket_code, status, technician_id", (technician_id, ticket_id)).fetchone()

    def get_detail(self, ticket_id: int):
        """Thông tin phiếu cho màn hình M2 (mã, nhóm sự cố, mức ưu tiên, hạn cam kết, trạng thái, mô tả lỗi)."""
        return self.conn.execute(
            "SELECT t.ticket_id, t.ticket_code, t.center_id, t.category_id, c.category_name, t.priority, t.status, "
            "t.technician_id, t.issue_desc, t.received_at, t.due_date FROM ticket t "
            "LEFT JOIN issue_category c ON c.category_id = t.category_id "
            "WHERE t.ticket_id = %s AND t.is_deleted = false", (ticket_id,)).fetchone()
