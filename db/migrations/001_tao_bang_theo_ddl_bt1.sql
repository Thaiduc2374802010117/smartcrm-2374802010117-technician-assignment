-- =====================================================================
-- Migration 001 – tạo bảng theo đúng DDL đã nộp ở BT1 (docs/schema.sql)
-- SQL DDL skeleton – Luồng L4: Phân công kỹ thuật viên và lịch hẹn
-- Sinh viên: Nguyễn Thái Đức – 2374802010117 – Track SE · PostgreSQL 16
-- 6 bảng: issue_category, technician, technician_skill, ticket,
--         appointment, ticket_status_log
-- center_id, changed_by, created_by là cột mã (không FK): danh mục trung tâm
-- và nhân viên quản lý thuộc hệ thống dùng chung, ngoài phạm vi L4.
-- =====================================================================
CREATE EXTENSION IF NOT EXISTS btree_gist;   -- cho ràng buộc EXCLUDE

CREATE TABLE IF NOT EXISTS issue_category (
    category_id       SERIAL PRIMARY KEY,
    category_name     VARCHAR(60) NOT NULL UNIQUE,   -- MAN_HINH, PIN, SAC, PHAN_MEM, NUOC_VAO, KHAC
    default_priority  VARCHAR(10) NOT NULL CHECK (default_priority IN ('CAO','TRUNG_BINH','THAP')),
    is_active         BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS technician (
    technician_id  BIGSERIAL PRIMARY KEY,
    full_name      VARCHAR(120) NOT NULL,
    center_id      INT NOT NULL,                     -- mã trung tâm làm việc (QT-08, QT-14)
    level          VARCHAR(10) NOT NULL CHECK (level IN ('SO_CAP','TRUNG_CAP','CAO_CAP')),
    is_active      BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS technician_skill (
    technician_id  BIGINT   NOT NULL REFERENCES technician(technician_id),
    category_id    INT      NOT NULL REFERENCES issue_category(category_id),
    proficiency    SMALLINT NOT NULL CHECK (proficiency BETWEEN 1 AND 5),
    PRIMARY KEY (technician_id, category_id)
);

CREATE TABLE IF NOT EXISTS ticket (
    ticket_id      BIGSERIAL PRIMARY KEY,
    ticket_code    VARCHAR(20) NOT NULL UNIQUE,      -- BH000123/2026
    center_id      INT    NOT NULL,                  -- trung tâm tiếp nhận
    category_id    INT    REFERENCES issue_category(category_id),
    issue_desc     TEXT   NOT NULL,
    priority       VARCHAR(10) NOT NULL CHECK (priority IN ('CAO','TRUNG_BINH','THAP')),
    status         VARCHAR(20) NOT NULL CHECK (status IN ('MOI','DA_PHAN_CONG','DANG_XU_LY',
                                   'CHO_LINH_KIEN','HOAN_TAT','DA_DONG','DA_HUY')),
    technician_id  BIGINT REFERENCES technician(technician_id),   -- tối đa 1 KTV (QT-07)
    received_at    TIMESTAMPTZ NOT NULL,
    due_date       TIMESTAMPTZ NOT NULL,             -- sinh ở L2 theo QT-04, L4 chỉ đọc
    is_deleted     BOOLEAN NOT NULL DEFAULT false,   -- soft delete (QT-13)
    CONSTRAINT ck_ticket_assigned CHECK (status IN ('MOI','DA_HUY') OR technician_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS appointment (
    appointment_id    BIGSERIAL PRIMARY KEY,
    ticket_id         BIGINT NOT NULL REFERENCES ticket(ticket_id),
    technician_id     BIGINT NOT NULL REFERENCES technician(technician_id),
    appointment_type  VARCHAR(10) NOT NULL CHECK (appointment_type IN ('GIAO_MAY','TRA_MAY')),
    start_at          TIMESTAMPTZ NOT NULL,
    end_at            TIMESTAMPTZ NOT NULL,
    status            VARCHAR(12) NOT NULL DEFAULT 'DA_HEN' CHECK (status IN ('DA_HEN','DA_HUY','HOAN_THANH')),
    note              VARCHAR(255),
    created_by        BIGINT NOT NULL,               -- mã nhân viên quản lý
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_appt_duration CHECK (end_at > start_at
        AND end_at - start_at BETWEEN INTERVAL '15 minutes' AND INTERVAL '120 minutes'),  -- QT-L4-03
    CONSTRAINT ex_appt_no_overlap EXCLUDE USING gist (                                  -- QT-L4-02
        technician_id WITH =, tstzrange(start_at, end_at, '[)') WITH &&) WHERE (status = 'DA_HEN')
);

CREATE TABLE IF NOT EXISTS ticket_status_log (
    log_id              BIGSERIAL PRIMARY KEY,
    ticket_id           BIGINT NOT NULL REFERENCES ticket(ticket_id),
    from_status         VARCHAR(20),                 -- NULL ở lần ghi đầu tiên
    to_status           VARCHAR(20) NOT NULL,
    from_technician_id  BIGINT REFERENCES technician(technician_id),   -- ghi đổi KTV (QT-07)
    to_technician_id    BIGINT REFERENCES technician(technician_id),
    changed_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    changed_by          BIGINT NOT NULL,             -- mã nhân viên thực hiện
    note                VARCHAR(255),
    CONSTRAINT ck_log_reassign_reason CHECK (from_status IS DISTINCT FROM to_status
        OR (to_technician_id IS NOT NULL AND char_length(note) >= 10))
);

-- Index phục vụ NFR1, NFR2
CREATE INDEX IF NOT EXISTS idx_ticket_center_status_due ON ticket (center_id, status, due_date) WHERE is_deleted = false;  -- NFR1
CREATE INDEX IF NOT EXISTS idx_ticket_technician_status ON ticket (technician_id, status);                                -- NFR1, NFR2
CREATE INDEX IF NOT EXISTS idx_technician_center        ON technician (center_id) WHERE is_active;                       -- NFR2
CREATE INDEX IF NOT EXISTS idx_skill_category           ON technician_skill (category_id, proficiency);                  -- NFR2
CREATE INDEX IF NOT EXISTS idx_log_ticket_time          ON ticket_status_log (ticket_id, changed_at);                    -- NFR3
