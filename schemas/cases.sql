CREATE TABLE IF NOT EXISTS Cases (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type  TEXT NOT NULL,
    moderator_id INTEGER NOT NULL,
    target_id    INTEGER,
    channel_id   INTEGER,
    reason       TEXT NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    dm_user           INTEGER,
    seconds_to_delete INTEGER,
    timeout_length    INTEGER,
    purge_amount      INTEGER,
    purge_force       INTEGER,

    expired         INTEGER DEFAULT 0,
    related_case_id INTEGER,

    FOREIGN KEY (related_case_id) REFERENCES Cases (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS IDXCasesTarget ON Cases(target_id);
CREATE INDEX IF NOT EXISTS IDXCasesAction ON Cases(action_type);
