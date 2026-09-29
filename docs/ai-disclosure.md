# Phụ lục – Bảng khai báo sử dụng công cụ AI

| Công cụ | Dùng vào việc gì | Áp dụng ở phần nào | Đã kiểm chứng thế nào |
|---|---|---|---|
| Claude (Anthropic) | Gợi ý bản nháp phiếu phạm vi, README khung, hướng dẫn cấu hình Git và cài môi trường; gợi ý mã smoke test FastAPI | Buổi 2: phiếu phạm vi, repo, `src/backend/main.py` | Tự cấu hình Git, tạo repo, cài Python/PostgreSQL; tự chạy `/` và `/db-check` trên máy, tự sửa lỗi mật khẩu và thiếu database |
| Claude (Anthropic) | Gợi ý bản nháp SRS, User Story, tiêu chí chấp nhận, đặc tả UC3/UC5, API contract | Mục 1 SRS, Mục 2 Use Case, `api-contract.md` | Đối chiếu từng yêu cầu với case study (Bảng 2.2, 3.1, 9.1, Hình 6.2); đối chiếu thứ tự US1–US7 với phiếu phạm vi đã nộp; rút từ 9 xuống 7 User Story theo đề BT1 |
| Claude (Anthropic) | Gợi ý bố cục sơ đồ Use Case, sơ đồ kiến trúc, ERD, SQL DDL và wireframe | Mục 2, 3, 4, 5 | Kiểm tra lập luận kiến trúc có mã NFR và đánh đổi; kiểm tra ERD đủ khóa chính, khóa ngoại; kiểm tra mọi trường trên wireframe có trong ERD; Ctrl+F từng thuật ngữ trong bảng thuật ngữ |

**Phần em tự làm:**

- Tự chọn luồng L4 ở buổi 1 và đối chiếu mô tả luồng L4 trong case study (Mục 7) với phiếu phạm vi; tự chọn Track SE và công nghệ Python 3.12 + FastAPI, HTML/CSS/JavaScript, PostgreSQL 16.
- Tự gắn email trường vào tài khoản GitHub, cấu hình Git, tạo repo `smartcrm-2374802010117-technician-assignment`, tự phát hiện và sửa lỗi tên repo thừa dấu "-" gây lỗi *Repository not found*.
- Tự dựng cấu trúc thư mục Track SE, `.gitignore`, `.env.example`; tự commit theo Conventional Commits, tạo nhánh `main`/`dev` và merge `dev` vào `main` sau mỗi lần cập nhật.
- Tự cài Python 3.12.9, PostgreSQL 16 và pgAdmin; tự xử lý lỗi Windows chặn lệnh `python` (dùng `py`) và lỗi chặn chạy script khi kích hoạt môi trường ảo.
- Tự tạo database `smartcrm`, tạo file `.env`, chạy backend và kiểm tra `/` trả về "Hello Smart CRM", `/db-check` trả về `status: OK`; tự sửa lỗi sai mật khẩu và lỗi chưa tạo database dựa trên thông báo lỗi.
- Tự đưa các tài liệu SRS, sơ đồ, ERD, wireframe vào `docs/`, thay bản cũ bằng bản đúng đề BT1 và đẩy lên GitHub.

Tôi xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp.

Họ tên: Nguyễn Thái Đức · MSSV: 2374802010117 · Ngày: 29/09/2026
