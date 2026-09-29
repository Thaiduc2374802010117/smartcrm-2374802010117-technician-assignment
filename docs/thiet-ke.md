# Thiết kế kiến trúc

![Sơ đồ kiến trúc phân lớp](diagrams/architecture.png)

File gốc: [`architecture.drawio`](architecture.drawio). Kiến trúc chọn: **monolith phân lớp** (một ứng dụng, năm lớp), chạy một tiến trình trên máy cá nhân.

| Lớp | Trách nhiệm | Trao đổi với lớp khác |
|---|---|---|
| ① Giao diện | Hiển thị 3 màn hình (xem wireframe), kiểm tra nhập liệu cơ bản; không chứa quy tắc nghiệp vụ | Gửi HTTP/JSON tới lớp API, kèm header `X-Employee-Id` |
| ② API | Nhận request theo API contract (E1–E8), kiểm tra kiểu dữ liệu, kiểm tra quyền dùng chung (vai trò + trung tâm), trả mã HTTP thống nhất | Gọi hàm Python của lớp Nghiệp vụ; không truy cập CSDL trực tiếp |
| ③ Nghiệp vụ | Áp dụng quy tắc: gợi ý và phân công (QT-06, QT-07, QT-08, QT-L4-01), lịch hẹn (QT-L4-02…05), truy vấn danh sách và khối lượng công việc | Gọi hàm Python của lớp Truy cập dữ liệu; không biết gì về HTTP |
| ④ Truy cập dữ liệu | Câu SQL tham số hóa, mở/đóng giao dịch, UPDATE có điều kiện | Gửi SQL tới PostgreSQL qua TCP cổng 5432 |
| ⑤ Cơ sở dữ liệu | Lưu 6 bảng chính; ràng buộc khóa, CHECK, EXCLUDE; index | Chỉ nhận kết nối từ lớp ④ |

**Quy tắc phụ thuộc:** lớp trên chỉ gọi lớp ngay dưới, không gọi tắt. **Ngoài phạm vi** (khối xám trong sơ đồ): L2 tiếp nhận, L5 kho linh kiện, L8 khảo sát, đăng nhập, SMS/Zalo, cập nhật tiến độ sửa chữa. Dữ liệu các phần này lấy từ bộ dữ liệu mẫu của case study, nạp một lần.

**Lập luận lựa chọn kiến trúc**

1. Vì **NFR3** yêu cầu phân công và ghi lịch sử phiếu cùng thành công hoặc cùng không xảy ra, và khi có 2 yêu cầu đồng thời thì **đúng 1** thành công, tôi chọn **một cơ sở dữ liệu quan hệ PostgreSQL duy nhất, giao dịch do lớp Truy cập dữ liệu quản lý, và câu `UPDATE ... WHERE status = 'MOI'` có điều kiện**, đánh đổi là mọi chức năng dùng chung một CSDL nên không tách triển khai riêng được, và tôi phải tự viết SQL thay vì dùng ORM cho nhanh.
2. Vì **NFR4** yêu cầu **100%** chức năng kiểm tra vai trò và trung tâm, tôi chọn **đặt việc kiểm tra quyền ở một thành phần dùng chung của lớp API, chạy trước mọi endpoint**, thay vì để từng hàm tự kiểm tra, đánh đổi là mỗi request tốn thêm một truy vấn tra bảng `employee` và lớp API phụ thuộc vào bảng này.
3. Vì **NFR1** và **NFR2** yêu cầu danh sách phiếu **dưới 2 giây** và gợi ý **dưới 1 giây** với **10.000 phiếu**, tôi chọn **để CSDL lọc, đếm và sắp xếp bằng truy vấn có index `(center_id, status, due_date)` và `(technician_id, status)`**, thay vì tải toàn bộ phiếu lên lớp Nghiệp vụ rồi xử lý bằng Python, đánh đổi là một phần quy tắc gợi ý QT-08 nằm trong câu SQL nên khó kiểm thử đơn vị hơn, và mỗi index làm thao tác ghi chậm thêm một chút.
4. Vì **NFR1** yêu cầu **dưới 2 giây trên máy 8 GB RAM** và dự án chỉ có một người làm trong 6 buổi, tôi chọn **monolith phân lớp chạy một tiến trình** thay vì tách microservices, đánh đổi là khi các luồng khác (L2, L5) nhập vào sẽ dùng chung một mã nguồn và không mở rộng từng phần độc lập được.

# Mô hình dữ liệu (Track SE)

![ERD luồng L4](diagrams/erd.png)

File gốc: [`schema.dbml`](schema.dbml) (dbdiagram.io) · SQL DDL: [`schema.sql`](schema.sql) (đã kiểm tra cú pháp bằng bộ phân tích cú pháp PostgreSQL).

| Bảng | Vai trò trong L4 | Khóa chính | Khóa ngoại |
|---|---|---|---|
| `issue_category` | Nhóm sự cố của phiếu, để khớp tay nghề | `category_id` | — (được tham chiếu) |
| `technician` | Kỹ thuật viên, trung tâm, bậc | `technician_id` | `employee_id`, `center_id` |
| `technician_skill` | Tay nghề 1–5 theo nhóm sự cố (QT-08) | `(technician_id, category_id)` | `technician_id`, `category_id` |
| `ticket` | Phiếu bảo hành, trạng thái phiếu, kỹ thuật viên đang giữ | `ticket_id` | `center_id`, `category_id`, `technician_id` |
| `appointment` | Lịch hẹn giao – nhận máy | `appointment_id` | `ticket_id`, `technician_id`, `created_by` |
| `ticket_status_log` | Lịch sử phiếu: chuyển trạng thái và đổi kỹ thuật viên (QT-06, QT-07) | `log_id` | `ticket_id`, `from_technician_id`, `to_technician_id`, `changed_by` |

**Kiểm chứng track SE:** 6 bảng chính ✔ · mỗi bảng có khóa chính ✔ · 15 quan hệ khóa ngoại ✔ · không bảng cô lập ✔ · có SQL DDL skeleton ✔. Hai bảng phụ trợ tối thiểu `service_center`, `employee` được case study cho phép tự thiết kế (Mục 8), chỉ giữ cột cần cho L4.

**Điều chỉnh so với từ điển dữ liệu tham chiếu (Mục 8 case study), có lý do:**
- `ticket_status_log` thêm `from_technician_id`, `to_technician_id` để ghi việc đổi kỹ thuật viên kèm lý do (QT-07) mà không cần thêm bảng thứ 7.
- `ticket` lược bỏ `customer_id`, `device_id`, `is_warranty` (thuộc L2, L4 không dùng); thêm `is_deleted` cho QT-13.
- `appointment` do tôi thiết kế (case study chỉ nêu tên): ràng buộc `EXCLUDE` chặn trùng lịch ở mức CSDL (QT-L4-02), `CHECK` độ dài 15–120 phút (QT-L4-03).
- Dùng `TIMESTAMPTZ` thay `TIMESTAMP` để lưu múi giờ +07:00 đúng quy ước ISO 8601 của API contract.

# Wireframe 3 màn hình

![Wireframe 3 màn hình](wireframe.png)

| Màn hình | Dạng | Use case | Trường hiển thị → cột trong ERD |
|---|---|---|---|
| 1. Danh sách phiếu chờ phân công | Danh sách | UC1 | Mã phiếu `ticket.ticket_code` · Nhóm sự cố `issue_category.category_name` · Mức ưu tiên `ticket.priority` · Thời điểm tiếp nhận `ticket.received_at` · Hạn cam kết `ticket.due_date` |
| 2. Phân công kỹ thuật viên | Chi tiết + sửa | UC2, UC3, UC4 | Kỹ thuật viên `employee.full_name` · Bậc `technician.level` · Tay nghề `technician_skill.proficiency` · Số phiếu đang mở (đếm `ticket`) · Mô tả lỗi `ticket.issue_desc` · Lý do đổi `ticket_status_log.note` |
| 3. Đặt lịch hẹn giao – nhận máy | Tạo mới | UC5 | Loại lịch hẹn `appointment.appointment_type` · Bắt đầu `appointment.start_at` · Kết thúc `appointment.end_at` · Ghi chú `appointment.note` |

UC6 (danh sách phiếu của kỹ thuật viên) và UC7 (bảng khối lượng công việc) dùng lại bố cục bảng của Màn hình 1, không vẽ riêng.
