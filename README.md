# Smart CRM – Phân công kỹ thuật viên và lịch hẹn giao – nhận máy bảo hành

**Sinh viên:** Nguyễn Thái Đức – MSSV: 2374802010117
**Track:** SE
**Học phần:** Chuyên đề Tốt nghiệp 1 – Trường ĐH Văn Lang

## 1. Mô tả bài toán
Luồng L4 – Phân công kỹ thuật viên và lịch hẹn (case study Mekong Mobile).

Phiếu bảo hành [Mới] -> Quản lý trung tâm xem gợi ý kỹ thuật viên phù hợp -> phân công [Đã phân công]
-> đặt lịch hẹn giao – nhận máy (kiểm tra trùng lịch) -> kỹ thuật viên xử lý [Đang xử lý] -> [Hoàn tất].

Người dùng: Quản lý trung tâm bảo hành, Kỹ thuật viên.

## 2. Phạm vi
- Làm:
  - Danh sách phiếu chờ phân công, sắp theo hạn cam kết
  - Gợi ý kỹ thuật viên theo tay nghề (≥ 3), cùng trung tâm, ít việc nhất
  - Phân công / đổi kỹ thuật viên kèm lý do, ghi lịch sử trạng thái
  - Đặt lịch hẹn giao – nhận máy, chặn trùng lịch kỹ thuật viên
  - Danh sách việc của kỹ thuật viên, cảnh báo phiếu sắp quá hạn
  - Bảng khối lượng công việc theo kỹ thuật viên
- Không làm:
  - Tiếp nhận phiếu, sinh hạn cam kết (thuộc L2)
  - Kho linh kiện (thuộc L5), khảo sát hài lòng (thuộc L8)
  - Khách tự đặt lịch online, gửi SMS/Zalo
  - Đăng nhập – phân quyền đầy đủ (chỉ giả lập vai trò)

## 3. Công nghệ sử dụng
| Thành phần | Công nghệ |
|---|---|
| Backend | Python 3.12 + FastAPI (Uvicorn) |
| Frontend | HTML, CSS, JavaScript |
| Cơ sở dữ liệu | PostgreSQL 16 |
| Kiểm thử | pytest |
| Quản lý mã nguồn | Git, GitHub (main / dev / feature/*) |

## 4. Cấu trúc thư mục
- `docs/`: SRS, sơ đồ, khai báo AI (`docs/diagrams/`: Use Case, ERD)
- `src/backend/`: mã nguồn API FastAPI
- `src/frontend/`: giao diện HTML/CSS/JS
- `tests/`: kiểm thử
- `.env.example`: tên biến môi trường (không chứa giá trị thật)

## 5. Hướng dẫn cài đặt & chạy
1. `python -m venv .venv` rồi `.venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. `copy .env.example .env` và điền `DB_USER`, `DB_PASSWORD`
4. `uvicorn src.backend.main:app --reload --port 3000` → mở http://localhost:3000

## 6. Khai báo sử dụng công cụ AI
| Công cụ | Dùng vào việc gì | Cách tự kiểm chứng |
|---|---|---|
| Claude | Gợi ý phiếu phạm vi, README khung, hướng dẫn cấu hình Git và môi trường | Đối chiếu với case study và đề bài; tự chạy lệnh và kiểm tra kết quả trên máy và GitHub |
