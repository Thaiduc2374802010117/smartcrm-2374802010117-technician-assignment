# Nhật ký thay đổi thiết kế

Luồng L4 – Phân công kỹ thuật viên và lịch hẹn · Nguyễn Thái Đức – 2374802010117 · Track SE

## Sau phản hồi Bài tập 1 (buổi 8, ngày 19/10/2026)

Điểm BT1: 8.5/10 (Đầy đủ 9.5 · Kỹ thuật 7.5 · Nhất quán 9 · Trình bày 8.5).

### TD-01 Rút ERD từ 8 bảng về 6 bảng
- Phản hồi của GV : ERD và DDL có 8 bảng (thêm service_center, employee), đề yêu cầu 4–6 bảng. Gợi ý gộp employee
                    vào technician (thêm full_name, center_id) và bỏ service_center, chỉ giữ center_id là một cột.
- Quyết định      : SỬA
- Lý do           : Đúng yêu cầu 4–6 bảng của track SE. Trong phạm vi L4, thông tin cần về nhân viên chỉ là họ tên
                    và trung tâm của kỹ thuật viên; danh mục trung tâm không có thuộc tính nào L4 dùng tới.
- Ảnh hưởng       : technician thêm full_name, center_id (cột mã, không FK); ticket.center_id, appointment.created_by,
                    ticket_status_log.changed_by thành cột mã. ERD còn 6 bảng, 9 khóa ngoại. Cập nhật docs/schema.sql,
                    docs/schema.dbml, docs/diagrams/erd.png, wireframe M2 (Kỹ thuật viên ← technician.full_name),
                    bảng nhất quán thuật ngữ, migration db/migrations/001_tao_bang_theo_ddl_bt1.sql.

### TD-02 Giả lập người dùng bằng header thay cho tra bảng employee
- Phản hồi của GV : (hệ quả của TD-01) không còn bảng employee để tra vai trò và trung tâm.
- Quyết định      : SỬA
- Lý do           : Đăng nhập và phân quyền đầy đủ là W8 (ngoài phạm vi). Prototype cần một nguồn vai trò và
                    trung tâm để giữ NFR4 và QT-14.
- Ảnh hưởng       : Mỗi request gửi X-Employee-Id, X-Role, X-Center-Id; kiểm tra quyền ở một chỗ
                    (src/backend/api/auth.py). Sửa phần đánh đổi của câu lập luận NFR4 (mục 3.2), mục 6 của
                    docs/api-contract.md và nhãn lớp API trên architecture.drawio.

### TD-03 Đặt đúng tên file nộp
- Phản hồi của GV : Tên file có thêm " (1)", chưa đúng mẫu BT1_<MSSV>_<HoTen>.pdf.
- Quyết định      : SỬA
- Lý do           : Trình duyệt tự thêm " (1)" khi thư mục Downloads đã có file trùng tên.
- Ảnh hưởng       : Không ảnh hưởng thiết kế. Quy trình nộp: xóa file cũ trước khi tải, kiểm tra tên trên
                    E-learning sau khi nộp. Áp dụng cho BT2, BT3.

### TD-04 Rút gọn PDF, chuyển các bảng soi lỗi vào repo
- Phản hồi của GV : Bài dài 21 trang, gợi ý 6–9 trang; các bảng soi lỗi ERD và 3NF có thể để trong repo.
- Quyết định      : SỬA
- Lý do           : PDF chỉ giữ phần bắt buộc theo khung slide Buổi 6 và các phần GV đã đánh giá tốt.
- Ảnh hưởng       : PDF còn 14 trang (bìa, mục lục, 12 trang nội dung). Bảng soi 5 lỗi ERD, 3NF, tiêu chí GWT,
                    đặc tả UC4 nằm trong docs/thiet-ke.md và docs/srs.md.

### TD-05 Giữ nguyên kiến trúc 4 lớp và 4 câu lập luận
- Phản hồi của GV : Đánh giá tốt sơ đồ 4 lớp, bảng trách nhiệm từng lớp và 4 câu lập luận đúng khuôn.
- Quyết định      : GIỮ NGUYÊN
- Lý do           : Đây là khung để dựng mã nguồn ở BT2: thư mục src/backend/ ánh xạ một–một với 4 lớp.
- Ảnh hưởng       : src/backend/api (① trình bày) · services (② nghiệp vụ) · repositories (③ truy cập dữ liệu)
                    · db.py + PostgreSQL (④ lưu trữ).

### TD-06 Đưa hai test GV gợi ý vào kế hoạch BT2
- Phản hồi của GV : Viết test cho NFR3 (2 yêu cầu phân công cùng lúc → đúng 1 thành công, đúng 1 dòng lịch sử) và
                    test ràng buộc EXCLUDE với 09:00–09:30 và 09:15–09:45 (AC1 của US5).
- Quyết định      : SỬA (bổ sung)
- Lý do           : Hai test kiểm chứng trực tiếp hai quyết định kỹ thuật quan trọng nhất của thiết kế.
- Ảnh hưởng       : Bảng truy vết ghi TC07 (NFR3), TC10 (EXCLUDE). Buổi 8 đã có unit test lớp nghiệp vụ cho kịch
                    bản NFR3 (tests/test_assignment_service.py) và đã chạy thử 2 yêu cầu đồng thời trên API thật
                    (201 và 409, đúng 1 dòng lịch sử). Test EXCLUDE làm cùng module Lịch hẹn ở buổi 10.

## Trong buổi 10 – Sprint 2 (module mở rộng và giao diện)

### TD-07 E2 trả thêm thông tin phiếu
- Phản hồi / vấn đề : Màn hình M2 cần mã phiếu, nhóm sự cố, mức ưu tiên, hạn cam kết, mô tả lỗi; API contract chưa có
                      endpoint chi tiết phiếu.
- Quyết định        : SỬA
- Lý do             : Thêm trường `ticket` vào response E2 thay vì thêm endpoint mới – không đổi số endpoint, M2 chỉ
                      gọi 1 API khi mở màn hình.
- Ảnh hưởng         : docs/api-contract.md (E2, E4 thêm `full_name`, `ticket_code`); SuggestionService; pages/assign.js.

### TD-08 Đăng nhập giả lập ở giao diện
- Phản hồi / vấn đề : Slide buổi 10 yêu cầu đăng nhập và xử lý 401; đăng nhập thật là W8 (ngoài phạm vi).
- Quyết định        : SỬA
- Lý do             : Trang đăng nhập lưu thông tin người dùng giả lập (mã nhân viên, vai trò, mã trung tâm) vào
                      localStorage; api/client.js gắn 3 header vào mọi request; nhận 401 thì xoá và về trang đăng nhập.
- Ảnh hưởng         : src/frontend/index.html, api/client.js. Không đổi backend (auth.py từ buổi 8).

### TD-09 Thu hẹp phạm vi Sprint 2 – phần đã cắt
- Phản hồi / vấn đề : Slide buổi 10 "Khi thiếu thời gian": giữ luồng chính, ghi nhận phần đã cắt.
- Quyết định        : HOÃN
- Lý do             : Luồng chính UC2 → UC4 (phân công rồi đặt lịch hẹn) ưu tiên trước. Ba chức năng mức SHOULD
                      chưa làm: E6 đổi kỹ thuật viên (US4), E7 phiếu của kỹ thuật viên (US6), E8 bảng khối lượng
                      công việc (US7). Ô "Lý do đổi kỹ thuật viên" trên M2 chưa hiển thị.
- Ảnh hưởng         : Bảng kiểm trong README mục 6; làm tiếp sau khi nộp BT2 nếu còn thời gian.

### TD-10 Nạp Dataset Smart CRM và mô phỏng phiếu mới
- Phản hồi / vấn đề : Checklist buổi 10 yêu cầu chạy trên dữ liệu mẫu THẬT; tickets_history.csv là phiếu lịch sử,
                      hầu hết đã đóng nên không có phiếu MOI để phân công.
- Quyết định        : SỬA
- Lý do             : `python -m src.backend.seed_dataset --reopen 5` nạp technicians.csv, technician_skills.csv,
                      tickets_history.csv; chọn 5 phiếu gần nhất mỗi trung tâm đặt lại MOI, dời thời gian về hiện tại,
                      hạn cam kết tính lại theo QT-04. Dòng lỗi bị bỏ qua và in lý do.
- Ảnh hưởng         : src/backend/seed_dataset.py; db/seed/ (dữ liệu rút gọn) vẫn giữ cho test tích hợp.

### TD-11 Giao diện chạy riêng, backend bật CORS
- Phản hồi / vấn đề : Điều kiện "xong" của slide: tắt backend phải thấy thông báo lỗi có nút thử lại – nếu backend
                      phục vụ luôn giao diện thì tắt backend sẽ mất cả trang.
- Quyết định        : SỬA
- Lý do             : Giao diện chạy bằng `python -m http.server 5500 -d src/frontend`, gọi API ở cổng 3000
                      (api/config.js). Backend cho phép origin http://localhost:5500 (biến FRONTEND_ORIGIN).
- Ảnh hưởng         : src/backend/main.py (CORSMiddleware), README mục 3.

### TD-12 Dùng mã gốc của Dataset Smart CRM
- Phản hồi / vấn đề : Dataset chính thức có issue_categories.csv (mã và mức ưu tiên mặc định riêng, ví dụ MAN_HINH = CAO)
                      và service_centers.csv (TTBH Quận Tân Bình mã 2, Quận 10 mã 1); tài liệu trước đó lấy ví dụ Tân Bình = 4.
- Quyết định        : SỬA
- Lý do             : Giữ nguyên mã gốc của dataset để dữ liệu không bị lệch mà không báo lỗi.
- Ảnh hưởng         : seed_dataset.py đọc issue_categories.csv và in tên trung tâm; dữ liệu rút gọn db/seed/, test tích hợp,
                      trang đăng nhập và ví dụ JSON trong docs/api-contract.md đổi Tân Bình sang mã 2.
