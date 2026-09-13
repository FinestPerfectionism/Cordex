CREATE TABLE IF NOT EXISTS Notes (
    member_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    PRIMARY KEY (member_id, guild_id)
);