# Smart CRM – Phân công kỹ thuật viên và lịch hẹn giao – nhận máy bảo hành

**Sinh viên:** Nguyễn Thái Đức – MSSV: 2374802010117 – Lớp: 261_71ITGR40203_05
**Track:** SE
**Học phần:** Chuyên đề Tốt nghiệp 1 – Trường ĐH Văn Lang
**Luồng nghiệp vụ:** L4 – Phân công kỹ thuật viên và lịch hẹn (case study Mekong Mobile)

## 1. Mô tả bài toán
Phiếu bảo hành [Mới] → Quản lý trung tâm xem gợi ý kỹ thuật viên phù hợp → phân công [Đã phân công]
→ đặt lịch hẹn giao – nhận máy (kiểm tra trùng lịch) → kỹ thuật viên xử lý → [Hoàn tất].

Người dùng: Quản lý trung tâm bảo hành, Kỹ thuật viên.

## 2. Phạm vi
- Làm (7 User Story): danh sách phiếu chờ phân công; gợi ý kỹ thuật viên theo tay nghề, trung tâm, khối lượng việc;
  phân công; đổi kỹ thuật viên kèm lý do; đặt lịch hẹn không trùng lịch; danh sách phiếu của kỹ thuật viên;
  bảng khối lượng công việc.
- Không làm: tiếp nhận phiếu (L2), kho linh kiện (L5), khảo sát (L8), cập nhật tiến độ sửa chữa, khách tự đặt lịch,
  SMS/Zalo, đăng nhập đầy đủ, màn hình lịch sử phiếu riêng, hủy lịch hẹn thủ công.

## 3. Công nghệ sử dụng
| Thành phần | Công nghệ |
|---|---|
| Backend | Python 3.12 + FastAPI (Uvicorn) |
| Frontend | HTML, CSS, JavaScript |
| Cơ sở dữ liệu | PostgreSQL 16 |
| Kiểm thử | pytest |
| Quản lý mã nguồn | Git, GitHub (main / dev / feature/*) |

## 4. Tài liệu thiết kế (Bài tập 1) và cách mở
| File | Nội dung | Cách mở |
|---|---|---|
| `BT1_2374802010117_NguyenThaiDuc.pdf` | Bản PDF đã nộp VLU E-learning | Trình duyệt / trình đọc PDF |
| `docs/srs.md` | Mục 1 – SRS rút gọn 6 mục, đặc tả UC2, UC4 | Xem trực tiếp trên GitHub |
| `docs/usecase.drawio` | Mục 2 – Use Case Diagram (file gốc) | app.diagrams.net → Tệp → Mở từ → Thiết bị |
| `docs/architecture.drawio` | Mục 3 – Sơ đồ kiến trúc 4 lớp (file gốc) | app.diagrams.net → Tệp → Mở từ → Thiết bị |
| `docs/schema.dbml`, `docs/schema.sql` | Mục 4 – ERD (dbdiagram.io) và SQL DDL | dbdiagram.io (dán nội dung) / psql |
| `docs/wireframe.png` | Mục 5 – Wireframe 3 màn hình | Xem trực tiếp |
| `docs/thiet-ke.md` | Lập luận kiến trúc, 5 lỗi ERD, 3NF, đối chiếu wireframe, rà soát nhất quán | Xem trực tiếp trên GitHub |
| `docs/api-contract.md` | Hợp đồng API (mẫu track SE) | Xem trực tiếp trên GitHub |
| `docs/ai-disclosure.md` | Bảng khai báo sử dụng công cụ AI | Xem trực tiếp trên GitHub |
| `docs/diagrams/*.png` | Ảnh xuất từ các sơ đồ để chèn PDF | Xem trực tiếp |

## 5. Hướng dẫn cài đặt & chạy
1. `python -m venv .venv` rồi `.venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. `copy .env.example .env` và điền `DB_USER`, `DB_PASSWORD`
4. `uvicorn src.backend.main:app --reload --port 3000` → mở http://localhost:3000

## 6. Khai báo sử dụng công cụ AI
Xem chi tiết tại [`docs/ai-disclosure.md`](docs/ai-disclosure.md).
