# Nhật ký lỗi đã gỡ (bug log) – Giai đoạn 2

Luồng L4 · Nguyễn Thái Đức – 2374802010117 · Track SE. Mỗi lỗi ghi theo quy trình gỡ 4 bước của buổi 11:
tái lập → khoanh vùng → sửa nguyên nhân → xác nhận.

## BUG-01 · Lỗi kiểm tra dữ liệu trả mã 422 và thông báo tiếng Anh (buổi 8)
- Hiện tượng   : Gọi E3 với `{"technician_id": 0}` nhận HTTP 422, thông báo "Input should be greater than 0".
- Tái lập      : `curl -X POST ... -d "{\"technician_id\":0}" localhost:3000/api/tickets/2/assignment`
- Khoanh vùng  : Lớp trình bày – FastAPI dùng bộ xử lý lỗi kiểm tra dữ liệu mặc định.
- Nguyên nhân  : Chưa đăng ký handler cho RequestValidationError nên lệch API contract (400 VALIDATION_FAILED).
- Cách sửa     : Thêm handler trong `src/backend/api/errors.py` trả 400 và thông báo tiếng Việt theo từng trường.
- Xác nhận     : Gọi lại → 400 `{"error":{"code":"VALIDATION_FAILED",...,"fields":{"technician_id":"Phải là số nguyên dương"}}}`.
- Commit       : [35708f2](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/35708f2)

## BUG-02 · Giờ lịch hẹn hiển thị lệch 7 tiếng và giờ kết thúc hiện "/2026" (buổi 10)
- Hiện tượng   : Lịch hẹn 09:00–09:30 hiện "02:00 24/10/2026 – /2026" trên M3.
- Tái lập      : Mở M3 trên trình duyệt đặt múi giờ UTC, lưu lịch hẹn 09:00–09:30.
- Khoanh vùng  : Lớp trình bày – hàm định dạng ngày giờ trong `components/layout.js`, backend trả đúng +07:00.
- Nguyên nhân  : `toLocaleString` dùng múi giờ của máy; lấy giờ kết thúc bằng `slice(-5)` sai vì định dạng vi-VN đặt giờ trước ngày.
- Cách sửa     : Định dạng luôn theo `timeZone: 'Asia/Ho_Chi_Minh'`; thêm hàm `fmtTime()` riêng cho giờ.
- Xác nhận     : Chạy lại luồng → "24/10/2026 09:00 – 09:30", gợi ý khung trống "09:30".
- Commit       : [ead96d5](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/ead96d5)

## BUG-03 · Tắt backend thì mất luôn giao diện, không kiểm được trạng thái lỗi (buổi 10)
- Hiện tượng   : Điều kiện "xong" của buổi 10 (tắt backend thấy thông báo lỗi có nút Thử lại) không thể kiểm.
- Tái lập      : Backend phục vụ giao diện ở /app; dừng uvicorn rồi tải lại trang → trình duyệt báo không kết nối được.
- Khoanh vùng  : Cách triển khai giao diện, không phải mã màn hình.
- Nguyên nhân  : Giao diện và API cùng một tiến trình nên tắt API là tắt cả giao diện.
- Cách sửa     : Giao diện chạy riêng (`python -m http.server 5500 -d src/frontend`), backend bật CORS cho cổng 5500 (TD-11).
- Xác nhận     : Tắt backend, bấm Lọc trên M1 → "Không kết nối được máy chủ…" kèm nút Thử lại.
- Commit       : [ead96d5](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/ead96d5)

## BUG-04 · Hai test tích hợp FAIL sau khi đổi mã trung tâm Tân Bình từ 4 sang 2 (buổi 10)
- Hiện tượng   : `test_tc07` và `test_ac2_1` FAIL – chỉ còn 2 kỹ thuật viên được gợi ý, thiếu "Lê Thị A".
- Tái lập      : `python -m pytest -v` sau khi sửa db/seed/001_du_lieu_mau.sql.
- Khoanh vùng  : Dữ liệu mẫu – dòng của Lê Thị A và Ngô Văn D vẫn mang center_id = 4.
- Nguyên nhân  : Lệnh thay thế giả định một dấu cách sau dấu phẩy; hai dòng này có nhiều dấu cách để canh cột nên bị bỏ sót.
- Cách sửa     : Sửa biểu thức thay thế chấp nhận nhiều dấu cách; kiểm lại toàn bộ cột center_id.
- Xác nhận     : `python -m pytest -v` → 21 passed.
- Commit       : [b8a6e91](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/b8a6e91)

## BUG-05 · Bộ nạp dataset tự tạo danh mục nhóm sự cố, lệch với dataset chính thức (buổi 10)
- Hiện tượng   : Kết quả nạp không có dòng "Đọc issue_categories.csv"; mức ưu tiên mặc định MAN_HINH là TRUNG_BINH thay vì CAO.
- Tái lập      : `python -m src.backend.seed_dataset --data data/official --reopen 5` với bộ dataset của học phần.
- Khoanh vùng  : `src/backend/seed_dataset.py` – phần nạp issue_category.
- Nguyên nhân  : Bộ nạp được viết trước khi có dataset, giả định danh mục theo Bảng 3.1 case study.
- Cách sửa     : Đọc tên cột và 3 dòng đầu từng file trước; bộ nạp đọc issue_categories.csv, giữ mã gốc, in tên trung tâm (TD-12).
- Xác nhận     : Nạp lại → "Nhóm sự cố: 1=MAN_HINH … 6=KHAC", 7.800 phiếu, 0 dòng bị loại.
- Commit       : [b8a6e91](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/b8a6e91)

## BUG-06 · Tắt cơ sở dữ liệu thì API trả "Internal Server Error" thô (buổi 12)
- Hiện tượng   : Dừng PostgreSQL rồi gọi E1 → HTTP 500, nội dung "Internal Server Error", không theo cấu trúc lỗi của API contract.
- Tái lập      : Dừng dịch vụ PostgreSQL (hoặc đặt DB_PORT sai), gọi `GET /api/tickets?status=MOI`.
- Khoanh vùng  : Lớp trình bày – không có handler cho lỗi kết nối psycopg.OperationalError.
- Nguyên nhân  : Lỗi kết nối lan thẳng lên ASGI server, trả lỗi thô (vi phạm C7 – suy giảm có kiểm soát).
- Cách sửa     : Handler trả 503 `DATABASE_UNAVAILABLE` "Không kết nối được cơ sở dữ liệu…", ghi log; handler chung trả 500 `INTERNAL_ERROR` không lộ chi tiết.
- Xác nhận     : `tests/test_api_crud.py::test_csdl_tat_tra_503_ro_rang_khong_treo` PASS; giao diện hiện lỗi kèm nút Thử lại.
- Commit       : commit "fix(api): bao loi 503 ro rang khi CSDL tat" (buổi 12)
