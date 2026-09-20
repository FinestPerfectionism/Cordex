CREATE TABLE IF NOT EXISTS CommandRestrictions (
    guild_id     INTEGER NOT NULL,
    command_name TEXT    NOT NULL,
    target_type  TEXT    NOT NULL CHECK (target_type IN ('user', 'role')),
    target_id    INTEGER NOT NULL,
    PRIMARY KEY (guild_id, command_name, target_type, target_id)
);