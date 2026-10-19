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
