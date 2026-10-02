# Hợp đồng API (API contract) – Luồng L4
## Phân công kỹ thuật viên và lịch hẹn giao – nhận máy bảo hành

Sinh viên: Nguyễn Thái Đức – MSSV 2374802010117 – Track SE
Tài liệu bổ sung kỹ thuật cho [SRS](srs.md). Mọi endpoint truy vết về User Story và bảng truy vết mục 6 của SRS (phiên bản 1.2).

---

## 1. Danh sách endpoint

| # | Phương thức | Đường dẫn | Mục đích | User Story | FR | Vai trò |
|---|---|---|---|---|---|---|
| E1 | GET | `/api/tickets?status=MOI` | Danh sách phiếu chờ phân công, có lọc và phân trang | US1 | FR1 | Quản lý |
| E2 | GET | `/api/tickets/{ticket_id}/technician-suggestions` | Gợi ý tối đa 3 kỹ thuật viên phù hợp | US2 | FR2 | Quản lý |
| E3 | POST | `/api/tickets/{ticket_id}/assignment` | Phân công phiếu Mới cho một kỹ thuật viên | US3 | FR3 | Quản lý |
| E4 | GET | `/api/technicians/{technician_id}/appointments` | Xem lịch hẹn của kỹ thuật viên trong khoảng thời gian | US5 | FR5 | Quản lý |
| E5 | POST | `/api/tickets/{ticket_id}/appointments` | Tạo lịch hẹn giao / trả máy, chặn trùng lịch | US5 | FR5 | Quản lý |
| E6 | PUT | `/api/tickets/{ticket_id}/assignment` | Đổi kỹ thuật viên kèm lý do | US4 | FR4 | Quản lý |
| E7 | GET | `/api/me/tickets` | Danh sách phiếu đang mở của kỹ thuật viên đang dùng | US6 | FR6 | Kỹ thuật viên |
| E8 | GET | `/api/workload` | Bảng khối lượng công việc của trung tâm | US7 | FR7 | Quản lý |
| E9 | GET | `/api/tickets/{ticket_id}/history` | Lịch sử phiếu: chuyển trạng thái, đổi kỹ thuật viên | US8 | FR8 | Quản lý |

Các endpoint `GET /` và `GET /db-check` là smoke test hạ tầng của Buổi 2, không phục vụ User Story nên **không thuộc hợp đồng này**.
Việc kỹ thuật viên cập nhật tiến độ sửa chữa là W4 trong SRS nên không có endpoint.

---

## 2. Quy ước chung

- **Định dạng:** JSON, mã hóa UTF-8. Header bắt buộc khi có body: `Content-Type: application/json`.
- **Tên trường:** `snake_case`, khớp tên cột trong cơ sở dữ liệu (ví dụ `ticket_id`, `due_date`, `technician_id`).
- **Thời gian:** ISO 8601 kèm múi giờ, ví dụ `2026-10-10T09:00:00+07:00`.
- **Giá trị danh mục:** viết hoa không dấu.
  - Trạng thái phiếu: `MOI`, `DA_PHAN_CONG`, `DANG_XU_LY`, `CHO_LINH_KIEN`, `HOAN_TAT`, `DA_DONG`, `DA_HUY`
  - Mức ưu tiên: `CAO`, `TRUNG_BINH`, `THAP`
  - Loại lịch hẹn: `GIAO_MAY`, `TRA_MAY` · Trạng thái lịch hẹn: `DA_HEN`, `DA_HUY`, `HOAN_THANH`
- **Dữ liệu mẫu trong JSON** lấy theo case study: trung tâm bảo hành Quận Tân Bình (quản lý: chị Trâm, Mục 4), mã phiếu dạng `BH000123/2026` (Mục 8), nhóm sự cố và mức ưu tiên theo Bảng 3.1, hạn cam kết tính theo QT-04 (CAO = 24 giờ).
- **Phân trang:** `page` (bắt đầu từ 1), `size` (mặc định 20, tối đa 100). Response danh sách kèm `page`, `size`, `total`.
- **Cấu trúc lỗi thống nhất:**
  ```json
  { "error": { "code": "MA_LOI", "message": "Mô tả cho người dùng", "fields": { "ten_truong": "lý do" } } }
  ```
- **Mã trạng thái dùng chung:**

| Mã | Khi nào |
|---|---|
| 200 OK | Đọc hoặc cập nhật thành công |
| 201 Created | Tạo mới thành công (phân công, lịch hẹn) |
| 400 Bad Request | Dữ liệu sai kiểu, thiếu trường bắt buộc (`VALIDATION_FAILED`) |
| 401 Unauthorized | Thiếu thông tin người dùng (`UNAUTHENTICATED`) |
| 403 Forbidden | Sai vai trò hoặc khác trung tâm (`FORBIDDEN`, QT-14) |
| 404 Not Found | Phiếu, kỹ thuật viên không tồn tại (`NOT_FOUND`) |
| 409 Conflict | Xung đột trạng thái hoặc trùng lịch (`INVALID_STATE`, `APPOINTMENT_CONFLICT`) |
| 422 Unprocessable Entity | Vi phạm quy tắc nghiệp vụ (`TECHNICIAN_NOT_ELIGIBLE`, `INVALID_TRANSITION`) |
| 500 Internal Server Error | Lỗi hệ thống không lường trước; không lộ chi tiết kỹ thuật |

---

## 3. Chi tiết endpoint (bắt buộc cho US mức MUST)

### E1. GET /api/tickets – Danh sách phiếu chờ phân công · US1 · FR1

**Query**

| Tham số | Bắt buộc | Mô tả |
|---|---|---|
| `status` | Có | Với US1 luôn là `MOI` |
| `category_id` | Không | Lọc theo nhóm sự cố |
| `priority` | Không | `CAO` / `TRUNG_BINH` / `THAP` |
| `page`, `size` | Không | Phân trang |

Trung tâm **lấy theo người dùng**, không nhận từ query, để bảo đảm QT-14. Kết quả luôn sắp theo `due_date` tăng dần.

**Response 200 OK**
```json
{
  "center_id": 4, "center_name": "Trung tâm bảo hành Quận Tân Bình",
  "page": 1, "size": 20, "total": 2,
  "items": [
    {
      "ticket_id": 88231,
      "ticket_code": "BH000231/2026",
      "category_id": 1, "category_name": "MAN_HINH",
      "priority": "CAO",
      "status": "MOI",
      "received_at": "2026-10-09T08:00:00+07:00",
      "due_date": "2026-10-10T08:00:00+07:00",
      "is_due_soon": true, "is_overdue": false
    },
    {
      "ticket_id": 88240,
      "ticket_code": "BH000240/2026",
      "category_id": 2, "category_name": "PIN",
      "priority": "TRUNG_BINH",
      "status": "MOI",
      "received_at": "2026-10-09T09:30:00+07:00",
      "due_date": "2026-10-12T09:30:00+07:00",
      "is_due_soon": false, "is_overdue": false
    }
  ]
}
```
**Response 400** – `priority` không thuộc danh mục hoặc `size` > 100 (`VALIDATION_FAILED`).
**Response 403** – người dùng không phải Quản lý (`FORBIDDEN`).

### E2. GET /api/tickets/{ticket_id}/technician-suggestions – Gợi ý kỹ thuật viên · US2 · FR2

Quy tắc (QT-08): `is_active = true`, cùng `center_id` với phiếu, `proficiency ≥ 3` ở `category_id` của phiếu. Sắp theo `open_ticket_count` tăng dần, rồi `proficiency` giảm dần. Tối đa 3 người.

**Response 200 OK**
```json
{
  "ticket_id": 88231,
  "category_name": "MAN_HINH",
  "suggestions": [
    { "technician_id": 12, "full_name": "Trần Văn B", "level": "CAO_CAP",  "proficiency": 5, "open_ticket_count": 2 },
    { "technician_id": 7,  "full_name": "Lê Thị A",   "level": "TRUNG_CAP","proficiency": 4, "open_ticket_count": 2 },
    { "technician_id": 21, "full_name": "Phạm Văn C", "level": "TRUNG_CAP","proficiency": 3, "open_ticket_count": 5 }
  ]
}
```
**Response 200 – không có ai phù hợp** (không phải lỗi; UC3 ngoại lệ 3a)
```json
{ "ticket_id": 88231, "category_name": "MAN_HINH", "suggestions": [],
  "message": "Không có kỹ thuật viên đủ tay nghề tại trung tâm" }
```
**Response 404** – phiếu không tồn tại (`NOT_FOUND`).
**Response 403** – phiếu thuộc trung tâm khác (`FORBIDDEN`).
**Response 422** – phiếu chưa có nhóm sự cố nên không gợi ý được (`CATEGORY_REQUIRED`).

### E3. POST /api/tickets/{ticket_id}/assignment – Phân công · US3 · FR3

**Request body**
```json
{ "technician_id": 12 }
```
**Response 201 Created**
```json
{
  "ticket_id": 88231,
  "ticket_code": "BH000231/2026",
  "status": "DA_PHAN_CONG",
  "technician_id": 12,
  "assigned_at": "2026-10-09T10:05:00+07:00",
  "status_log": {
    "log_id": 5501,
    "from_status": "MOI",
    "to_status": "DA_PHAN_CONG",
    "to_technician_id": 12,
    "changed_at": "2026-10-09T10:05:00+07:00",
    "changed_by": 3
  }
}
```
**Response 400** – thiếu `technician_id` hoặc không phải số nguyên dương
```json
{ "error": { "code": "VALIDATION_FAILED", "message": "Dữ liệu không hợp lệ",
  "fields": { "technician_id": "Trường bắt buộc, phải là số nguyên dương" } } }
```
**Response 404** – phiếu hoặc kỹ thuật viên không tồn tại.
**Response 409** – phiếu không còn ở trạng thái Mới (đã được phân công, UC3 ngoại lệ 5a)
```json
{ "error": { "code": "INVALID_STATE",
  "message": "Phiếu đã được phân công cho kỹ thuật viên khác. Dùng chức năng đổi kỹ thuật viên.",
  "fields": { "current_status": "DA_PHAN_CONG", "technician_id": "7" } } }
```
**Response 422** – kỹ thuật viên không thỏa QT-08 (UC3 ngoại lệ 5b)
```json
{ "error": { "code": "TECHNICIAN_NOT_ELIGIBLE",
  "message": "Kỹ thuật viên không đủ tay nghề (cần ≥ 3) hoặc không cùng trung tâm",
  "fields": { "technician_id": "12" } } }
```
Ghi chú hiện thực: kiểm tra trạng thái và cập nhật trong **cùng giao dịch** (NFR3), ví dụ `UPDATE ... WHERE ticket_id = ? AND status = 'MOI'`; số dòng bị ảnh hưởng = 0 thì trả 409.

### E4. GET /api/technicians/{technician_id}/appointments – Lịch hẹn của kỹ thuật viên · US5

**Query:** `from`, `to` (ISO 8601, bắt buộc, khoảng tối đa 7 ngày).

**Response 200 OK**
```json
{
  "technician_id": 12,
  "items": [
    { "appointment_id": 301, "ticket_id": 88100, "appointment_type": "TRA_MAY",
      "start_at": "2026-10-10T09:00:00+07:00", "end_at": "2026-10-10T09:30:00+07:00", "status": "DA_HEN" }
  ]
}
```
**Response 400** – thiếu `from`/`to` hoặc khoảng > 7 ngày. **Response 403** – kỹ thuật viên thuộc trung tâm khác. **Response 404** – kỹ thuật viên không tồn tại.

### E5. POST /api/tickets/{ticket_id}/appointments – Tạo lịch hẹn · US5 · FR5

Lịch hẹn tự gắn với kỹ thuật viên **đang giữ phiếu** (QT-L4-04), không nhận `technician_id` từ body.

**Request body**
```json
{
  "appointment_type": "TRA_MAY",
  "start_at": "2026-10-10T10:00:00+07:00",
  "end_at":   "2026-10-10T10:30:00+07:00",
  "note": "Khách hẹn lấy máy trước giờ trưa"
}
```
**Response 201 Created**
```json
{
  "appointment_id": 305,
  "ticket_id": 88231,
  "technician_id": 12,
  "appointment_type": "TRA_MAY",
  "start_at": "2026-10-10T10:00:00+07:00",
  "end_at": "2026-10-10T10:30:00+07:00",
  "status": "DA_HEN",
  "created_by": 3
}
```
**Response 400** – sai định dạng thời gian, `end_at` ≤ `start_at`, ngoài giờ làm việc (UC5 ngoại lệ 4a)
```json
{ "error": { "code": "VALIDATION_FAILED", "message": "Khung giờ không hợp lệ",
  "fields": { "start_at": "Lịch hẹn phải trong 08:00–18:00, thứ Hai đến thứ Bảy" } } }
```
**Response 409** – trùng lịch kỹ thuật viên (UC5 ngoại lệ 5a, QT-L4-02)
```json
{ "error": { "code": "APPOINTMENT_CONFLICT", "message": "Kỹ thuật viên đã có lịch hẹn trong khung giờ này",
  "fields": { "conflict_appointment_id": "301",
              "conflict_start_at": "2026-10-10T09:00:00+07:00",
              "conflict_end_at": "2026-10-10T09:30:00+07:00",
              "suggested_start_at": "2026-10-10T09:30:00+07:00" } } }
```
**Response 422** – phiếu chưa có kỹ thuật viên (UC5 ngoại lệ 1a)
```json
{ "error": { "code": "TICKET_NOT_ASSIGNED", "message": "Phiếu chưa được phân công", "fields": {} } }
```
Điều kiện trùng: tồn tại lịch hẹn `status = 'DA_HEN'` của cùng kỹ thuật viên với `start_at < new_end_at AND end_at > new_start_at`.

---

## 4. Endpoint mức SHOULD và COULD (tóm tắt)

| Endpoint | Request | Response thành công | Response lỗi chính |
|---|---|---|---|
| **E6** PUT `/api/tickets/{id}/assignment` | `{ "technician_id": 7, "reason": "KTV B nghỉ phép đột xuất" }` | 200 – phiếu với `technician_id` mới, dòng `status_log` có `from_technician_id`, `to_technician_id`, `note` = lý do; lịch hẹn chưa diễn ra bị hủy (QT-L4-05) | 400 thiếu lý do · 409 phiếu không đang mở hoặc chọn trùng KTV hiện tại · 422 KTV mới không thỏa QT-08 |
| **E7** GET `/api/me/tickets` | Query `page`, `size` | 200 – danh sách phiếu đang mở của KTV, sắp theo `due_date`, có `is_due_soon`, `is_overdue` | 401 thiếu người dùng · 403 không phải KTV |
| **E9** GET `/api/tickets/{id}/history` | Không | 200 – `[{ log_id, from_status, to_status, from_technician_id, to_technician_id, note, changed_at, changed_by }]` sắp theo `changed_at` tăng dần | 403 phiếu thuộc trung tâm khác · 404 phiếu không tồn tại |
| **E8** GET `/api/workload` | Không | 200 – `[{ technician_id, full_name, open_ticket_count, due_soon_count, overdue_count }]` | 401 thiếu người dùng · 403 không phải Quản lý |

---

## 5. Bảng validation

### E3 – POST assignment

| Trường | Bắt buộc | Kiểu / ràng buộc | Thông báo lỗi |
|---|---|---|---|
| `ticket_id` (path) | Có | Số nguyên dương, tồn tại, thuộc trung tâm của quản lý (QT-14) | Không tìm thấy phiếu / Không có quyền với phiếu này |
| — trạng thái phiếu | — | Phải là `MOI` (QT-L4-01) | Phiếu đã được phân công. Dùng chức năng đổi kỹ thuật viên |
| `technician_id` | Có | Số nguyên dương, tồn tại, `is_active = true` | Kỹ thuật viên không tồn tại hoặc đã nghỉ việc |
| — tay nghề | — | Cùng trung tâm và `proficiency ≥ 3` ở nhóm sự cố của phiếu (QT-08) | Kỹ thuật viên không đủ tay nghề hoặc không cùng trung tâm |

### E5 – POST appointments

| Trường | Bắt buộc | Kiểu / ràng buộc | Thông báo lỗi |
|---|---|---|---|
| `ticket_id` (path) | Có | Tồn tại, thuộc trung tâm, đang mở và đã có kỹ thuật viên (QT-L4-04) | Phiếu chưa được phân công |
| `appointment_type` | Có | `GIAO_MAY` hoặc `TRA_MAY` | Loại lịch hẹn không hợp lệ |
| `start_at` | Có | ISO 8601; sau thời điểm hiện tại; thứ Hai–thứ Bảy; ≥ 08:00 (QT-L4-03) | Thời gian bắt đầu không hợp lệ |
| `end_at` | Có | ISO 8601; > `start_at`; ≤ 18:00 cùng ngày; độ dài 15–120 phút | Thời gian kết thúc không hợp lệ |
| — trùng lịch | — | Không giao nhau với lịch hẹn `DA_HEN` của cùng kỹ thuật viên (QT-L4-02) | Kỹ thuật viên đã có lịch hẹn trong khung giờ này |
| `note` | Không | Chuỗi, tối đa 255 ký tự | Ghi chú tối đa 255 ký tự |

### E6 – PUT assignment

| Trường | Bắt buộc | Kiểu / ràng buộc | Thông báo lỗi |
|---|---|---|---|
| `technician_id` | Có | Như E3; khác kỹ thuật viên hiện tại | Kỹ thuật viên mới phải khác kỹ thuật viên hiện tại |
| `reason` | Có | Chuỗi 10–255 ký tự (QT-07) | Lý do đổi phải có từ 10 đến 255 ký tự |
| — trạng thái phiếu | — | `DA_PHAN_CONG`, `DANG_XU_LY` hoặc `CHO_LINH_KIEN` | Chỉ đổi kỹ thuật viên khi phiếu đang mở |


### E1 – Query

| Tham số | Ràng buộc | Thông báo lỗi |
|---|---|---|
| `status` | Thuộc danh mục trạng thái | Trạng thái không hợp lệ |
| `priority` | `CAO` / `TRUNG_BINH` / `THAP` | Mức ưu tiên không hợp lệ |
| `page` | Số nguyên ≥ 1 | Trang không hợp lệ |
| `size` | Số nguyên 1–100 | Kích thước trang từ 1 đến 100 |

---

## 6. Xác thực và phân quyền

Phiên bản hiện tại **giả lập** người dùng (W8 trong SRS): mỗi request gửi header `X-Employee-Id` với mã nhân viên có trong bảng `employee`. Hệ thống tra vai trò và trung tâm từ mã này; không tin vai trò do client gửi lên.

| Endpoint | Quản lý trung tâm | Kỹ thuật viên |
|---|---|---|
| E1, E2, E3, E4, E5, E6, E8, E9 | ✅ trong trung tâm mình | ❌ 403 |
| E7 | ❌ 403 | ✅ phiếu của chính mình |

Thiếu header hoặc mã không tồn tại → **401**. Đúng vai trò nhưng khác trung tâm → **403** (QT-14).

---

## 7. Tự kiểm trước khi nộp

- [x] Mỗi endpoint nối được về ít nhất một User Story (bảng mục 1).
- [x] Mỗi endpoint MUST có ≥ 1 response thành công và ≥ 2 response lỗi.
- [x] Mọi trường request body có cột tương ứng trong mô hình dữ liệu dự kiến trong ERD (`ticket`, `technician`, `technician_skill`, `issue_category`, `appointment`, `ticket_status_log`) – đã đối chiếu với `schema.sql`.
- [x] Không có endpoint thừa.
- [x] QT-06, QT-07, QT-08, QT-14 và QT-L4-01…05 xuất hiện trong bảng validation hoặc mã lỗi.
