"""Sinh docs/api-docs.md (tiếng Anh) với ví dụ request/response THẬT: gọi từng endpoint trên database thử vừa resetDb.
Chạy:  python -m scripts.gen_api_docs        (cần PostgreSQL như khi chạy test)
Đồng thời xuất docs/openapi.json từ chính ứng dụng (FastAPI)."""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.tc_bt3 import QL_TAN_BINH, Ctx, slot  # noqa: E402

H = QL_TAN_BINH
AUTH = "Required – headers `X-Employee-Id`, `X-Role: QUAN_LY`, `X-Center-Id` (simulated login, see §Authentication)."
COMMON = "| 401 | UNAUTHENTICATED | missing/invalid identity headers |\n| 403 | FORBIDDEN | wrong role, or resource of another service centre (QT-14) |"


def short(obj):
    if isinstance(obj, dict) and isinstance(obj.get("items"), list) and len(obj["items"]) > 2:
        obj = {**obj, "items": obj["items"][:2] + [f"... {len(obj['items']) - 2} more items"]}
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)


def main():
    x = Ctx()
    api, calls = x.api, {}

    def call(key, method, path, body=None, params=None, headers=H):
        r = api.request(method, path, json=body, params=params, headers=headers)
        q = ("?" + "&".join(f"{k}={v}" for k, v in params.items())) if params else ""
        calls[key] = (method, path + q, body, r.status_code, r.json())
        return r

    call("health", "GET", "/health", headers={})
    call("e1", "GET", "/api/tickets", params={"status": "MOI", "page": 1, "size": 20})
    call("e2", "GET", "/api/tickets/1/technician-suggestions")
    call("e3", "POST", "/api/tickets/1/assignment", {"technician_id": 2})
    s, e = slot(9, 0, 30)
    a = call("e5", "POST", "/api/tickets/1/appointments", {"appointment_type": "TRA_MAY", "start_at": s, "end_at": e, "note": "Customer picks up before noon"}).json()
    d0 = s[:10]
    call("e4", "GET", "/api/technicians/2/appointments", params={"from": f"{d0}T00:00:00+07:00", "to": f"{d0}T23:59:00+07:00"})
    call("e14", "GET", f"/api/appointments/{a['appointment_id']}")
    s2, e2 = slot(10, 0, 45)
    call("e15", "PUT", f"/api/appointments/{a['appointment_id']}", {"start_at": s2, "end_at": e2})
    call("e16", "DELETE", f"/api/appointments/{a['appointment_id']}", params={"reason": "Customer is busy, rebook next week"})
    call("e9", "GET", "/api/technicians")
    t = call("e10", "POST", "/api/technicians", {"full_name": "Tran Van Moi", "level": "SO_CAP"}).json()
    call("e11", "GET", f"/api/technicians/{t['technician_id']}")
    call("e12", "PUT", f"/api/technicians/{t['technician_id']}", {"full_name": "Tran Van Moi", "level": "TRUNG_CAP", "is_active": True})
    call("e13", "DELETE", f"/api/technicians/{t['technician_id']}")
    call("err400", "POST", "/api/tickets/2/assignment", {})
    call("err409", "POST", "/api/tickets/1/assignment", {"technician_id": 3})

    E = [
        ("health", "GET /health", "Liveness and database check (used by the docker compose healthcheck).", "None.",
         "None.", "`200 {\"status\":\"ok\",\"db\":\"up\"}`", "| 503 | – | `{\"status\":\"degraded\",\"db\":\"down\"}` – database unreachable; no connection details are returned |", "None."),
        ("e1", "GET /api/tickets  (E1)", "List tickets of the caller's service centre, ordered by committed due date ascending; flags `is_due_soon` (< 24 h) and `is_overdue`.", AUTH,
         "Query: `status` (default `MOI`; MOI, DA_PHAN_CONG, DANG_XU_LY, CHO_LINH_KIEN, HOAN_TAT, DA_DONG, DA_HUY) · `category_id` int · `priority` CAO/TRUNG_BINH/THAP · `page` ≥ 1 (default 1) · `size` 1–100 (default 20).",
         "`200 {page, size, total, items[]}`", "| 400 | VALIDATION_FAILED | invalid status/priority/page/size |\n" + COMMON, "Max 100 items per page."),
        ("e2", "GET /api/tickets/{ticket_id}/technician-suggestions  (E2)", "Up to 3 technicians for the ticket: same centre, active, proficiency ≥ 3 in the ticket's issue category (QT-08), sorted by open tickets ascending then proficiency descending. Also returns the ticket summary for screen M2.", AUTH,
         "Path: `ticket_id` int.", "`200 {ticket_id, category_name, ticket{}, suggestions[], message?}` – `message` when no technician qualifies.", "| 404 | NOT_FOUND | ticket does not exist |\n| 422 | CATEGORY_REQUIRED | ticket has no issue category |\n" + COMMON, "At most 3 suggestions."),
        ("e3", "POST /api/tickets/{ticket_id}/assignment  (E3)", "Assign a NEW ticket to a technician; writes one status-log row in the same transaction. Concurrent requests: exactly one succeeds (conditional UPDATE … WHERE status='MOI', NFR3).", AUTH,
         "Path: `ticket_id` int. Body: `{\"technician_id\": int > 0}`.", "`201 {ticket_id, ticket_code, status, technician_id, assigned_at, status_log{}}`",
         "| 400 | VALIDATION_FAILED | missing/invalid technician_id, malformed JSON |\n| 404 | NOT_FOUND | ticket or technician not found |\n| 409 | INVALID_STATE | ticket is no longer MOI (already assigned) |\n| 422 | TECHNICIAN_NOT_ELIGIBLE / CATEGORY_REQUIRED | QT-08 not met |\n" + COMMON, "One technician per ticket (QT-07)."),
        ("e4", "GET /api/technicians/{technician_id}/appointments  (E4)", "Booked (DA_HEN) appointments of a technician overlapping [from, to).", AUTH,
         "Path: `technician_id` int. Query (ISO 8601; without offset = +07:00): `from`, `to`.", "`200 {technician_id, full_name, items[]}`",
         "| 400 | VALIDATION_FAILED | missing/invalid from/to, range > 7 days or to ≤ from |\n| 404 | NOT_FOUND | technician not found |\n" + COMMON, "Range ≤ 7 days."),
        ("e5", "POST /api/tickets/{ticket_id}/appointments  (E5)", "Book a device hand-over (GIAO_MAY) or return (TRA_MAY) appointment for the technician currently holding the ticket.", AUTH,
         "Path: `ticket_id` int. Body: `{appointment_type: GIAO_MAY|TRA_MAY, start_at, end_at, note?}` (ISO 8601).", "`201 {appointment_id, ticket_id, technician_id, appointment_type, start_at, end_at, status: DA_HEN, note, created_by}`",
         "| 400 | VALIDATION_FAILED | QT-L4-03: 15–120 min, 08:00–18:00, Mon–Sat, in the future; note ≤ 255 chars |\n| 404 | NOT_FOUND | ticket not found |\n| 409 | APPOINTMENT_CONFLICT | overlaps another DA_HEN appointment (QT-L4-02); `fields.suggested_start_at` |\n| 409 | INVALID_STATE | ticket is not open |\n| 422 | TICKET_NOT_ASSIGNED | ticket has no technician (QT-L4-04) |\n" + COMMON, "Overlap also blocked by a database EXCLUDE constraint."),
        ("e14", "GET /api/appointments/{appointment_id}  (E14)", "Read one appointment.", AUTH, "Path: `appointment_id` int.", "`200 {appointment_id, ticket_id, ticket_code, center_id, technician_id, appointment_type, start_at, end_at, status, note, created_by}`",
         "| 404 | NOT_FOUND | appointment not found |\n" + COMMON, "None."),
        ("e15", "PUT /api/appointments/{appointment_id}  (E15)", "Reschedule a booked appointment (same QT-L4-03 rules, conflict check ignores the appointment itself).", AUTH,
         "Path: `appointment_id` int. Body: `{start_at, end_at, note?}`.", "`200` – updated appointment.",
         "| 400 | VALIDATION_FAILED | invalid time slot or note > 255 chars |\n| 404 | NOT_FOUND | appointment not found |\n| 409 | APPOINTMENT_CONFLICT / INVALID_STATE | overlap, or not DA_HEN / already started (QT-L4-06) |\n" + COMMON, "Only DA_HEN appointments that have not started."),
        ("e16", "DELETE /api/appointments/{appointment_id}?reason=…  (E16)", "Cancel an appointment (soft delete: status → DA_HUY, QT-13).", AUTH,
         "Path: `appointment_id` int. Query: `reason` 10–255 chars (URL-encoded).", "`200` – appointment with `status: DA_HUY`.",
         "| 400 | VALIDATION_FAILED | missing reason or length out of range |\n| 404 | NOT_FOUND | appointment not found |\n| 409 | INVALID_STATE | already cancelled or already started |\n" + COMMON, "No physical delete."),
        ("e9", "GET /api/technicians  (E9)", "Technicians of the caller's centre with their number of open tickets.", AUTH, "Query: `include_inactive` bool (default false).", "`200 {center_id, items[]}`", COMMON, "None."),
        ("e10", "POST /api/technicians  (E10)", "Create a technician in the caller's centre (centre taken from the caller, QT-14).", AUTH,
         "Body: `{full_name: 2–120 chars, level: SO_CAP|TRUNG_CAP|CAO_CAP}`.", "`201 {technician_id, full_name, center_id, level, is_active}`", "| 400 | VALIDATION_FAILED | invalid full_name or level |\n" + COMMON, "None."),
        ("e11", "GET /api/technicians/{technician_id}  (E11)", "Read one technician.", AUTH, "Path: `technician_id` int.", "`200 {technician_id, full_name, center_id, level, is_active}`", "| 404 | NOT_FOUND | technician not found |\n" + COMMON, "None."),
        ("e12", "PUT /api/technicians/{technician_id}  (E12)", "Update name, level and active flag.", AUTH,
         "Path: `technician_id` int. Body: `{full_name, level, is_active (default true)}`.", "`200` – updated technician.",
         "| 400 | VALIDATION_FAILED | invalid fields |\n| 404 | NOT_FOUND | technician not found |\n| 409 | TECHNICIAN_HAS_OPEN_TICKETS | deactivating a technician who still holds open tickets |\n" + COMMON, "Centre cannot be changed."),
        ("e13", "DELETE /api/technicians/{technician_id}  (E13)", "Deactivate a technician (soft delete: `is_active = false`, QT-13).", AUTH, "Path: `technician_id` int.", "`200` – technician with `is_active: false`.",
         "| 404 | NOT_FOUND | technician not found |\n| 409 | TECHNICIAN_HAS_OPEN_TICKETS | technician still holds open tickets |\n" + COMMON, "No physical delete."),
    ]
    L = ["# API Documentation – Smart CRM, flow L4 (Technician assignment & appointments), track SE", "",
         f"Base URL: `http://localhost:3000` · Version 1.0.0 · Interactive docs: `http://localhost:3000/docs` · OpenAPI: `docs/openapi.json`  ",
         f"Examples below are REAL request/response pairs generated by `python -m scripts.gen_api_docs` on the sample data ({datetime.now():%Y-%m-%d %H:%M}).", "",
         "## Conventions",
         "- JSON in/out, UTF-8. Times are ISO 8601; a time without offset is read as Vietnam time (+07:00).",
         "- Every error uses one shape: `{\"error\": {\"code\": \"...\", \"message\": \"...\", \"fields\": {...}}}`. Database unavailable → `503 DATABASE_UNAVAILABLE`; unexpected error → `500 INTERNAL_ERROR` without internal details.",
         "- **Authentication:** the prototype simulates login (out of scope, W8). Every `/api/*` call sends `X-Employee-Id` (1…2⁶³−1), `X-Role` (`QUAN_LY`) and `X-Center-Id` (1…2³¹−1). Missing/out-of-range → 401; data of another centre → 403.",
         "- 13 business endpoints (E1–E5, E9–E16; E6–E8 postponed, see docs/thay-doi-thiet-ke.md TD-09) + `/health`.", ""]
    for key, title, desc, auth, params, ok, errs, limits in E:
        m, p, b, st, resp = calls[key]
        L += [f"## {title}", f"1. **Description:** {desc}", f"2. **Authentication:** {auth}", f"3. **Parameters:** {params}",
              f"4. **Success response:** {ok}", "5. **Errors:**", "", "| HTTP | code | when |", "|---|---|---|", errs, "",
              f"6. **Limits:** {limits}", "7. **Example (real run):**", "", "```http", f"{m} {p}" + ("" if key == "health" else "\nX-Employee-Id: 3\nX-Role: QUAN_LY\nX-Center-Id: 2")]
        if b is not None:
            L += ["Content-Type: application/json", "", json.dumps(b, ensure_ascii=False)]
        L += ["```", "", f"Response `{st}`:", "", "```json", short(resp), "```", ""]
    L += ["## Error examples (real run)", ""]
    for key, label in (("err400", "Missing field (TC-07)"), ("err409", "Ticket already assigned")):
        m, p, b, st, resp = calls[key]
        L += [f"**{label}** – `{m} {p}` body `{json.dumps(b)}` → `{st}`", "", "```json", short(resp), "```", ""]
    (ROOT / "docs" / "api-docs.md").write_text("\n".join(L), encoding="utf-8")
    from src.backend.main import app
    (ROOT / "docs" / "openapi.json").write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("Đã ghi docs/api-docs.md và docs/openapi.json")


if __name__ == "__main__":
    main()
