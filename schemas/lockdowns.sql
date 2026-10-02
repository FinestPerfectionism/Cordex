CREATE TABLE IF NOT EXISTS Lockdowns (
    channel_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    PRIMARY KEY (channel_id, guild_id)
);