-- =====================================================================
-- SQL DDL skeleton – Luồng L4: Phân công kỹ thuật viên và lịch hẹn
-- Sinh viên: Nguyễn Thái Đức – 2374802010117 – Track SE
-- CSDL: PostgreSQL 16 · Thời gian dùng TIMESTAMPTZ (ISO 8601 kèm +07:00)
-- 6 bảng chính: issue_category, technician, technician_skill, ticket,
--               appointment, ticket_status_log
-- 2 bảng phụ trợ tối thiểu (Mục 8 case study): service_center, employee
-- =====================================================================
CREATE EXTENSION IF NOT EXISTS btree_gist;   -- cho ràng buộc EXCLUDE chống trùng lịch

-- ---------- Bảng phụ trợ tối thiểu ----------
CREATE TABLE service_center (
    center_id    SERIAL PRIMARY KEY,
    center_name  VARCHAR(120) NOT NULL,
    city         VARCHAR(60)
);

CREATE TABLE employee (
    employee_id  BIGSERIAL PRIMARY KEY,
    full_name    VARCHAR(120) NOT NULL,
    role         VARCHAR(20)  NOT NULL CHECK (role IN ('QUAN_LY', 'KY_THUAT_VIEN')),
    center_id    INT NOT NULL REFERENCES service_center(center_id),
    is_active    BOOLEAN NOT NULL DEFAULT true
);

-- ---------- 6 bảng chính của L4 ----------
CREATE TABLE issue_category (
    category_id       SERIAL PRIMARY KEY,
    category_name     VARCHAR(60) NOT NULL UNIQUE,      -- MAN_HINH, PIN, SAC, PHAN_MEM, NUOC_VAO, KHAC
    default_priority  VARCHAR(10) NOT NULL CHECK (default_priority IN ('CAO', 'TRUNG_BINH', 'THAP')),
    is_active         BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE technician (
    technician_id  BIGSERIAL PRIMARY KEY,
    employee_id    BIGINT NOT NULL UNIQUE REFERENCES employee(employee_id),
    -- 3NF: trung tâm làm việc lấy qua employee.center_id, không lưu lặp ở đây
    level          VARCHAR(10) NOT NULL CHECK (level IN ('SO_CAP', 'TRUNG_CAP', 'CAO_CAP')),
    is_active      BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE technician_skill (
    technician_id  BIGINT   NOT NULL REFERENCES technician(technician_id),
    category_id    INT      NOT NULL REFERENCES issue_category(category_id),
    proficiency    SMALLINT NOT NULL CHECK (proficiency BETWEEN 1 AND 5),
    PRIMARY KEY (technician_id, category_id)
);

CREATE TABLE ticket (
    ticket_id      BIGSERIAL PRIMARY KEY,
    ticket_code    VARCHAR(20) NOT NULL UNIQUE,          -- BH000123/2026
    center_id      INT    NOT NULL REFERENCES service_center(center_id),
    category_id    INT    REFERENCES issue_category(category_id),
    issue_desc     TEXT   NOT NULL,
    priority       VARCHAR(10) NOT NULL CHECK (priority IN ('CAO', 'TRUNG_BINH', 'THAP')),
    status         VARCHAR(20) NOT NULL CHECK (status IN ('MOI', 'DA_PHAN_CONG', 'DANG_XU_LY',
                                   'CHO_LINH_KIEN', 'HOAN_TAT', 'DA_DONG', 'DA_HUY')),
    technician_id  BIGINT REFERENCES technician(technician_id),   -- tối đa 1 KTV (QT-07)
    received_at    TIMESTAMPTZ NOT NULL,
    due_date       TIMESTAMPTZ NOT NULL,                  -- sinh ở L2 theo QT-04, L4 chỉ đọc
    is_deleted     BOOLEAN NOT NULL DEFAULT false,        -- soft delete (QT-13)
    -- phiếu đã qua trạng thái Mới thì bắt buộc có kỹ thuật viên
    CONSTRAINT ck_ticket_assigned CHECK (status IN ('MOI', 'DA_HUY') OR technician_id IS NOT NULL)
    -- customer_id, device_id: thuộc L2, lược bỏ trong mô hình L4
);

CREATE TABLE appointment (
    appointment_id    BIGSERIAL PRIMARY KEY,
    ticket_id         BIGINT NOT NULL REFERENCES ticket(ticket_id),
    technician_id     BIGINT NOT NULL REFERENCES technician(technician_id),
    appointment_type  VARCHAR(10) NOT NULL CHECK (appointment_type IN ('GIAO_MAY', 'TRA_MAY')),
    start_at          TIMESTAMPTZ NOT NULL,
    end_at            TIMESTAMPTZ NOT NULL,
    status            VARCHAR(12) NOT NULL DEFAULT 'DA_HEN'
                      CHECK (status IN ('DA_HEN', 'DA_HUY', 'HOAN_THANH')),
    note              VARCHAR(255),
    created_by        BIGINT NOT NULL REFERENCES employee(employee_id),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_appt_duration CHECK (end_at > start_at
        AND end_at - start_at BETWEEN INTERVAL '15 minutes' AND INTERVAL '120 minutes'),   -- QT-L4-03
    -- QT-L4-02: hai lịch hẹn DA_HEN của cùng KTV không được giao nhau
    CONSTRAINT ex_appt_no_overlap EXCLUDE USING gist (
        technician_id WITH =, tstzrange(start_at, end_at, '[)') WITH &&
    ) WHERE (status = 'DA_HEN')
);

CREATE TABLE ticket_status_log (
    log_id              BIGSERIAL PRIMARY KEY,
    ticket_id           BIGINT NOT NULL REFERENCES ticket(ticket_id),
    from_status         VARCHAR(20),                       -- NULL ở lần ghi đầu tiên
    to_status           VARCHAR(20) NOT NULL,
    from_technician_id  BIGINT REFERENCES technician(technician_id),   -- thêm để ghi đổi KTV (QT-07)
    to_technician_id    BIGINT REFERENCES technician(technician_id),
    changed_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    changed_by          BIGINT NOT NULL REFERENCES employee(employee_id),
    note                VARCHAR(255),
    -- dòng đổi KTV (trạng thái giữ nguyên) bắt buộc có lý do 10–255 ký tự
    CONSTRAINT ck_log_reassign_reason CHECK (
        from_status IS DISTINCT FROM to_status
        OR (to_technician_id IS NOT NULL AND char_length(note) >= 10))
);

-- ---------- Index phục vụ NFR1, NFR2 ----------
CREATE INDEX idx_ticket_center_status_due ON ticket (center_id, status, due_date)
    WHERE is_deleted = false;                                      -- E1: danh sách phiếu Mới (NFR1)
CREATE INDEX idx_ticket_technician_status ON ticket (technician_id, status);   -- E2, E6, E7: đếm phiếu đang mở (NFR2)
CREATE INDEX idx_skill_category ON technician_skill (category_id, proficiency); -- E2: lọc KTV đủ tay nghề (NFR2)
CREATE INDEX idx_appt_technician_start ON appointment (technician_id, start_at); -- E4: lịch hẹn của KTV
CREATE INDEX idx_log_ticket_time ON ticket_status_log (ticket_id, changed_at);
