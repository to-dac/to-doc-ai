-- ============================================================
-- to-dac ERD DDL (PostgreSQL)
-- ============================================================

-- ------------------------------------------------------------
-- 1. users
--    해커톤용 러프 스키마
-- ------------------------------------------------------------
CREATE TABLE users (
    id          SERIAL          PRIMARY KEY,
    email       VARCHAR(255)    NOT NULL UNIQUE,
    user_name   VARCHAR(100)    NOT NULL,
    password    VARCHAR(255)    NOT NULL,           -- bcrypt hash
    created_at  TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- ------------------------------------------------------------
-- 2. chat_sessions
--    왼쪽 사이드바의 대화 목록 한 row = 한 채팅방
--    address: 조회 대상 토지/건물 주소 (같은 주소 반복 입력 방지)
-- ------------------------------------------------------------
CREATE TABLE chat_sessions (
    id          SERIAL          PRIMARY KEY,
    user_id     INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(255)    NOT NULL DEFAULT '새 채팅',   -- 첫 메시지에서 자동 생성
    address     VARCHAR(500),                                  -- 핀 찍은 토지/건물 주소
    created_at  TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- ------------------------------------------------------------
-- 3. messages
--    role: 'user' | 'assistant'
--    status: AI 응답은 MCP 처리 전까지 'pending'
--            content는 pending 동안 NULL 허용
-- ------------------------------------------------------------
CREATE TABLE messages (
    id          SERIAL          PRIMARY KEY,
    session_id  INTEGER         NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role        VARCHAR(20)     NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT,
    status      VARCHAR(20)     NOT NULL DEFAULT 'completed'
                                CHECK (status IN ('pending', 'completed', 'failed')),
    created_at  TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- ------------------------------------------------------------
-- 4. attachments
--    세션 단위로 귀속 (한번 업로드 → 같은 세션에서 재참조)
--    file_type: 'image' | 'document' | 'map'
-- ------------------------------------------------------------
CREATE TABLE attachments (
    id          SERIAL          PRIMARY KEY,
    session_id  INTEGER         NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id     INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_name   VARCHAR(255)    NOT NULL,
    file_url    VARCHAR(1000)   NOT NULL,
    file_type   VARCHAR(20)     NOT NULL DEFAULT 'image'
                                CHECK (file_type IN ('image', 'document', 'map')),
    created_at  TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- ------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------
CREATE INDEX idx_chat_sessions_user_id   ON chat_sessions(user_id);
CREATE INDEX idx_messages_session_id     ON messages(session_id);
CREATE INDEX idx_attachments_session_id  ON attachments(session_id);
