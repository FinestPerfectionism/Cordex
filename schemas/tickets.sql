CREATE TABLE IF NOT EXISTS tickets (
    thread_id INTEGER PRIMARY KEY,
    team      TEXT    NOT NULL CHECK (team IN ('director', 'moderator')),
    open      INTEGER NOT NULL DEFAULT 1 CHECK (open IN (0, 1))
);