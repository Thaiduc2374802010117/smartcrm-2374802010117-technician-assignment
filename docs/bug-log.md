# Bug Log – Luồng L4 · Nguyễn Thái Đức – 2374802010117 · Track SE

Mẫu bảy dòng (buổi 13). Mức độ phân loại bằng hai câu hỏi, hỏi đúng thứ tự:
**(1)** Hệ thống không dùng được, dữ liệu bị sai hay bị lộ? → **CRITICAL**.
**(2)** Một chức năng quan trọng sai / không dùng được nhưng có cách làm khác? → **MAJOR**. Còn lại → **MINOR**.
Mỗi bug của BT3 sửa trong **một commit riêng** `fix(...): ... (BUG-xx)`; link commit điền bằng `python -m scripts.fill_bug_links`.

## Bài tập 3 – phát hiện khi kiểm thử hệ thống (buổi 14) và chạy thử checklist bảo mật (buổi 15)

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

### BUG-11 — Kiểm tra sức khoẻ lộ host, cổng, tên user CSDL và trả 200 khi hệ thống hỏng
1. Mã và mức độ : BUG-11 · **MAJOR** — câu (1): không lộ mật khẩu hay dữ liệu khách, hệ thống vẫn chạy; câu (2): có – chức năng kiểm tra sức khoẻ (dùng cho healthcheck triển khai) báo sai "200" khi CSDL hỏng nên không phát hiện được sự cố, đồng thời lộ thông tin cấu hình (OWASP A02/A10); cách làm tạm: gọi một API nghiệp vụ để biết CSDL lỗi.
2. Phát hiện bởi : Chạy thử checklist bảo mật mục 5 (buổi 15) – gọi `/db-check` khi CSDL sai mật khẩu.
3. Triệu chứng   : `GET /db-check` trả **200** `{"status":"ERROR","message":"connection failed: connection to server at \"127.0.0.1\", port 5432 failed: … for user \"postgres\""}`.
4. Cách tái lập : Đặt `DB_PASSWORD` sai (hoặc dừng PostgreSQL) rồi gọi `GET /db-check` – lặp lại 3/3 lần.
5. Nguyên nhân   : Endpoint smoke test từ buổi 2 trả nguyên `str(e)` của psycopg cho người gọi và luôn trả 200.
6. Cách sửa      : Thay bằng `GET /health`: 200 `{"status":"ok","db":"up"}` hoặc **503** `{"status":"degraded","db":"down"}`, chi tiết lỗi chỉ ghi log (chỉ tên loại lỗi); `/db-check` giữ làm bí danh của `/health`; thêm `tests/test_bug11_health_khong_lo_cau_hinh.py`.
7. Commit và xác nhận : [6d1bf29](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/6d1bf29163931a44094938f44764ea4366faddc1) · gọi lại khi CSDL hỏng → 503, không có "127.0.0.1", "5432", "user"; toàn bộ bộ test PASS.

### BUG-12 — Thư viện certifi có lỗ hổng đã công bố (PYSEC-2026-4320)
1. Mã và mức độ : BUG-12 · **MINOR** — câu (1): không, chưa có dữ liệu bị sai hay bị lộ; câu (2): không – certifi chỉ dùng cho kết nối HTTPS ra ngoài (qua httpx), ứng dụng khi chạy thật không gọi HTTPS ra ngoài, httpx chỉ dùng trong test; vẫn sửa ngay vì đã có bản vá (OWASP A03 – chuỗi cung ứng).
2. Phát hiện bởi : Chạy thử checklist bảo mật mục 7 (buổi 15) – `pip-audit -r requirements.txt`.
3. Triệu chứng   : `Found 2 known vulnerabilities in 1 package` – `certifi 2026.7.22 PYSEC-2026-4320`, bản vá `2026.10.18` (hai dòng cùng một mã lỗ hổng).
4. Cách tái lập : `pip install pip-audit` → `pip-audit -r requirements.txt` trên requirements.txt cũ – lặp lại 2/2 lần.
5. Nguyên nhân   : Tệp khoá ghim certifi ở phiên bản trước khi lỗ hổng được vá; ghim phiên bản giữ cố định cả lỗ hổng nếu không kiểm định kỳ.
6. Cách sửa      : Nâng `certifi==2026.10.18` trong requirements.txt (đổi đúng một dòng, giữ UTF-8 – `tests/test_requirements.py` vẫn PASS).
7. Commit và xác nhận : [87846fb](https://github.com/Thaiduc2374802010117/smartcrm-2374802010117-technician-assignment/commit/87846fb814b02577368abce99b1506ed2179e390) · `pip-audit -r requirements.txt` → `No known vulnerabilities found`; 61/61 test PASS.

---
Lỗi đã gỡ ở giai đoạn 2 (Bài tập 2, BUG-01 … BUG-06) được ghi riêng trong `docs/bug-log-bt2.md` để truy vết – không thuộc Bug Log của Bài tập 3.
