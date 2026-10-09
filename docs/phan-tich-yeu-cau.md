# Phân tích yêu cầu – Luồng L4
Sinh viên: Nguyễn Thái Đức – MSSV 2374802010117 – Track SE

Tài liệu làm việc cho Buổi 3 – 4: áp bộ mười câu hỏi khai thác lên case study Mekong Mobile, ghi lại ngoại lệ tìm được, và tự kiểm User Story theo INVEST. Kết quả được dùng để viết [SRS](srs.md).

---

## 1. Ba kỹ thuật lấy yêu cầu đã dùng

| Kỹ thuật | Nguồn trong case study | Thu được gì cho L4 |
|---|---|---|
| Phỏng vấn | Mục 4 – chị Trâm (quản lý TT Tân Bình), anh Dũng (KTV Cần Thơ) | Nhu cầu thấy khối lượng việc, phân công theo chuyên môn, biết phiếu gấp |
| Nghiên cứu tài liệu | Mục 5.1 phiếu giấy (ô "Kỹ thuật viên", "Hẹn trả"); Mục 8 từ điển dữ liệu (`technician`, `technician_skill`) | Trường dữ liệu và ràng buộc: tay nghề 1–5, `is_active`, `center_id` |
| Quan sát | Mục 6.1 bước 7–9 (phân công cuối buổi sáng, khay "chờ linh kiện" bị quên) | Hai đường tránh: phân công theo xấp phiếu; phiếu chờ linh kiện nằm 3 tuần |

## 2. Bộ mười câu hỏi khai thác áp lên L4

| # | Câu hỏi | Trả lời từ case study | Yêu cầu rút ra |
|---|---|---|---|
| 1 | Công việc này hiện đang làm thế nào? Ai làm? Mất bao lâu? | Quản lý lấy xấp phiếu cuối buổi sáng, phân công theo trí nhớ (6.1 bước 7). Cuối tháng đếm tay phiếu quá hạn gần một ngày (chị Trâm). | FR1, FR3, FR7 |
| 2 | Điều gì khiến việc này chậm hoặc sai nhất? | Không nhớ ai đang giữ bao nhiêu phiếu; giao sai chuyên môn phải chuyển qua lại (chị Trâm). | FR2 (gợi ý theo tay nghề và khối lượng) |
| 3 | Nếu hệ thống chỉ làm đúng MỘT việc, đó là gì? | "Một màn hình thấy được hôm nay có bao nhiêu phiếu, bao nhiêu sắp quá hạn, ai đang làm gì" (chị Trâm). | US1, US7; phân công là MUST |
| 4 | Ai dùng chức năng này? Mỗi vai trò thấy gì, không được thấy gì? | Quản lý trung tâm phân công; KTV xử lý. QT-14: chỉ thấy trung tâm mình; QT-15: KTV thấy SĐT dạng che. | Mục 2 SRS, NFR4 |
| 5 | Ai quyết định khi có tranh chấp? | Quản lý trung tâm quyết định phân công; KTV không tự nhận phiếu. | W6: hệ thống chỉ gợi ý, người quyết định |
| 6 | Thông tin nào BẮT BUỘC trước khi tạo bản ghi? | Phân công: phiếu + KTV. Lịch hẹn: phiếu đã có KTV + khung giờ. Đổi KTV: lý do (QT-07). | Bảng validation E3, E5, E6 |
| 7 | Thông tin nào không được sửa sau khi lưu? | Lịch sử trạng thái, lịch sử đổi KTV (QT-06, QT-07); không xóa vật lý (QT-13). | Log chỉ thêm, không sửa; lịch hẹn chỉ hủy |
| 8 | Quy tắc nghiệp vụ nào đang áp dụng? | QT-04, QT-06, QT-07, QT-08, QT-13, QT-14, QT-15. | Mục 5 SRS |
| 9 | Khi điều kiện bình thường không thỏa thì xử lý thế nào? | Xem mục 3 dưới đây. | Luồng ngoại lệ UC2, UC4 |
| 10 | Trường hợp nào phải làm thủ công ngoài hệ thống? | Không có KTV đủ tay nghề tại trung tâm; lỗi hàng loạt cùng lô (anh Dũng: "sửa lần thứ ba cùng lỗi thì báo lên"). | UC2 ngoại lệ 3a; báo lỗi lô: WON'T (ngoài L4) |

## 3. Ngoại lệ tìm được (câu 9)

| # | Tình huống | Xử lý đề xuất | Đưa vào |
|---|---|---|---|
| N1 | Không có KTV nào cùng trung tâm đủ tay nghề ≥ 3 | Báo rõ, phiếu giữ trạng thái Mới, quản lý xử lý ngoài hệ thống | UC2 – 3a |
| N2 | Hai quản lý cùng phân công một phiếu | Chỉ người đầu tiên thành công; người sau nhận thông báo đã phân công | UC2 – 5a, NFR3 |
| N3 | KTV nghỉ việc / bị chỉnh tay nghề giữa lúc đang chọn | Kiểm tra lại khi xác nhận, tải lại gợi ý | UC2 – 5b |
| N4 | Mất kết nối khi đang lưu phân công | Hủy giao dịch, cho phép thử lại, không sinh log trùng | UC2 – 6a |
| N5 | Đặt lịch hẹn trùng giờ KTV | Từ chối, gợi ý khung giờ trống gần nhất | UC4 – 5a |
| N6 | Đặt lịch hẹn cho phiếu chưa phân công | Từ chối, dẫn tới chức năng phân công | UC4 – 1a |
| N7 | Đổi KTV khi phiếu đã có lịch hẹn | Hủy lịch hẹn chưa diễn ra, yêu cầu đặt lại | QT-L4-05 |
| N8 | Phiếu nằm Chờ linh kiện quá lâu (6.1 bước 9: có phiếu 3 tuần) | Hiển thị trong bảng khối lượng công việc (phiếu quá hạn); cảnh báo tự động để hướng mở rộng | US7 |
| N9 | Phân công lại phiếu đã có KTV bằng chức năng phân công | Từ chối, yêu cầu dùng chức năng đổi KTV (QT-L4-01) | FR3, E3 |

## 4. "Hỏi vì sao hai lần" – từ giải pháp về yêu cầu thật

| Phát biểu gốc | Vì sao? (lần 1 → lý do) | Vì sao? (lần 2 → yêu cầu thật) |
|---|---|---|
| Chị Trâm: "Em cần một màn hình thấy ai đang làm gì" | Để biết ai rảnh mà giao việc | Hệ thống phải tính được **số phiếu đang mở của từng KTV** và dùng nó khi gợi ý (FR2, FR7) |
| Anh Dũng: "Em không biết cái nào gấp, thường làm cái dễ trước" | Vì xấp phiếu giấy không có thứ tự | Danh sách phiếu của KTV phải **sắp theo hạn cam kết** và **đánh dấu phiếu sắp quá hạn** (FR6) |
| Chị Trâm: "Giao sai người thì mất thời gian chuyển qua lại" | Vì mỗi KTV giỏi một nhóm sự cố khác nhau | Chỉ gợi ý KTV có **tay nghề ≥ 3 ở đúng nhóm sự cố** (QT-08, FR2); đổi người phải **có lý do** để truy được (FR4) |

## 5. Tự kiểm INVEST cho 7 User Story

| Story | I | N | V | E | S | T | Ghi chú |
|---|---|---|---|---|---|---|---|
| US1 Xem phiếu chờ phân công | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Chỉ đọc dữ liệu có sẵn |
| US2 Gợi ý KTV | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Chỉ cần phiếu + dữ liệu tay nghề |
| US3 Phân công | ✅* | ✅ | ✅ | ✅ | ✅ | ✅ | *Dùng điều kiện của US2 nhưng hiện thực và kiểm thử riêng được |
| US4 Đổi KTV | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| US5 Đặt lịch hẹn | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Kiểm thử bằng phiếu đã phân công sẵn |
| US6 Danh sách của KTV | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |
| US7 Khối lượng công việc | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | |

**Đã sửa so với bản nháp Buổi 2:**
- Bản nháp "hệ thống **gợi ý 3 kỹ thuật viên** (cùng trung tâm, tay nghề ≥ 3, ít việc nhất)" chứa chi tiết hiện thực → đưa chi tiết sang FR2 và tiêu chí chấp nhận, story chỉ giữ mục tiêu (tiêu chí **N**).
- Bản nháp "đổi kỹ thuật viên kèm lý do **bắt buộc**" và "ghi lịch sử trạng thái" → giữ ở FR, không nhồi vào story.
- Khi nộp BT1: giữ 7 story (5–7 theo yêu cầu BT1), 3 MUST (US1, US2, US3); story "KTV cập nhật trạng thái" thành W4, "xem lịch sử phiếu" và "hủy lịch hẹn thủ công" thành W9, W10.

## 6. Tự kiểm bốn lỗi khi phát biểu yêu cầu

| Lỗi | Đã kiểm | Ví dụ đã tránh |
|---|---|---|
| Mơ hồ | ✅ | Không dùng "nhanh", "dễ dùng"; NFR đều có số (2 giây, 3 lần bấm) |
| Không kiểm chứng được | ✅ | Mỗi NFR có cột "Cách kiểm chứng" |
| Hai yêu cầu trong một câu | ✅ | Phân công (FR3) tách khỏi đặt lịch hẹn (FR5) |
| Nêu giải pháp thay vì yêu cầu | ✅ | SRS không nêu tên công nghệ; chi tiết SQL chỉ nằm trong ghi chú hiện thực của API contract |
