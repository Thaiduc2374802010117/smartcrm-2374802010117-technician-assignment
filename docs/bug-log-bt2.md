# Bug Log giai đoạn 2 (Bài tập 2) – lưu để truy vết

Các lỗi này được sửa CÙNG commit tính năng ở BT2 (trước khi có quy ước một bug một commit của BT3), nên KHÔNG tính vào Bug Log BT3. Bug Log BT3: `docs/bug-log.md` (BUG-07 … BUG-12, mỗi bug một commit riêng).


### BUG-01 — Lỗi kiểm tra dữ liệu trả 422 và thông báo tiếng Anh
1. Mã và mức độ : BUG-01 · MINOR — nghiệp vụ đúng, chỉ sai mã lỗi và thông báo khó hiểu.
2. Phát hiện bởi : Kiểm thử thủ công E3 bằng curl (buổi 8).
3. Triệu chứng   : `{"technician_id": 0}` → 422 "Input should be greater than 0".
4. Cách tái lập : `curl -X POST ... -d "{\"technician_id\":0}" localhost:3000/api/tickets/2/assignment`.
5. Nguyên nhân   : Chưa đăng ký handler RequestValidationError nên lệch API contract.
6. Cách sửa      : Handler trong `api/errors.py` trả 400 VALIDATION_FAILED, thông báo tiếng Việt từng trường.
7. Commit và xác nhận : [35708f2](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/35708f2) · gọi lại → 400 `fields.technician_id = "Phải là số nguyên dương"`.

### BUG-02 — Giờ lịch hẹn hiển thị lệch 7 tiếng
1. Mã và mức độ : BUG-02 · MAJOR — quản lý báo sai giờ hẹn cho khách; cách làm tạm: xem giờ trong API.
2. Phát hiện bởi : Kiểm thử end-to-end trên trình duyệt (buổi 10).
3. Triệu chứng   : Lịch 09:00–09:30 hiện "02:00 – /2026" trên M3.
4. Cách tái lập : Mở M3 trên máy đặt múi giờ UTC, lưu lịch 09:00–09:30.
5. Nguyên nhân   : `toLocaleString` dùng múi giờ của máy; cắt giờ kết thúc bằng `slice(-5)` sai định dạng vi-VN.
6. Cách sửa      : Định dạng theo `timeZone: 'Asia/Ho_Chi_Minh'`, thêm `fmtTime()`.
7. Commit và xác nhận : [ead96d5](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/ead96d5) · hiện "24/10/2026 09:00 – 09:30".

### BUG-03 — Tắt backend thì mất luôn giao diện
1. Mã và mức độ : BUG-03 · MAJOR — không hiển thị được trạng thái lỗi cho người dùng; cách làm tạm: tải lại trang khi backend bật.
2. Phát hiện bởi : Kiểm tra điều kiện "xong" của buổi 10.
3. Triệu chứng   : Dừng backend → trình duyệt "không kết nối được", không có nút Thử lại.
4. Cách tái lập : Backend phục vụ giao diện ở /app; dừng uvicorn rồi tải lại trang.
5. Nguyên nhân   : Giao diện và API chung một tiến trình.
6. Cách sửa      : Giao diện chạy riêng cổng 5500, backend bật CORS (TD-11).
7. Commit và xác nhận : [ead96d5](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/ead96d5) · tắt backend → "Không kết nối được máy chủ…" + nút Thử lại.

### BUG-04 — Hai test tích hợp FAIL sau khi đổi mã trung tâm Tân Bình
1. Mã và mức độ : BUG-04 · MAJOR — gợi ý kỹ thuật viên thiếu người trên dữ liệu mẫu; cách làm tạm: sửa tay dữ liệu.
2. Phát hiện bởi : `test_tc07`, `test_ac2_1` (pytest, buổi 10).
3. Triệu chứng   : Chỉ còn 2 KTV được gợi ý, thiếu "Lê Thị A".
4. Cách tái lập : `python -m pytest -v` sau khi sửa db/seed/001_du_lieu_mau.sql.
5. Nguyên nhân   : Lệnh thay thế giả định một dấu cách; hai dòng canh cột nhiều dấu cách bị bỏ sót, vẫn center_id = 4.
6. Cách sửa      : Biểu thức thay thế chấp nhận nhiều dấu cách; kiểm lại toàn bộ cột center_id.
7. Commit và xác nhận : [b8a6e91](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/b8a6e91) · 21/21 test PASS.

### BUG-05 — Bộ nạp dataset tự tạo danh mục lệch với dataset chính thức
1. Mã và mức độ : BUG-05 · CRITICAL — dữ liệu bị sai (mức ưu tiên mặc định của nhóm sự cố khác dataset) mà không báo lỗi.
2. Phát hiện bởi : Đối chiếu tên cột và 3 dòng đầu từng tệp dataset trước khi nạp (buổi 10).
3. Triệu chứng   : Không có dòng "Đọc issue_categories.csv"; MAN_HINH mặc định TRUNG_BINH thay vì CAO.
4. Cách tái lập : `python -m src.backend.seed_dataset --data data/official --reopen 5` bằng bộ nạp cũ.
5. Nguyên nhân   : Bộ nạp viết trước khi có dataset, giả định danh mục theo Bảng 3.1.
6. Cách sửa      : Đọc issue_categories.csv, giữ mã gốc, in tên trung tâm (TD-12).
7. Commit và xác nhận : [b8a6e91](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/b8a6e91) · "Nhóm sự cố: 1=MAN_HINH … 6=KHAC", 7.800 phiếu, 0 dòng bị loại.

### BUG-06 — Tắt cơ sở dữ liệu thì API trả lỗi thô
1. Mã và mức độ : BUG-06 · MAJOR — khi CSDL tắt người dùng nhận lỗi thô, không biết nguyên nhân; nghiệp vụ không thể dùng trong lúc CSDL tắt.
2. Phát hiện bởi : Kiểm tra mục C7 của BT2 (buổi 12).
3. Triệu chứng   : Dừng PostgreSQL rồi gọi E1 → 500 "Internal Server Error" không theo cấu trúc lỗi.
4. Cách tái lập : Dừng PostgreSQL hoặc đặt DB_PORT sai, gọi `GET /api/tickets?status=MOI`.
5. Nguyên nhân   : Không có handler cho psycopg.OperationalError.
6. Cách sửa      : Handler trả 503 DATABASE_UNAVAILABLE, ghi log; handler chung trả 500 INTERNAL_ERROR không lộ chi tiết.
7. Commit và xác nhận : [baa8ff2](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/baa8ff2) · `test_csdl_tat_tra_503_ro_rang_khong_treo` PASS.
