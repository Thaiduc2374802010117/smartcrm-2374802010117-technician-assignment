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
Yêu cầu trước: **Python 3.12**, **PostgreSQL 16**, Git; đã tạo database `smartcrm` (pgAdmin → Databases → Create).
Thư viện ghi phiên bản cố định (`==`) trong `requirements.txt`.

| Bước | Lệnh | Kết quả mong đợi |
|---|---|---|
| 1 | `git clone --branch v0.2 https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment.git thu-nghiem` | Có thư mục `thu-nghiem` (bản nộp BT2, tag v0.2) |
| 1b | `cd thu-nghiem` | Đang ở thư mục gốc repo |
| 2 | `py -m venv .venv` | Có thư mục `.venv` |
| 3 | `.venv\Scripts\activate` | Đầu dòng lệnh hiện `(.venv)` |
| 4 | `pip install -r requirements.txt` | Cài xong FastAPI, psycopg, pytest… |
| 5 | `copy .env.example .env` rồi mở `.env` điền `DB_USER`, `DB_PASSWORD` | Có file `.env` |
| 6 | `python -m src.backend.migrate` | `✓ migrations/001_tao_bang_theo_ddl_bt1.sql` – 6 bảng |
| 7 | `python -m src.backend.seed_dataset --data data/official --reopen 5` | Nạp dataset thật, in số dòng và số phiếu MOI mỗi trung tâm |
| 8 | `uvicorn src.backend.main:app --port 3000` (để cửa sổ này chạy) | `Uvicorn running on http://127.0.0.1:3000` |
| 9 | Mở **cửa sổ cmd thứ hai** tại thư mục repo: `python -m http.server 5500 -d src/frontend` | Mở http://localhost:5500 → trang đăng nhập |
| 10 | Cửa sổ thứ ba (đã activate `.venv`): `python -m pytest -v` | `58 passed` |
| 11 | (tùy chọn) Cửa sổ thứ ba: `powershell -ExecutionPolicy Bypass -File scripts\demo-crud.ps1` | Gọi CRUD đủ cho 2 thực thể, in mã HTTP từng bước |

- Bước 7 cần bộ **Mekong Mobile – Dataset Smart CRM** (E-learning) giải nén vào `data/official/`. Nếu chưa có: chạy
  `python -m src.backend.migrate --seed` để dùng dữ liệu mẫu rút gọn.
- **Chạy lại lần hai (C5):** bước 6 và bước 7 chạy lại bao nhiêu lần cũng được – migration dùng `IF NOT EXISTS`, bộ nạp xoá rồi nạp lại nên số dòng không nhân đôi (luôn 7.800 phiếu).
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
[![CI](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/actions/workflows/ci.yml/badge.svg)](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/actions)

- **Toàn bộ bộ kiểm thử – một lệnh:** `python -m pytest -q` → **58 passed** (unit 35 · integration 3 · API 18 · cấu hình 2).
- **Một test case của Test Report (in đủ tám cột):** `python -m scripts.run_tc TC-05` · cả 12: `python -m scripts.run_tc --all`.
- **Sinh Test Report từ lịch sử chạy thật:** `python -m scripts.run_tc --report` → `docs/test-report.md`.
- Tài liệu: `docs/test-plan.md` (Test Plan bốn mục) · `docs/test-report.md` (12 test case) · `docs/bug-log.md` (Bug Log bảy dòng).
- Test tích hợp và test case BT3 dùng database RIÊNG `smartcrm_test` (tự tạo, resetDb trước mỗi test) – không đụng dữ liệu `smartcrm`.
- CI: `.github/workflows/ci.yml` chạy `pytest -q` trên máy sạch của GitHub (dịch vụ PostgreSQL 16) mỗi lần push.

### Thử CRUD bằng curl (cmd, backend đang chạy)
```
curl -s -H "X-Employee-Id: 3" -H "X-Role: QUAN_LY" -H "X-Center-Id: 2" localhost:3000/api/technicians
curl -s -X POST -H "X-Employee-Id: 3" -H "X-Role: QUAN_LY" -H "X-Center-Id: 2" -H "Content-Type: application/json" -d "{\"full_name\":\"Tran Van Moi\",\"level\":\"SO_CAP\"}" localhost:3000/api/technicians
```
Danh sách đầy đủ 16 endpoint và mã lỗi: `docs/api-contract.md` · thử trực quan: http://localhost:3000/docs

## 6. Trạng thái hiện tại (buổi 12 – nộp BT2, tag `v0.2`)
- [x] Module Phân công: E1, E2, E3 qua 3 lớp; NFR3 đã kiểm chứng (TC07)
- [x] Module Lịch hẹn: E4, E5, E14 – E16 (tạo, xem, sửa giờ, hủy), chặn trùng ở lớp nghiệp vụ và bằng EXCLUDE (TC10)
- [x] Danh mục kỹ thuật viên: E9 – E13 – **CRUD đủ cho 2 thực thể** (TD-13)
- [x] Giao diện 3 màn hình M1 – M3 gọi API thật, đủ ba trạng thái; đăng nhập giả lập, xử lý 401
- [x] Dữ liệu thật Dataset Smart CRM (7.800 phiếu); chạy lại không nhân đôi
- [x] Suy giảm có kiểm soát: tắt backend → giao diện báo lỗi có nút Thử lại; tắt CSDL → API trả 503 rõ ràng (TD-14)
- [x] 35 test PASS; `docs/bug-log.md` 6 lỗi đã gỡ
- [ ] E6 đổi kỹ thuật viên, E7, E8 – hoãn (TD-09); Docker – chưa làm

## 7. Khai báo sử dụng công cụ AI
Xem `docs/ai-disclosure.md`.
