"""Nạp bộ Dataset Smart CRM chính thức (tải từ E-learning) vào 6 bảng của ERD.

Cách dùng (từ thư mục gốc repo, đã chạy migration):
    python -m src.backend.seed_dataset --data data/official --reopen 5

- Đọc issue_categories.csv, technicians.csv, technician_skills.csv, tickets_history.csv (và service_centers.csv
  để in tên trung tâm). Giữ nguyên mã gốc của dataset. Dòng không hợp lệ bị bỏ qua và in lý do.
- --reopen N: dữ liệu lịch sử hầu hết đã đóng, nên chọn N phiếu gần nhất mỗi trung tâm, đặt lại trạng thái MOI,
  bỏ kỹ thuật viên và dời thời gian về hiện tại (hạn cam kết theo QT-04) để mô phỏng phiếu mới tiếp nhận (TD-10).
- Chạy lại nhiều lần được: xoá dữ liệu cũ của 6 bảng rồi nạp lại.
"""
import argparse
import csv
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from .db import ROOT, connect

CATEGORIES = [("MAN_HINH", "TRUNG_BINH"), ("PIN", "TRUNG_BINH"), ("SAC", "THAP"),
              ("PHAN_MEM", "THAP"), ("NUOC_VAO", "CAO"), ("KHAC", "THAP")]          # Bảng 3.1 case study
SLA_HOURS = {"CAO": 24, "TRUNG_BINH": 72, "THAP": 120}                               # QT-04
STATUSES = {"MOI", "DA_PHAN_CONG", "DANG_XU_LY", "CHO_LINH_KIEN", "HOAN_TAT", "DA_DONG", "DA_HUY"}
ALIASES = {
    "technician_id": ["technician_id", "ma_ktv", "ma_ky_thuat_vien", "tech_id", "id"],
    "full_name": ["full_name", "ho_ten", "ten", "name", "technician_name", "ten_ky_thuat_vien"],
    "center_id": ["center_id", "ma_trung_tam", "service_center_id", "trung_tam"],
    "level": ["level", "bac", "bac_tay_nghe", "cap_bac"],
    "is_active": ["is_active", "active", "dang_lam_viec", "con_lam_viec"],
    "category": ["category_id", "category", "category_name", "issue_category", "nhom_su_co"],
    "proficiency": ["proficiency", "muc_thanh_thao", "tay_nghe", "skill_level"],
    "ticket_code": ["ticket_code", "ma_phieu", "code"],
    "issue_desc": ["issue_desc", "mo_ta_loi", "description", "mo_ta"],
    "priority": ["priority", "muc_uu_tien"],
    "status": ["status", "trang_thai"],
    "received_at": ["received_at", "ngay_tiep_nhan", "created_at", "thoi_diem_tiep_nhan"],
    "due_date": ["due_date", "han_cam_ket", "deadline"],
}


def norm(text: str) -> str:
    t = unicodedata.normalize("NFD", str(text or "").strip().lower()).replace("đ", "d")
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return "_".join(t.replace("-", " ").split())


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096); f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample else csv.excel
        rows = [{norm(k): (v or "").strip() for k, v in r.items() if k} for r in csv.DictReader(f, dialect=dialect)]
    return rows


def pick(row: dict, field: str, default=None):
    for a in ALIASES[field]:
        if row.get(a) not in (None, ""):
            return row[a]
    return default


def to_bool(v, default=True):
    if v is None or v == "":
        return default
    return norm(v) in {"1", "true", "t", "yes", "y", "co", "x", "dang_lam_viec"}


def to_dt(v):
    if not v:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d"):
        try:
            return datetime.strptime(v[:19] if "T" in v or len(v) >= 19 else v, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(v)
    except ValueError:
        return None


def enum(v, allowed, default=None):
    n = norm(v).upper()
    if n in allowed:
        return n
    return {"CAO": "CAO", "HIGH": "CAO", "TRUNG_BINH": "TRUNG_BINH", "MEDIUM": "TRUNG_BINH", "THAP": "THAP", "LOW": "THAP",
            "SOCAP": "SO_CAP", "SO_CAP": "SO_CAP", "TRUNGCAP": "TRUNG_CAP", "CAOCAP": "CAO_CAP"}.get(n.replace(" ", ""), default)


CAT_IDS: dict = {}   # mã hoặc tên nhóm sự cố (đã chuẩn hóa) -> category_id trong CSDL


def category_id(v):
    if v is None or v == "":
        return None
    return CAT_IDS.get(str(v).strip()) or CAT_IDS.get(norm(v).upper())


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default="data/official", help="thư mục chứa các file CSV của bộ dataset")
    ap.add_argument("--reopen", type=int, default=5, help="số phiếu gần nhất mỗi trung tâm đặt lại MOI (0 = không)")
    args = ap.parse_args()
    folder = (ROOT / args.data) if not Path(args.data).is_absolute() else Path(args.data)
    files = {k: folder / f"{k}.csv" for k in ("technicians", "technician_skills", "tickets_history")}
    cat_file, center_file = folder / "issue_categories.csv", folder / "service_centers.csv"
    missing = [str(p) for p in files.values() if not p.exists()]
    if missing:
        sys.exit("Thiếu file dataset: " + ", ".join(missing) + "\nTải 'Mekong Mobile – Dataset Smart CRM' trên E-learning và giải nén vào " + str(folder))
    techs, skills, tickets = (read_csv(files[k]) for k in ("technicians", "technician_skills", "tickets_history"))
    for name, rows in (("technicians", techs), ("technician_skills", skills), ("tickets_history", tickets)):
        print(f"Đọc {name}.csv: {len(rows)} dòng · cột: {', '.join(rows[0].keys()) if rows else '(rỗng)'}")
    reject = Counter()
    with connect() as conn:
        conn.execute("TRUNCATE ticket_status_log, appointment, ticket, technician_skill, technician, issue_category RESTART IDENTITY CASCADE")
        cats = read_csv(cat_file) if cat_file.exists() else [
            {"category_id": str(i), "category_name": n, "default_priority": p} for i, (n, p) in enumerate(CATEGORIES, 1)]
        print(f"Đọc issue_categories.csv: {len(cats)} dòng" if cat_file.exists() else "Không có issue_categories.csv – dùng danh mục Bảng 3.1")
        for r in cats:
            cid, name = r.get("category_id", ""), norm(r.get("category_name", "")).upper()
            if not (cid.isdigit() and name):
                reject["issue_categories: thiếu mã hoặc tên"] += 1; continue
            conn.execute("INSERT INTO issue_category (category_id, category_name, default_priority, is_active) VALUES (%s,%s,%s,%s)",
                         (int(cid), name, enum(r.get("default_priority", ""), set(SLA_HOURS), "TRUNG_BINH"), to_bool(r.get("is_active"))))
            CAT_IDS[cid] = int(cid); CAT_IDS[name] = int(cid)
        conn.execute("SELECT setval('issue_category_category_id_seq', GREATEST((SELECT max(category_id) FROM issue_category), 1))")
        print("  Nhóm sự cố: " + ", ".join(f"{v}={k}" for k, v in CAT_IDS.items() if not k.isdigit()))
        tech_ids = set()
        for r in techs:
            tid, center = pick(r, "technician_id"), pick(r, "center_id")
            if not (tid and str(tid).isdigit() and center and str(center).isdigit()):
                reject["technicians: thiếu mã KTV hoặc mã trung tâm"] += 1; continue
            conn.execute("INSERT INTO technician (technician_id, full_name, center_id, level, is_active) VALUES (%s,%s,%s,%s,%s) "
                         "ON CONFLICT (technician_id) DO NOTHING",
                         (int(tid), pick(r, "full_name", f"Kỹ thuật viên {tid}"), int(center),
                          enum(pick(r, "level", ""), {"SO_CAP", "TRUNG_CAP", "CAO_CAP"}, "TRUNG_CAP"), to_bool(pick(r, "is_active"))))
            tech_ids.add(int(tid))
        conn.execute("SELECT setval('technician_technician_id_seq', GREATEST((SELECT max(technician_id) FROM technician), 1))")
        for r in skills:
            tid, cat, prof = pick(r, "technician_id"), category_id(pick(r, "category")), pick(r, "proficiency")
            if not (tid and str(tid).isdigit() and int(tid) in tech_ids and cat and prof and str(prof).isdigit() and 1 <= int(prof) <= 5):
                reject["technician_skills: KTV/nhóm sự cố/tay nghề không hợp lệ"] += 1; continue
            conn.execute("INSERT INTO technician_skill VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", (int(tid), cat, int(prof)))
        for r in tickets:
            code, center = pick(r, "ticket_code"), pick(r, "center_id")
            received = to_dt(pick(r, "received_at"))
            prio = enum(pick(r, "priority", ""), set(SLA_HOURS), None)
            if not (code and center and str(center).isdigit() and received and prio):
                reject["tickets_history: thiếu mã phiếu/trung tâm/thời điểm tiếp nhận/mức ưu tiên"] += 1; continue
            status = enum(pick(r, "status", ""), STATUSES, "DA_DONG")
            tech = pick(r, "technician_id")
            tech = int(tech) if tech and str(tech).isdigit() and int(tech) in tech_ids else None
            if tech is None and status not in ("MOI", "DA_HUY"):
                status = "DA_DONG" if status in ("HOAN_TAT", "DA_DONG") else "MOI"
            due = to_dt(pick(r, "due_date")) or received + timedelta(hours=SLA_HOURS[prio])
            cur = conn.execute("INSERT INTO ticket (ticket_code, center_id, category_id, issue_desc, priority, status, technician_id, "
                               "received_at, due_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (ticket_code) DO NOTHING",
                               (code, int(center), category_id(pick(r, "category")), pick(r, "issue_desc", "(không có mô tả)"),
                                prio, status, tech if status not in ("MOI",) else None,
                                received.replace(tzinfo=None), due.replace(tzinfo=None)))
            if cur.rowcount == 0:
                reject["tickets_history: trùng mã phiếu"] += 1
        if args.reopen > 0:
            conn.execute(
                "WITH pick AS (SELECT ticket_id, row_number() OVER (ORDER BY received_at DESC, ticket_id) AS rn, "
                "  row_number() OVER (PARTITION BY center_id ORDER BY received_at DESC, ticket_id) AS k FROM ticket "
                "  WHERE category_id IS NOT NULL) "
                "UPDATE ticket t SET status = 'MOI', technician_id = NULL, "
                "  received_at = now() - (p.rn || ' minutes')::interval, "
                "  due_date = now() - (p.rn || ' minutes')::interval + CASE t.priority WHEN 'CAO' THEN interval '24 hour' "
                "    WHEN 'TRUNG_BINH' THEN interval '72 hour' ELSE interval '120 hour' END "
                "FROM pick p WHERE p.ticket_id = t.ticket_id AND p.k <= %s", (args.reopen,))
        counts = {t: conn.execute(f"SELECT count(*) AS n FROM {t}").fetchone()["n"]
                  for t in ("issue_category", "technician", "technician_skill", "ticket")}
        centers = conn.execute("SELECT center_id, count(*) FILTER (WHERE status = 'MOI') AS moi, count(*) AS n "
                               "FROM ticket GROUP BY center_id ORDER BY center_id").fetchall()
    names = {r.get("center_id"): r.get("center_name", "") for r in read_csv(center_file)} if center_file.exists() else {}
    print("Đã nạp: " + " · ".join(f"{k} {v}" for k, v in counts.items()))
    for c in centers:
        print(f"  Trung tâm {c['center_id']} {names.get(str(c['center_id']), '')}: {c['n']} phiếu, {c['moi']} phiếu MOI")
    for reason, n in reject.items():
        print(f"  Bỏ qua {n} dòng – {reason}")
    print("Đăng nhập giao diện bằng một mã trung tâm ở trên (Quản lý trung tâm).")


if __name__ == "__main__":
    main()
