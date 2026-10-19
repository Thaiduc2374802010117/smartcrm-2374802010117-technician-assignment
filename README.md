# Smart CRM – Phân công kỹ thuật viên và lịch hẹn giao – nhận máy bảo hành

**Sinh viên:** Nguyễn Thái Đức – MSSV: 2374802010117 – Lớp: 261_71ITGR40203_05
**Track:** SE · **Học phần:** Chuyên đề Tốt nghiệp 1 – Trường ĐH Văn Lang
**Luồng nghiệp vụ:** L4 – Phân công kỹ thuật viên và lịch hẹn (case study Mekong Mobile)

## 1. Mục tiêu
Quản lý trung tâm phân công phiếu bảo hành đang ở trạng thái Mới cho kỹ thuật viên phù hợp theo tay nghề,
trung tâm và khối lượng công việc, đặt lịch hẹn giao – nhận máy không trùng lịch, rồi theo dõi phiếu đến khi Hoàn tất.
Giải quyết V2 (không biết phiếu đang ở đâu) và V3 (phân công theo trí nhớ, khối lượng lệch nhau) của case study.

## 2. Yêu cầu môi trường
- Python 3.12 (Windows: dùng lệnh `py` hoặc `python` trong môi trường ảo `.venv`)
- PostgreSQL 16 (quản trị bằng pgAdmin), database `smartcrm`
- Thư viện: xem `requirements.txt` (FastAPI, Uvicorn, psycopg 3, python-dotenv, pytest, httpx)
- Biến môi trường: xem `.env.example` (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `APP_PORT`).
  Mật khẩu chỉ ghi trong `.env`, không commit.

## 3. Hướng dẫn chạy (từ thư mục gốc repo)
1. `py -m venv .venv` → `.venv\Scripts\activate` → `pip install -r requirements.txt`
2. `copy .env.example .env` rồi điền `DB_USER`, `DB_PASSWORD`
3. `python -m src.backend.migrate --seed` – tạo 6 bảng theo DDL BT1 và nạp dữ liệu mẫu
4. `uvicorn src.backend.main:app --reload --port 3000` → mở http://localhost:3000/docs để thử API

## 4. Cấu trúc thư mục – ánh xạ một–một với sơ đồ kiến trúc (docs/architecture.drawio)
| Thư mục / file | Lớp kiến trúc | Nội dung |
|---|---|---|
| `src/backend/api/` | ① Trình bày (Controller) | Endpoint theo API contract, kiểm tra quyền dùng chung (`auth.py`), đổi lỗi nghiệp vụ thành mã HTTP (`errors.py`) |
| `src/backend/services/` | ② Nghiệp vụ | Toàn bộ quy tắc: `assignment_service.py` (QT-06, QT-07, QT-08, QT-L4-01), `ticket_query_service.py`, `appointment_service.py` |
| `src/backend/repositories/` | ③ Truy cập dữ liệu | Câu SQL tham số hóa, `unit_of_work.py` quản lý giao dịch (NFR3) |
| `src/backend/db.py`, `db/` | ④ Lưu trữ | Kết nối PostgreSQL; `db/migrations/` (DDL BT1), `db/seed/` (dữ liệu mẫu) |
| `tests/` | — | Unit test lớp nghiệp vụ |
| `docs/` | — | SRS, sơ đồ `.drawio`, ERD, wireframe, API contract, nhật ký thay đổi thiết kế, ảnh chụp kết quả |

Tài liệu Bài tập 1: `BT1_2374802010117_NguyenThaiDuc.pdf` · thay đổi sau phản hồi BT1: `docs/thay-doi-thiet-ke.md`.
File `.drawio` mở tại app.diagrams.net → Tệp → Mở từ → Thiết bị.

## 5. Kiểm thử
`python -m pytest -v` → 6 test lớp nghiệp vụ `AssignmentService` (AC3.1, AC3.2, AC3.3, QT-08, QT-14, NFR3) PASS.

## 6. Trạng thái hiện tại (buổi 8)
- [x] Khởi tạo project, smoke test `/` và `/db-check` (buổi 2)
- [x] Điều chỉnh thiết kế theo phản hồi BT1 – `docs/thay-doi-thiet-ke.md` (TD-01 … TD-06)
- [x] Cấu trúc `src/backend/` theo 4 lớp của sơ đồ kiến trúc
- [x] Migration tạo 6 bảng theo DDL BT1, chạy lại nhiều lần không lỗi; dữ liệu mẫu rút gọn
- [x] Module Phân công qua đủ 3 lớp: **E1** `GET /api/tickets?status=MOI`, **E3** `POST /api/tickets/{id}/assignment`
- [x] Kiểm chứng NFR3 trên API thật: 2 yêu cầu phân công cùng lúc → 201 và 409, đúng 1 dòng lịch sử
- [x] 6 unit test lớp nghiệp vụ
- [ ] E2 gợi ý kỹ thuật viên, E6 đổi kỹ thuật viên (buổi 10)
- [ ] Module Lịch hẹn E4, E5 và test ràng buộc EXCLUDE 09:00–09:30 / 09:15–09:45 (buổi 10)
- [ ] Nạp dữ liệu từ bộ Dataset Smart CRM (hiện dùng dữ liệu mẫu rút gọn `db/seed/`)
- [ ] Giao diện M1–M3 (buổi 10 – 12)

## 7. Khai báo sử dụng công cụ AI
Xem `docs/ai-disclosure.md`.
