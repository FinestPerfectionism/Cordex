CREATE TABLE IF NOT EXISTS guild_info (
    channel_id INTEGER NOT NULL,
    position   INTEGER NOT NULL,
    message_id INTEGER NOT NULL UNIQUE,
    PRIMARY KEY (channel_id, position)
);