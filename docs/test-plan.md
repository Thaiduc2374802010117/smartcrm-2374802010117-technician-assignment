# Test Plan – Luồng L4: Phân công kỹ thuật viên và lịch hẹn (track SE)

Nguyễn Thái Đức – 2374802010117 · Repo tag v1.0 · Test Report: `docs/test-report.md` · Bug Log: `docs/bug-log.md`

## 1. Phạm vi – kiểm gì và CHỦ Ý không kiểm gì
**Kiểm:**
- Gợi ý kỹ thuật viên theo QT-08 (cùng trung tâm, tay nghề ≥ 3, sắp theo số phiếu đang mở rồi tay nghề) – E2.
- Phân công phiếu MOI, ghi lịch sử phiếu, chống phân công trùng khi gửi đồng thời (QT-06, QT-07, QT-L4-01, NFR3) – E3.
- Lịch hẹn: khung giờ hợp lệ 15–120 phút, 08:00–18:00, thứ Hai – thứ Bảy (QT-L4-03); chống trùng lịch (QT-L4-02); sửa giờ, hủy (QT-L4-06) – E5, E14–E16.
- CRUD kỹ thuật viên, xoá mềm (QT-13) – E9–E13.
- Phân quyền theo trung tâm (QT-14, OWASP A01) và kiểm tra header định danh; mã lỗi theo API contract (400/401/403/404/409/422, 503 khi CSDL tắt).
- Tính tái lập: migration + dữ liệu mẫu chạy lại không lỗi, không nhân đôi (C8).

**CHỦ Ý không kiểm (và lý do):**
- Hiệu năng, tải đồng thời lớn – thuộc Chuyên đề tốt nghiệp 2 (NFR1, NFR2 chỉ đo thủ công khi demo).
- Giao diện trình duyệt bằng công cụ tự động – giao diện chỉ hiển thị, không chứa quy tắc nghiệp vụ; đã kiểm thủ công ba trạng thái (đang tải · rỗng · lỗi) và chụp ảnh ở BT2.
- Đăng nhập thật – ngoài phạm vi (W8), prototype giả lập người dùng bằng header.
- Chức năng chưa hiện thực: E6 đổi kỹ thuật viên, E7, E8 (TD-09) – không kiểm thứ chưa có.
- Bộ nạp Dataset Smart CRM với 7.800 phiếu – đã kiểm chạy lại không nhân đôi ở BT2; test tự động dùng dữ liệu mẫu nhỏ, cố định để kết quả lặp lại được.

## 2. Loại test và số lượng mỗi tầng
| Tầng | Số test | Tệp | Ghi chú |
|---|---|---|---|
| Unit – lớp nghiệp vụ và kiểm tra quyền (repository giả, không CSDL) | 35 | `tests/test_assignment_service.py`, `test_appointment_service.py`, `test_technician_service.py`, hồi quy `test_bug08_*.py`, `test_bug09_*.py` | Cô lập service khỏi CSDL và thời gian (truyền `now`) |
| Integration – service + PostgreSQL thử | 3 | `tests/test_integration_db.py` | TC07 NFR3 đồng thời, TC10 ràng buộc EXCLUDE, AC2.1 |
| API – FastAPI TestClient + PostgreSQL thử | 23 = 4 CRUD + **12 test case BT3** + 3 hồi quy + 2 bảo mật + 2 deploy | `tests/test_api_crud.py`, `tests/test_tc_bt3.py`, `tests/test_bug10_*.py`, `test_bug11_*.py`, `test_security.py`, `test_deploy_start.py` | 12 test case của Test Report, chạy cả bằng `scripts/run_tc.py` |
| Cấu hình | 2 | `tests/test_requirements.py` | Tệp khoá phiên bản `==`, UTF-8 (C6 – BUG-07) |
| **Tổng** | **63** | `python -m pytest -q` | Chạy cả trên CI (GitHub Actions) mỗi lần push |

**Kỹ thuật chọn dữ liệu:**
- **Phân vùng tương đương** cho khung giờ lịch hẹn: hợp lệ (15–120 phút, trong 08:00–18:00, thứ Hai – thứ Bảy) · quá ngắn · quá dài · ngoài giờ · Chủ nhật · quá khứ; cho người dùng: cùng trung tâm · khác trung tâm · header thiếu · header ngoài phạm vi.
- **Giá trị biên** ở hai bên cùng một ranh giới: 15 phút (TC-05, hợp lệ) / 14 phút (TC-06, không hợp lệ); thêm trong unit test: 120/121 phút, bắt đầu 07:59/08:00, kết thúc 18:00/18:01, ghi chú 255/300 ký tự, họ tên 1/120/121 ký tự.

**Đủ năm loại BT3 trong 12 test case:** luồng đúng ×4 (TC-01 – TC-04) · giá trị biên ×2 (TC-05, TC-06) · dữ liệu sai ×3 (TC-07 – TC-09) · bảo mật ×2 (TC-10 phân quyền A01, TC-11 header giả mạo) · tái lập ×1 (TC-12).

## 3. Tiêu chí thành công (đặt TRƯỚC khi chạy test)
- 12/12 test case có kết quả thực tế ghi từ lần chạy thật và ảnh chụp `docs/screenshots/TC-xx.png`.
- Mỗi quy tắc đã hiện thực (QT-06, QT-07, QT-08, QT-13, QT-14, QT-L4-01 … 06) có ≥ 1 test.
- Toàn bộ bộ kiểm thử PASS bằng một lệnh `python -m pytest -q`.
- Không còn bug Critical đang mở; mọi bug Major phát hiện được đã sửa, mỗi bug một commit riêng, ghi Bug Log bảy dòng.
- Không endpoint nào trả 500 với dữ liệu đầu vào sai – phải là 400/401/403/404/409/422 theo API contract.

## 4. Môi trường và dữ liệu thử
- Máy: Windows 11, Python 3.12, PostgreSQL 16 (cục bộ); CI: GitHub Actions `ubuntu-latest` + dịch vụ `postgres:16` (`.github/workflows/ci.yml`).
- Dữ liệu: `db/seed/001_du_lieu_mau.sql` – 6 nhóm sự cố, 6 kỹ thuật viên (A tay nghề 4, B 5, C 3, D 2, E khác trung tâm, F nghỉ việc), 10 dòng tay nghề, 13 phiếu (3 phiếu MOI ở trung tâm 2).
- Dựng và dọn: **resetDb trước MỖI test case** – tạo database riêng `smartcrm_test` nếu chưa có, chạy migration + dữ liệu mẫu (xoá rồi nạp lại); không đụng database `smartcrm` đang dùng.
- Lệnh: `python -m pytest -q` (toàn bộ) · `python -m scripts.run_tc TC-05` (một test case, in tám cột) · `python -m scripts.run_tc --report` (sinh Test Report từ `docs/test-runs.jsonl`).
