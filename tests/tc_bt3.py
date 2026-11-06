"""12 test case của Test Report BT3 (docs/test-report.md) – đủ năm loại: luồng đúng · biên · dữ liệu sai · bảo mật · tái lập.

Mỗi test case: dựng tiền điều kiện bằng resetDb (migration + dữ liệu mẫu db/seed) trên database RIÊNG smartcrm_test,
thực hiện đúng các bước qua API thật (FastAPI TestClient), rồi ghi KẾT QUẢ THỰC TẾ: mã trạng thái, mã lỗi
và tác dụng phụ (đếm bản ghi trước/sau). Dùng chung cho:
  - python -m scripts.run_tc TC-05      (chạy một test case, in đủ tám cột – để chụp ảnh / chạy lại tại chỗ)
  - python -m pytest -v                 (tests/test_tc_bt3.py)
"""
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable

TEST_DB = os.getenv("TEST_DB_NAME", "smartcrm_test")
VN = timezone(timedelta(hours=7))
QL_TAN_BINH = {"X-Employee-Id": "3", "X-Role": "QUAN_LY", "X-Center-Id": "2"}     # quản lý TTBH Tân Bình (mã 2)
QL_QUAN_10 = {"X-Employee-Id": "9", "X-Role": "QUAN_LY", "X-Center-Id": "1"}      # quản lý TTBH Quận 10 (mã 1)


def reset_db():
    """resetDb: tạo database thử nếu chưa có, chạy migration + dữ liệu mẫu (xoá rồi nạp lại)."""
    from src.backend.db import ROOT, connect
    with connect("postgres") as c:
        c.autocommit = True
        if not c.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB,)).fetchone():
            c.execute(f'CREATE DATABASE "{TEST_DB}"')
    with connect(TEST_DB) as c:
        for folder in ("migrations", "seed"):
            for f in sorted((ROOT / "db" / folder).glob("*.sql")):
                c.execute(f.read_text(encoding="utf-8"))


class Ctx:
    def __init__(self):
        os.environ["DB_NAME"] = TEST_DB                     # API ghi vào database thử, không đụng smartcrm
        reset_db()
        from fastapi.testclient import TestClient
        from src.backend.main import app
        self.api = TestClient(app, raise_server_exceptions=False)

    def count(self, sql, *params):
        from src.backend.db import connect
        with connect(TEST_DB) as c:
            return c.execute(f"SELECT count(*) AS n FROM {sql}", params).fetchone()["n"]

    def one(self, sql, *params):
        from src.backend.db import connect
        with connect(TEST_DB) as c:
            return c.execute(sql, params).fetchone()


def slot(h, m=0, minutes=30, days=2):
    """Khung giờ hợp lệ trong tương lai (bỏ qua Chủ nhật), giờ Việt Nam."""
    d = datetime.now(VN) + timedelta(days=days)
    if d.weekday() == 6:
        d += timedelta(days=1)
    s = d.replace(hour=h, minute=m, second=0, microsecond=0)
    return s.isoformat(), (s + timedelta(minutes=minutes)).isoformat()


def body_error(r):
    try:
        return r.json().get("error") or {}
    except Exception:
        return {}


def err(r):
    e = body_error(r)
    return f'{r.status_code} {e.get("code", "")} {e.get("fields") or ""}'.strip()


@dataclass
class TestCase:
    id: str
    loai: str
    uu_tien: str
    ten: str
    tien_dk: str
    cac_buoc: list
    du_lieu: str
    mong_doi: str
    run: Callable = field(repr=False)


def _assigned(x):
    x.api.post("/api/tickets/1/assignment", json={"technician_id": 2}, headers=QL_TAN_BINH)


def tc01(x):
    r = x.api.get("/api/tickets/1/technician-suggestions", headers=QL_TAN_BINH)
    names = [s["full_name"] for s in r.json().get("suggestions", [])] if r.status_code == 200 else []
    ok = r.status_code == 200 and names == ["Trần Văn B", "Lê Thị A", "Phạm Văn C"]
    return f"{r.status_code}; gợi ý = {names}; Ngô Văn D (tay nghề 2) {'không có' if 'Ngô Văn D' not in names else 'CÓ'} trong danh sách", ok


def tc02(x):
    before = x.count("ticket_status_log WHERE ticket_id = 1")
    r = x.api.post("/api/tickets/1/assignment", json={"technician_id": 2}, headers=QL_TAN_BINH)
    t = x.one("SELECT status, technician_id FROM ticket WHERE ticket_id = 1")
    after = x.count("ticket_status_log WHERE ticket_id = 1")
    ok = r.status_code == 201 and t["status"] == "DA_PHAN_CONG" and t["technician_id"] == 2 and (before, after) == (0, 1)
    return f"{r.status_code}; phiếu {t['status']}, technician_id={t['technician_id']}; ticket_status_log {before} -> {after}", ok


def tc03(x):
    _assigned(x)
    s, e = slot(9, 0, 30)
    before = x.count("appointment")
    r = x.api.post("/api/tickets/1/appointments", headers=QL_TAN_BINH, json={"appointment_type": "TRA_MAY", "start_at": s, "end_at": e})
    after = x.count("appointment")
    st = r.json().get("status") if r.status_code == 201 else err(r)
    return f"{r.status_code}; status={st}; appointment {before} -> {after}", r.status_code == 201 and st == "DA_HEN" and (before, after) == (0, 1)


def tc04(x):
    n0 = x.count("technician")
    r1 = x.api.post("/api/technicians", json={"full_name": "Trần Văn Mới", "level": "SO_CAP"}, headers=QL_TAN_BINH)
    tid = r1.json().get("technician_id")
    n1 = x.count("technician")
    r2 = x.api.delete(f"/api/technicians/{tid}", headers=QL_TAN_BINH)
    n2 = x.count("technician")
    active = x.one("SELECT is_active FROM technician WHERE technician_id = %s", tid)["is_active"]
    ok = r1.status_code == 201 and r2.status_code == 200 and active is False and (n0, n1, n2) == (6, 7, 7)
    return f"POST {r1.status_code} (id={tid}); DELETE {r2.status_code}; is_active={active}; technician {n0} -> {n1} -> {n2} (xoá mềm)", ok


def tc05(x):
    _assigned(x)
    s, e = slot(10, 0, 15)
    r = x.api.post("/api/tickets/1/appointments", headers=QL_TAN_BINH, json={"appointment_type": "GIAO_MAY", "start_at": s, "end_at": e})
    n = x.count("appointment")
    return f"{r.status_code}; appointment 0 -> {n}", r.status_code == 201 and n == 1


def tc06(x):
    _assigned(x)
    s, e = slot(10, 0, 14)
    r = x.api.post("/api/tickets/1/appointments", headers=QL_TAN_BINH, json={"appointment_type": "GIAO_MAY", "start_at": s, "end_at": e})
    n = x.count("appointment")
    fields = body_error(r).get("fields", {})
    return f"{err(r)}; appointment 0 -> {n}", r.status_code == 400 and "end_at" in fields and n == 0


def tc07(x):
    before = x.count("ticket_status_log")
    r = x.api.post("/api/tickets/1/assignment", json={}, headers=QL_TAN_BINH)
    st = x.one("SELECT status FROM ticket WHERE ticket_id = 1")["status"]
    after = x.count("ticket_status_log")
    fields = body_error(r).get("fields", {})
    ok = r.status_code == 400 and fields.get("technician_id") == "Trường bắt buộc" and st == "MOI" and before == after == 0
    return f"{err(r)}; phiếu vẫn {st}; ticket_status_log {before} -> {after}", ok


def tc08(x):
    _assigned(x)
    s, e = slot(9, 0, 30)
    a = x.api.post("/api/tickets/1/appointments", headers=QL_TAN_BINH, json={"appointment_type": "TRA_MAY", "start_at": s, "end_at": e}).json()
    s2, e2 = slot(14, 0, 30)
    r = x.api.put(f"/api/appointments/{a['appointment_id']}", headers=QL_TAN_BINH, json={"start_at": s2, "end_at": e2, "note": "x" * 300})
    row = x.one("SELECT start_at FROM appointment WHERE appointment_id = %s", a["appointment_id"])
    unchanged = row["start_at"].astimezone(VN).hour == 9
    fields = body_error(r).get("fields", {})
    return f"{err(r)}; lịch hẹn {'giữ nguyên 09:00' if unchanged else 'BỊ ĐỔI'}", r.status_code == 400 and "note" in fields and unchanged


def tc09(x):
    _assigned(x)
    s, e = slot(9, 0, 30)
    x.api.post("/api/tickets/1/appointments", headers=QL_TAN_BINH, json={"appointment_type": "TRA_MAY", "start_at": s, "end_at": e})
    s2, e2 = slot(9, 15, 30)
    r = x.api.post("/api/tickets/1/appointments", headers=QL_TAN_BINH, json={"appointment_type": "GIAO_MAY", "start_at": s2, "end_at": e2})
    n = x.count("appointment")
    e_ = body_error(r); f = e_.get("fields", {})
    sug = datetime.fromisoformat(f["suggested_start_at"]).astimezone(VN).strftime("%H:%M") if f.get("suggested_start_at") else "-"
    ok = r.status_code == 409 and e_.get("code") == "APPOINTMENT_CONFLICT" and sug == "09:30" and n == 1
    return f"{r.status_code} {e_.get('code')}; gợi ý {sug}; appointment 1 -> {n}", ok


def tc10(x):
    r = x.api.post("/api/tickets/1/assignment", json={"technician_id": 2}, headers=QL_QUAN_10)
    st = x.one("SELECT status FROM ticket WHERE ticket_id = 1")["status"]
    n = x.count("ticket_status_log")
    return f"{err(r)}; phiếu vẫn {st}; ticket_status_log 0 -> {n}", r.status_code == 403 and st == "MOI" and n == 0


def tc11(x):
    h = {**QL_TAN_BINH, "X-Employee-Id": "99999999999999999999"}
    r = x.api.post("/api/tickets/1/assignment", json={"technician_id": 2}, headers=h)
    st = x.one("SELECT status FROM ticket WHERE ticket_id = 1")["status"]
    return f"{err(r)}; phiếu vẫn {st}", r.status_code == 401 and st == "MOI"


def tc12(x):
    from src.backend.db import ROOT, connect
    tables = ["issue_category", "technician", "technician_skill", "ticket", "appointment", "ticket_status_log"]
    counts = []
    for _ in range(2):
        with connect(TEST_DB) as c:
            for folder in ("migrations", "seed"):
                for f in sorted((ROOT / "db" / folder).glob("*.sql")):
                    c.execute(f.read_text(encoding="utf-8"))
            counts.append([c.execute(f"SELECT count(*) AS n FROM {t}").fetchone()["n"] for t in tables])
    return f"lần 1: {counts[0]} · lần 2: {counts[1]} · không lỗi", counts[0] == counts[1] == [6, 6, 10, 13, 0, 0]


CASES = [
    TestCase("TC-01", "Luồng đúng", "Cao", "E2 gợi ý kỹ thuật viên theo QT-08 (AC2.1)",
             "resetDb; phiếu 1 BH000231/2026 (MAN_HINH, MOI, trung tâm 2); KTV A tay nghề 4/2 phiếu mở, B 5/2, C 3/5, D 2/0",
             ["GET /api/tickets/1/technician-suggestions"], "Header quản lý trung tâm 2 (X-Employee-Id 3)",
             "200; thứ tự [Trần Văn B, Lê Thị A, Phạm Văn C]; không có Ngô Văn D", tc01),
    TestCase("TC-02", "Luồng đúng", "Cao", "E3 phân công phiếu MOI (QT-06, QT-07)",
             "resetDb; phiếu 1 ở MOI, chưa có dòng ticket_status_log",
             ["POST /api/tickets/1/assignment"], '{"technician_id": 2} (Trần Văn B)',
             "201; phiếu DA_PHAN_CONG, technician_id=2; ticket_status_log 0 -> 1", tc02),
    TestCase("TC-03", "Luồng đúng", "Cao", "E5 tạo lịch hẹn trong khung giờ trống (AC5.2)",
             "resetDb; phiếu 1 đã phân công cho KTV 2; chưa có lịch hẹn",
             ["POST /api/tickets/1/assignment {technician_id: 2}", "POST /api/tickets/1/appointments"],
             "TRA_MAY, 09:00 – 09:30, ngày làm việc sau 2 ngày", "201; status DA_HEN; appointment 0 -> 1", tc03),
    TestCase("TC-04", "Luồng đúng", "Trung bình", "CRUD kỹ thuật viên: tạo rồi xoá mềm (QT-13)",
             "resetDb; CSDL có 6 bản ghi technician",
             ["POST /api/technicians", "DELETE /api/technicians/{id vừa tạo}"], '{"full_name": "Trần Văn Mới", "level": "SO_CAP"}',
             "201 rồi 200; is_active=false; technician 6 -> 7 -> 7 (không xoá vật lý)", tc04),
    TestCase("TC-05", "Giá trị biên", "Trung bình", "Lịch hẹn dài ĐÚNG 15 phút – mức tối thiểu QT-L4-03 (hợp lệ)",
             "resetDb; phiếu 1 đã phân công cho KTV 2; chưa có lịch hẹn",
             ["POST /api/tickets/1/assignment {technician_id: 2}", "POST /api/tickets/1/appointments"],
             "GIAO_MAY, 10:00 – 10:15", "201; appointment 0 -> 1", tc05),
    TestCase("TC-06", "Giá trị biên", "Trung bình", "Lịch hẹn dài 14 phút – ngay dưới mức tối thiểu (không hợp lệ)",
             "resetDb; phiếu 1 đã phân công cho KTV 2; chưa có lịch hẹn",
             ["POST /api/tickets/1/assignment {technician_id: 2}", "POST /api/tickets/1/appointments"],
             "GIAO_MAY, 10:00 – 10:14", "400 VALIDATION_FAILED, fields có end_at; appointment 0 -> 0", tc06),
    TestCase("TC-07", "Dữ liệu sai", "Cao", "E3 thiếu trường bắt buộc technician_id",
             "resetDb; phiếu 1 ở MOI; ticket_status_log rỗng",
             ["POST /api/tickets/1/assignment"], "{} (body rỗng)",
             "400 VALIDATION_FAILED, fields.technician_id = 'Trường bắt buộc'; phiếu vẫn MOI; ticket_status_log 0 -> 0", tc07),
    TestCase("TC-08", "Dữ liệu sai", "Trung bình", "E15 sửa giờ lịch hẹn kèm ghi chú 300 ký tự (giới hạn 255)",
             "resetDb; phiếu 1 đã phân công cho KTV 2; có lịch hẹn 09:00 – 09:30",
             ["POST /api/tickets/1/assignment", "POST lịch hẹn 09:00 – 09:30", "PUT /api/appointments/{id}"],
             'start 14:00, end 14:30, note = "x" × 300', "400 VALIDATION_FAILED, fields có note; lịch hẹn giữ nguyên 09:00", tc08),
    TestCase("TC-09", "Dữ liệu sai", "Cao", "Lịch hẹn trùng 09:15 – 09:45 với lịch 09:00 – 09:30 (QT-L4-02, AC5.1)",
             "resetDb; phiếu 1 đã phân công cho KTV 2; có lịch hẹn 09:00 – 09:30",
             ["POST /api/tickets/1/assignment", "POST lịch 09:00 – 09:30", "POST lịch 09:15 – 09:45"], "GIAO_MAY, 09:15 – 09:45",
             "409 APPOINTMENT_CONFLICT; gợi ý 09:30; appointment 1 -> 1", tc09),
    TestCase("TC-10", "Bảo mật (A01)", "Cao", "Quản lý trung tâm 1 phân công phiếu của trung tâm 2 (QT-14)",
             "resetDb; phiếu 1 thuộc trung tâm 2, ở MOI",
             ["POST /api/tickets/1/assignment với header của quản lý trung tâm 1"], 'X-Center-Id: 1; {"technician_id": 2}',
             "403 FORBIDDEN; phiếu vẫn MOI; ticket_status_log 0 -> 0", tc10),
    TestCase("TC-11", "Bảo mật", "Trung bình", "Header định danh ngoài phạm vi (giả mạo) phải bị từ chối",
             "resetDb; phiếu 1 ở MOI",
             ["POST /api/tickets/1/assignment với X-Employee-Id ngoài phạm vi BIGINT"], "X-Employee-Id: 99999999999999999999",
             "401 UNAUTHENTICATED; phiếu vẫn MOI", tc11),
    TestCase("TC-12", "Tái lập", "Cao", "Chạy migration + dữ liệu mẫu hai lần liên tiếp (C8)",
             "resetDb", ["Chạy migration + seed lần 1, đếm 6 bảng", "Chạy lại lần 2, đếm 6 bảng"], "db/migrations/*.sql, db/seed/*.sql",
             "Không lỗi; số dòng hai lần bằng nhau [6, 6, 10, 13, 0, 0]", tc12),
]
BY_ID = {c.id: c for c in CASES}


def execute(case: TestCase):
    """Chạy một test case trên CSDL thử vừa reset; trả (kết quả thực tế, PASS?)."""
    try:
        return case.run(Ctx())
    except Exception as e:  # noqa: BLE001 – test case phải ghi lại mọi lỗi thực tế
        return f"LỖI KHI CHẠY: {type(e).__name__}: {e}", False
