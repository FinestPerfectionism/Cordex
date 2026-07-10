CREATE TABLE IF NOT EXISTS partnership_meta (
    id        INTEGER NOT NULL PRIMARY KEY,
    timestamp INTEGER NOT NULL DEFAULT 0
);

INSERT OR IGNORE INTO partnership_meta (id, timestamp) VALUES (0, 0);