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

## 3. Các bước dựng và chạy hệ thống (mỗi bước một lệnh, chạy trong **cmd** tại thư mục gốc repo)
Yêu cầu trước: đã cài Python 3.12, PostgreSQL 16 và đã tạo database `smartcrm` (pgAdmin → Databases → Create).

| Bước | Lệnh | Kết quả mong đợi |
|---|---|---|
| 1 | `git clone https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment.git` | Có thư mục repo |
| 1b | `cd smartcrm-2374802010117-technician-assignment` | Đang ở thư mục gốc repo |
| 2 | `py -m venv .venv` | Có thư mục `.venv` |
| 3 | `.venv\Scripts\activate` | Đầu dòng lệnh hiện `(.venv)` |
| 4 | `pip install -r requirements.txt` | Cài xong FastAPI, psycopg, pytest… |
| 5 | `copy .env.example .env` rồi mở `.env` điền `DB_USER`, `DB_PASSWORD` | Có file `.env` |
| 6 | `python -m src.backend.migrate` | `✓ migrations/001_tao_bang_theo_ddl_bt1.sql` – 6 bảng |
| 7 | `python -m src.backend.seed_dataset --data data/official --reopen 5` | Nạp dataset thật, in số dòng và số phiếu MOI mỗi trung tâm |
| 8 | `uvicorn src.backend.main:app --port 3000` (để cửa sổ này chạy) | `Uvicorn running on http://127.0.0.1:3000` |
| 9 | Mở **cửa sổ cmd thứ hai** tại thư mục repo: `python -m http.server 5500 -d src/frontend` | Mở http://localhost:5500 → trang đăng nhập |
| 10 | Cửa sổ thứ ba (đã activate `.venv`): `python -m pytest -v` | `21 passed` |

- Bước 7 cần bộ **Mekong Mobile – Dataset Smart CRM** (E-learning) giải nén vào `data/official/`. Nếu chưa có: chạy
  `python -m src.backend.migrate --seed` để dùng dữ liệu mẫu rút gọn.
- Đăng nhập: nhập mã nhân viên bất kỳ và **mã trung tâm** in ra ở bước 7 (dataset thật: 2 = TTBH Quận Tân Bình; dữ liệu rút gọn cũng dùng mã 2).
- Luồng chính: Đăng nhập → **M1** Phiếu chờ phân công → Phân công → **M2** chọn kỹ thuật viên gợi ý → Phân công →
  Đặt lịch hẹn → **M3** lưu lịch hẹn. Tài liệu API: http://localhost:3000/docs

## 4. Cấu trúc thư mục – ánh xạ một–một với sơ đồ kiến trúc (docs/architecture.drawio)
| Thư mục / file | Lớp kiến trúc | Nội dung |
|---|---|---|
| `src/frontend/` | ① Trình bày (View) | `index.html` đăng nhập · `pages/` M1 `tickets`, M2 `assign`, M3 `appointment` · `api/client.js` (nơi DUY NHẤT gọi `fetch`), `tickets.api.js`, `appointments.api.js` · `components/data-state.js` (đang tải · rỗng · lỗi) |
| `src/backend/api/` | ① Trình bày (Controller) | E1, E2, E3 (`tickets.py`), E4, E5 (`appointments.py`), kiểm tra quyền (`auth.py`), mã lỗi (`errors.py`) |
| `src/backend/services/` | ② Nghiệp vụ | `assignment_service.py` (QT-06, QT-07, QT-08, QT-L4-01), `appointment_service.py` (QT-L4-02 … 04), `ticket_query_service.py` |
| `src/backend/repositories/` | ③ Truy cập dữ liệu | SQL tham số hóa, `unit_of_work.py` quản lý giao dịch (NFR3) |
| `src/backend/db.py`, `db/` | ④ Lưu trữ | Kết nối PostgreSQL; `db/migrations/` (DDL BT1), `db/seed/` (dữ liệu rút gọn), `seed_dataset.py` (dataset thật) |
| `tests/` | — | Unit test lớp nghiệp vụ + test tích hợp trên database riêng `smartcrm_test` |
| `docs/` | — | SRS, sơ đồ `.drawio`, ERD, wireframe, API contract, nhật ký thay đổi thiết kế, ảnh chụp kết quả |

## 5. Kiểm thử
`python -m pytest -v` → **21 test PASS** (in số test trên màn hình):
- `test_assignment_service.py` – 6 test: phân công đúng, tay nghề < 3, khác trung tâm, phiếu đã phân công, QT-14, NFR3.
- `test_appointment_service.py` – 12 test: luồng đúng · **biên** 15/14 phút, 120/121 phút, 08:00, 18:00, lịch sát nhau ·
  **dữ liệu sai** Chủ nhật, quá khứ, phiếu chưa có kỹ thuật viên, **trùng 09:15–09:45 với 09:00–09:30**.
- `test_integration_db.py` – 3 test trên PostgreSQL thật (database `smartcrm_test`, tự tạo): **TC07** 2 yêu cầu phân công
  cùng lúc → đúng 1 thành công, 1 dòng lịch sử · **TC10** ràng buộc EXCLUDE · AC2.1 thứ tự gợi ý. Tự bỏ qua nếu không có PostgreSQL.

## 6. Trạng thái hiện tại (buổi 10)
- [x] Module Phân công: E1, E2, E3 qua 3 lớp; NFR3 đã kiểm chứng (TC07)
- [x] Module Lịch hẹn: E4, E5, chặn trùng lịch ở lớp nghiệp vụ và bằng EXCLUDE ở CSDL (TC10)
- [x] Giao diện 3 màn hình M1 – M3 theo wireframe BT1, gọi API thật; DataState cho cả 3 màn hình
- [x] Đăng nhập giả lập; nhận 401 thì xoá người dùng, về trang đăng nhập; tắt backend thấy lỗi có nút Thử lại
- [x] Luồng chính end-to-end: đăng nhập → M1 → M2 phân công → M3 đặt lịch hẹn
- [x] Bộ nạp Dataset Smart CRM (`seed_dataset.py`), 21 test PASS
- [ ] E6 đổi kỹ thuật viên, E7 phiếu của kỹ thuật viên, E8 khối lượng công việc – đã hoãn, xem TD-09
- [ ] Đóng gói Docker (buổi 11), PDF báo cáo BT2 và tag v0.2 (buổi 12)

## 7. Khai báo sử dụng công cụ AI
Xem `docs/ai-disclosure.md`.
