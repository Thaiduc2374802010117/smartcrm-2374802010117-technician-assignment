-- Dữ liệu mẫu rút gọn cho module Phân công (buổi 8).
-- Danh mục nhóm sự cố theo Bảng 3.1 case study; kỹ thuật viên, tay nghề, phiếu theo ví dụ
-- trong tiêu chí chấp nhận US2 (A tay nghề 4, B 5, C 3, D 2). Mã trung tâm theo service_centers.csv của dataset: 2 = TTBH Quận Tân Bình, 1 = TTBH Quận 10.
-- Chạy lại nhiều lần được: xóa sạch rồi nạp lại (CHỈ dùng cho môi trường phát triển).
TRUNCATE ticket_status_log, appointment, ticket, technician_skill, technician, issue_category RESTART IDENTITY CASCADE;

INSERT INTO issue_category (category_name, default_priority) VALUES
  ('MAN_HINH','TRUNG_BINH'), ('PIN','TRUNG_BINH'), ('SAC','THAP'),
  ('PHAN_MEM','THAP'), ('NUOC_VAO','CAO'), ('KHAC','THAP');

INSERT INTO technician (full_name, center_id, level, is_active) VALUES
  ('Lê Thị A',   2, 'TRUNG_CAP', true),   -- id 1
  ('Trần Văn B', 2, 'CAO_CAP',   true),   -- id 2
  ('Phạm Văn C', 2, 'TRUNG_CAP', true),   -- id 3
  ('Ngô Văn D',  2, 'SO_CAP',    true),   -- id 4: tay nghề màn hình 2 -> không đủ QT-08
  ('Võ Thị E',   1, 'CAO_CAP',   true),   -- id 5: khác trung tâm
  ('Đặng Văn F', 2, 'TRUNG_CAP', false);  -- id 6: đã nghỉ việc

INSERT INTO technician_skill (technician_id, category_id, proficiency) VALUES
  (1,1,4), (2,1,5), (3,1,3), (4,1,2), (5,1,5), (6,1,5),
  (1,2,3), (3,2,4), (2,3,3), (4,3,3);

-- Phiếu chờ phân công (MOI). Hạn cam kết tính từ bây giờ để thấy cờ "sắp quá hạn".
INSERT INTO ticket (ticket_code, center_id, category_id, issue_desc, priority, status, received_at, due_date) VALUES
  ('BH000231/2026', 2, 1, 'Màn hình sọc xanh sau khi rơi, cảm ứng không nhận', 'CAO',        'MOI', now() - interval '4 hour',  now() + interval '20 hour'),
  ('BH000228/2026', 2, 2, 'Pin tụt nhanh, máy nóng khi sạc',                    'TRUNG_BINH', 'MOI', now() - interval '20 hour', now() + interval '52 hour'),
  ('BH000240/2026', 2, 3, 'Cắm sạc báo lỗi phụ kiện',                           'THAP',       'MOI', now() - interval '2 hour',  now() + interval '118 hour'),
  ('BH000300/2026', 1, 1, 'Màn hình chết điểm ảnh',                             'TRUNG_BINH', 'MOI', now() - interval '1 hour',  now() + interval '71 hour');

-- Phiếu đang mở để có khối lượng công việc: A 2 phiếu, B 2 phiếu, C 5 phiếu.
INSERT INTO ticket (ticket_code, center_id, category_id, issue_desc, priority, status, technician_id, received_at, due_date)
SELECT format('BH%s/2026', lpad((100 + g)::text, 6, '0')), 2, 1, 'Phiếu mẫu đang xử lý', 'TRUNG_BINH',
       CASE WHEN g % 2 = 0 THEN 'DA_PHAN_CONG' ELSE 'DANG_XU_LY' END,
       CASE WHEN g <= 2 THEN 1 WHEN g <= 4 THEN 2 ELSE 3 END,
       now() - interval '1 day', now() + interval '2 day'
FROM generate_series(1, 9) AS g;
