# Bug Log – Luồng L4 · Nguyễn Thái Đức – 2374802010117 · Track SE

Mẫu bảy dòng (buổi 13). Mức độ phân loại bằng hai câu hỏi, hỏi đúng thứ tự:
**(1)** Hệ thống không dùng được, dữ liệu bị sai hay bị lộ? → **CRITICAL**.
**(2)** Một chức năng quan trọng sai / không dùng được nhưng có cách làm khác? → **MAJOR**. Còn lại → **MINOR**.
Mỗi bug của BT3 sửa trong **một commit riêng** `fix(...): ... (BUG-xx)`; link commit điền bằng `python -m scripts.fill_bug_links`.

## Bài tập 3 – phát hiện khi kiểm thử hệ thống (buổi 14)

### BUG-07 — requirements.txt không đọc được như tệp khoá UTF-8
1. Mã và mức độ : BUG-07 · **MAJOR** — câu (1): không, hệ thống vẫn chạy, dữ liệu không sai; câu (2): có – chức năng "dựng lại hệ thống trên máy khác" không bảo đảm cài đúng phiên bản; cách làm tạm: pip trên Windows vẫn tự nhận ra UTF-16.
2. Phát hiện bởi : Giảng viên – nhận xét Bài tập 2, mục kiểm chứng C6.
3. Triệu chứng   : C6 không đạt: "requirements.txt chưa khoá toàn bộ phiên bản bằng ==", dù trên máy em `pip install -r` vẫn chạy.
4. Cách tái lập : Đọc requirements.txt bằng công cụ đọc UTF-8 (hoặc chạy `tests/test_requirements.py` trên bản cũ) → ký tự lạ, không thấy dòng `==`; `git merge` hiển thị tệp là "Bin" (nhị phân) – lặp lại 3/3 lần.
5. Nguyên nhân   : Buổi 2 tạo tệp bằng `pip freeze > requirements.txt` trong Windows PowerShell 5 – PowerShell ghi tệp chuyển hướng bằng UTF-16 LE có BOM.
6. Cách sửa      : Tạo lại tệp bằng cmd (UTF-8); thêm `tests/test_requirements.py` kiểm mọi dòng có `==` và tệp không phải UTF-16.
7. Commit và xác nhận : [637733a](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/637733ac91d355b52b53676701f5571a2f57ebd3) · `findstr /v "==" requirements.txt` không in dòng nào; tệp còn 450 byte dạng văn bản; 37/37 test PASS; gắn tag v0.2.1.

### BUG-08 — Sửa giờ lịch hẹn kèm ghi chú dài trả lỗi 500
1. Mã và mức độ : BUG-08 · **MAJOR** — câu (1): không, giao dịch rollback nên dữ liệu không sai; câu (2): có – chức năng sửa giờ lịch hẹn (US5) thất bại với thông báo "Máy chủ gặp lỗi" khó hiểu; cách làm tạm: rút ngắn ghi chú.
2. Phát hiện bởi : TC-08 (Test Report) – lần chạy đầu FAIL.
3. Triệu chứng   : `PUT /api/appointments/{id}` với ghi chú 300 ký tự trả **500 INTERNAL_ERROR** thay vì 400 VALIDATION_FAILED nêu trường `note`.
4. Cách tái lập : resetDb → phân công phiếu 1 cho KTV 2 → tạo lịch 09:00–09:30 → PUT sửa sang 14:00–14:30 với `note` = "x" × 300; `python -m scripts.run_tc TC-08` – lỗi xuất hiện 3/3 lần.
5. Nguyên nhân   : `AppointmentService.reschedule()` không kiểm độ dài ghi chú (hàm `create()` có kiểm) → câu UPDATE gặp `StringDataRightTruncation` của cột `VARCHAR(255)`, lỗi lan lên handler chung 500.
6. Cách sửa      : `reschedule()` kiểm `note` ≤ 255 ký tự cùng lúc với khung giờ, trả lỗi nghiệp vụ `ValidationFailed` (→ 400); thêm `tests/test_bug08_ghi_chu_dai.py` (300 ký tự bị từ chối, đúng 255 ký tự hợp lệ).
7. Commit và xác nhận : [5d5a0df](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/5d5a0dfe0b5307812959df6bba4c5ac60ae7ceb6) · chạy lại TC-08 → PASS (400, fields.note, lịch giữ nguyên 09:00); toàn bộ bộ test PASS.

### BUG-09 — Header định danh ngoài phạm vi làm API trả lỗi 500
1. Mã và mức độ : BUG-09 · **MINOR** — câu (1): không, dữ liệu không sai, không lộ (giao dịch rollback, thông báo không lộ chi tiết); câu (2): không – người dùng bình thường không gặp vì giao diện luôn gửi mã hợp lệ; chỉ sai mã lỗi trả về (500 thay vì 401).
2. Phát hiện bởi : TC-11 (Test Report) – lần chạy đầu FAIL.
3. Triệu chứng   : `POST /api/tickets/1/assignment` với `X-Employee-Id: 99999999999999999999` trả **500 INTERNAL_ERROR**; `X-Center-Id: 99999999999` khi tạo kỹ thuật viên cũng 500.
4. Cách tái lập : resetDb → gửi E3 hoặc E10 với header trên; `python -m scripts.run_tc TC-11` – lỗi xuất hiện 3/3 lần.
5. Nguyên nhân   : `api/auth.py` chỉ kiểm header "là số nguyên", không kiểm phạm vi; giá trị vượt BIGINT/INT đi tới CSDL gây `NumericValueOutOfRange`.
6. Cách sửa      : `current_user()` từ chối mã nhân viên ngoài 1…2⁶³−1 và mã trung tâm ngoài 1…2³¹−1 bằng 401 UNAUTHENTICATED ngay ở lớp trình bày; thêm `tests/test_bug09_header_ngoai_pham_vi.py` (4 giá trị sai + biên trên hợp lệ).
7. Commit và xác nhận : [d8a30e9](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/d8a30e95b3913a9e16ec6093691bd20260c06887) · chạy lại TC-11 → PASS (401, phiếu vẫn MOI); toàn bộ bộ test PASS.

### BUG-10 — Xem lịch hẹn với khoảng thời gian trộn có / không múi giờ trả lỗi 500
1. Mã và mức độ : BUG-10 · **MINOR** — câu (1): không; câu (2): không – giao diện M3 luôn gửi thời gian có múi giờ nên luồng chính không bị ảnh hưởng; chỉ người gọi API trực tiếp nhận 500 thay vì kết quả.
2. Phát hiện bởi : Kiểm thử thăm dò khi chuẩn bị TC-03 (gọi E4 bằng tay với tham số `to` không ghi múi giờ).
3. Triệu chứng   : `GET /api/technicians/2/appointments?from=2026-11-07T08:00:00+07:00&to=2026-11-08T08:00:00` trả **500 INTERNAL_ERROR**.
4. Cách tái lập : Gọi E4 như trên – lỗi xuất hiện 3/3 lần; log backend: `TypeError: can't compare offset-naive and offset-aware datetimes`.
5. Nguyên nhân   : Controller E4 chuyển thẳng hai giá trị thời gian (một có, một không có múi giờ) cho service; phép so sánh `end <= start` giữa hai kiểu thời gian khác nhau ném TypeError.
6. Cách sửa      : Controller chuẩn hoá thời gian không ghi múi giờ thành giờ Việt Nam (+07:00) trước khi gọi service – cùng quy ước với E5/E15; thêm `tests/test_bug10_mui_gio.py`.
7. Commit và xác nhận : [3a664e7](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/3a664e7750834f0e157e925d7f496118580fb48b) · gọi lại E4 → 200; toàn bộ bộ test PASS.

## Bài tập 2 – lỗi đã gỡ ở giai đoạn 2 (sửa cùng commit tính năng, ghi lại để truy vết)

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
