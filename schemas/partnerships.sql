CREATE TABLE IF NOT EXISTS partnerships (
    id        INTEGER NOT NULL PRIMARY KEY,
    timestamp INTEGER NOT NULL DEFAULT 0
);

INSERT OR IGNORE INTO partnerships (id, timestamp) VALUES (0, 0);