# Checklist bảo mật – Luồng L4 · Nguyễn Thái Đức – 2374802010117 · Track SE

Mỗi mục: trạng thái **ĐÃ LÀM / CHƯA LÀM / KHÔNG ÁP DỤNG** + minh chứng chạy thật. Ảnh: `docs/screenshots/sec-x.png`.
Điền bằng cách CHẠY THỬ – lần chạy này phát hiện **BUG-11** (mục 5), đã sửa và ghi Bug Log.

## 1. Không có secret nào trong repo (OWASP A02) — ĐÃ LÀM
- `git log --all --oneline -- .env` → **rỗng** (.env chưa từng vào lịch sử) · `git check-ignore -v .env` → `.gitignore:…:.env`.
- `git grep -niE "(password|secret|api_key)\s*=\s*['\"][^'\"]+['\"]" -- src` → **rỗng**: mật khẩu chỉ đọc từ biến môi trường (`os.getenv`).
- `.env.example` chỉ chứa giá trị MẪU; `.dockerignore` loại `.env` khỏi image; CI dùng mật khẩu thử riêng. Ảnh: `sec-1.png`.

## 2. Dữ liệu vào được kiểm ở tầng ứng dụng (A05) — ĐÃ LÀM
- Kiểu dữ liệu kiểm ở lớp trình bày (Pydantic), quy tắc nghiệp vụ ở lớp service; lỗi trả 400 nêu từng trường (TC-06, TC-07, TC-08).
- Chống injection: mọi giá trị người dùng đi qua tham số `%s` của psycopg. `tests/test_security.py` gửi `' OR '1'='1`, `1 OR 1=1`, `MOI'; DROP TABLE ticket;--` → **400**, không trả danh sách – PASS.
- Lệnh tìm SQL ghép chuỗi `git grep -nE "execute\(f\"" -- src` ra 3 dòng, đã rà từng dòng: `ticket_repository.py:23` ghép điều kiện WHERE từ **đoạn hằng trong mã** (giá trị vẫn là tham số `%s`); `migrate.py:28`, `seed_dataset.py:176` ghép **tên bảng từ danh sách hằng**. Không có biến người dùng nào trong chuỗi SQL. Ảnh: `sec-2.png`.

## 3. Kiểm soát truy cập theo chủ sở hữu (A01) — ĐÃ LÀM
- Mọi endpoint kiểm vai trò và trung tâm (QT-14). TC-10: quản lý trung tâm 1 phân công phiếu trung tâm 2 → **403**, phiếu không đổi – PASS. TC-11: header định danh giả mạo → **401** – PASS.
- Ảnh: `TC-10.png`, `TC-11.png`.

## 4. Mật khẩu, dữ liệu nhạy cảm được băm / mã hoá (A04 · A07) — KHÔNG ÁP DỤNG
- Lý do: prototype không có đăng nhập thật (W8 – ngoài phạm vi), **không lưu mật khẩu** người dùng; 6 bảng của L4 không có cột mật khẩu hay số điện thoại khách. Mật khẩu CSDL chỉ nằm trong `.env` (không commit).
- Kế hoạch khi làm đăng nhập thật: lưu `password_hash` bằng bcrypt, ký token bằng `JWT_SECRET` từ biến môi trường.

## 5. Thông báo lỗi không lộ cấu trúc bên trong (A10 · A02) — ĐÃ LÀM (sau khi sửa BUG-11)
- Chạy thử phát hiện `GET /db-check` trả **200** kèm `connection to server at "127.0.0.1", port 5432 … user "postgres"` → **BUG-11**, đã sửa: `/health` trả `503 {"status":"degraded","db":"down"}`, chi tiết chỉ ghi log.
- JSON hỏng → `400 {"body":"JSON không hợp lệ"}`, không có stack/tên bảng (`tests/test_security.py`); CSDL tắt → `503 DATABASE_UNAVAILABLE`; lỗi khác → `500 INTERNAL_ERROR` không chi tiết.
- Minh chứng: `docker compose stop db` → `curl http://localhost:3000/health` → `{"status":"degraded","db":"down"}` → `docker compose start db`. Ảnh: `sec-5.png`.

## 6. Nhật ký không ghi secret, dữ liệu cá nhân (A09) — ĐÃ LÀM
- Log chỉ có dòng truy cập (phương thức, đường dẫn, mã trạng thái) và loại lỗi; không log thân yêu cầu, header hay chuỗi kết nối. Dữ liệu L4 không có số điện thoại/email khách.
- `docker compose logs app | findstr /i "password secret token doi-mat-khau"` (Linux/macOS: `grep -iE`) → **rỗng**. Ảnh: `sec-6.png`.

## 7. Phụ thuộc ghim phiên bản, đã kiểm lỗ hổng (A03) — ĐÃ LÀM phần ghim phiên bản; kiểm lỗ hổng: xem kết quả
- `requirements.txt` ghim mọi thư viện bằng `==`, UTF-8 (BUG-07); `tests/test_requirements.py` chặn tái diễn; image Docker cố định `python:3.12-slim`, `postgres:16-alpine`, `nginx:1.27-alpine`.
- Kiểm lỗ hổng: `pip install pip-audit` → `pip-audit -r requirements.txt` → **KẾT QUẢ: (điền sau khi chạy)**. Ảnh: `sec-7.png`.
