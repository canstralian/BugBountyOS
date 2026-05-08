-- Snowflake DDL parity for storage vector v1.0.0
-- Mirrors SQLAlchemy models in models.py

CREATE TABLE IF NOT EXISTS findings (
    id         NUMBER AUTOINCREMENT PRIMARY KEY,
    target     VARCHAR(512)  NOT NULL,
    severity   VARCHAR(16)   NOT NULL,
    title      VARCHAR(256)  NOT NULL,
    description TEXT         NOT NULL,
    status     VARCHAR(32)   NOT NULL DEFAULT 'draft',
    source_action_plan_id VARCHAR(36),
    created_at TIMESTAMP_TZ  NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS evidence (
    id          NUMBER AUTOINCREMENT PRIMARY KEY,
    finding_id  NUMBER REFERENCES findings(id),
    kind        VARCHAR(64)  NOT NULL,
    value       TEXT         NOT NULL,
    sha256      VARCHAR(64),
    created_at  TIMESTAMP_TZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS tool_runs (
    id         NUMBER AUTOINCREMENT PRIMARY KEY,
    tool       VARCHAR(128) NOT NULL,
    target     VARCHAR(512) NOT NULL,
    status     VARCHAR(32)  NOT NULL DEFAULT 'running',
    output_ref TEXT,
    created_at TIMESTAMP_TZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
