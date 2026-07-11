DROP TABLE IF EXISTS partnerships;

CREATE TABLE partnerships (
    id                 INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    server_name        TEXT NOT NULL DEFAULT '',
    server_description TEXT NOT NULL DEFAULT '',
    server_owner_id    INTEGER NOT NULL DEFAULT 0,
    server_link        TEXT NOT NULL DEFAULT '',
    image_filename     TEXT NOT NULL DEFAULT '',
    timestamp          INTEGER NOT NULL DEFAULT 0
);

INSERT INTO partnerships (id, timestamp) VALUES (0, 0);