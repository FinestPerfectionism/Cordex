CREATE TABLE IF NOT EXISTS Quarantines (
    member_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    old_roles TEXT NOT NULL,
    PRIMARY KEY (user_id, guild_id)
);