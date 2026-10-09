# Phụ lục – Bảng khai báo sử dụng công cụ AI

| Công cụ | Phần áp dụng | Cách dùng (tóm tắt yêu cầu đã gửi) | Em đã chỉnh sửa / kiểm chứng gì |
|---|---|---|---|
| Claude (trợ lý AI dạng chat) | Buổi 2: phiếu phạm vi, README, cấu trúc repo, `src/backend/main.py` | "Đọc file buổi 2 và làm các yêu cầu cho luồng L4"; "chỉ tôi thiết lập Git repo theo yêu cầu đề" | Tự chọn stack Python 3.12 + FastAPI, HTML/CSS/JS; tự cấu hình Git bằng email trường, tạo repo, tự phát hiện lỗi tên repo thừa dấu "-"; tự cài Python, PostgreSQL; sửa lỗi sai mật khẩu và lỗi chưa tạo database theo thông báo lỗi; chạy `/` và `/db-check` thành công |
| Claude | Mục 1 – SRS, 7 User Story, tiêu chí Given–When–Then | "Đọc 2 file buổi 3 và làm đầy đủ yêu cầu"; "làm theo đúng yêu cầu buổi 4"; "đọc kĩ yêu cầu buổi 6" | Chọn làm theo checklist Buổi 4 (8 story, 3 MUST), rồi rút về 7 story khi nộp BT1 theo yêu cầu 5–7; đối chiếu vấn đề V2, V3 và quy tắc QT-04, QT-06, QT-07, QT-08 với case study; đối chiếu thứ tự US1–US7 với phiếu phạm vi đã nộp |
| Claude | Mục 2 – Use Case Diagram, đặc tả UC2, UC4 | "Use case phải là use case mạnh" (theo nhắc nhở của thầy trên lớp) | Đưa yêu cầu "use case mạnh" của thầy vào; đồng ý bỏ use case yếu "Xem gợi ý kỹ thuật viên" sau khi áp phép thử "làm xong actor có đạt mục tiêu không"; mở `usecase.drawio` bằng draw.io để kiểm tra file gốc |
| Claude | Mục 3 – Kiến trúc; Mục 4 – ERD, SQL DDL | "Đọc file buổi 5 và làm 4 việc thầy giao" | Đối chiếu sơ đồ với mẫu kiến trúc 4 lớp của slide Buổi 5; kiểm 4 câu lập luận theo khuôn "Vì NFR… tôi chọn… đánh đổi là…"; soát 5 lỗi ERD và 3NF (sửa phụ thuộc bắc cầu `technician.center_id`) |
| Claude | Mục 5 – Wireframe; rà soát nhất quán | "Đọc kĩ file buổi 6 làm cho tôi" | Chạy 6 phép kiểm nhất quán và 11 mục kiểm chứng; kiểm từng trường wireframe có cột trong ERD; kiểm 7 luồng ngoại lệ có chỗ hiển thị thông báo |

**Phần em tự làm:**

- Chọn luồng L4 và Track SE; tự thực hiện toàn bộ thao tác trên máy: tạo repo GitHub, cài đặt môi trường, chạy backend, commit theo Conventional Commits và merge `dev` vào `main` sau mỗi lần cập nhật.
- Đọc lại, đối chiếu tài liệu với case study Mekong Mobile và các slide Buổi 2 – 6; quyết định các điểm thay đổi phạm vi (số User Story, bỏ use case yếu).

Tôi xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp.

Họ tên: Nguyễn Thái Đức · MSSV: 2374802010117 · Ngày: 09/10/2026
