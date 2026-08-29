CREATE TABLE IF NOT EXISTS GuildConfig (
    guild_id INTEGER NOT NULL,
    config_key TEXT NOT NULL,
    config_value INTEGER,
    PRIMARY KEY (guild_id, config_key)
);