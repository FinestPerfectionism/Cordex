from typing import TYPE_CHECKING, cast, final

from discord import Guild, Member, Role

from bot.types import GuildMessagable

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Configuration State
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class Config:
    def __init__(self, bot : Cordex, guild : Guild) -> None:
        super().__init__()
        self.bot   = bot
        self.guild = guild

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_command_allowed
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_command_allowed(self) -> list[Role | Member]:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_moderation_quarantine_role
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_moderation_quarantine_role(self) -> Role | None:
        async with self.bot.db.execute(
            t"SELECT config_value FROM GuildConfig WHERE guild_id = {self.guild.id} AND config_key = {"moderation_quarantine_role"}",
        ) as cursor:
            res = await cursor.fetchone()

        if not res:
            return None

        role_id = cast("int | None", res[0])
        if role_id is None:
            return None

        return self.guild.get_role(role_id)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_moderation_logging_channel
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_moderation_logging_channel(self) -> GuildMessagable | None:
        async with self.bot.db.execute(
            t"SELECT config_value FROM GuildConfig WHERE guild_id = {self.guild.id} AND config_key = {"moderation_logging_channel"}",
        ) as cursor:
            res = await cursor.fetchone()

        if not res:
            return None

        channel_id = cast("int | None", res[0])
        if channel_id is None:
            return None

        log_channel = self.guild.get_channel(channel_id)

        if not isinstance(log_channel, GuildMessagable):
            return None

        return log_channel

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_messages_delete_logging_channel
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_messages_delete_logging_channel(self) -> GuildMessagable | None:
        async with self.bot.db.execute(
            t"SELECT config_value FROM GuildConfig WHERE guild_id = {self.guild.id} AND config_key = {"messages_delete_channel"}",
        ) as cursor:
            res = await cursor.fetchone()

        if not res:
            return None

        channel_id = cast("int | None", res[0])
        if channel_id is None:
            return None

        log_channel = self.guild.get_channel(channel_id)

        if not isinstance(log_channel, GuildMessagable):
            return None

        return log_channel

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_messages_edit_logging_channel
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_messages_edit_logging_channel(self) -> GuildMessagable | None:
        async with self.bot.db.execute(
            t"SELECT config_value FROM GuildConfig WHERE guild_id = {self.guild.id} AND config_key = {"messages_edit_channel"}",
        ) as cursor:
            res = await cursor.fetchone()

        if not res:
            return None

        channel_id = cast("int | None", res[0])
        if channel_id is None:
            return None

        log_channel = self.guild.get_channel(channel_id)

        if not isinstance(log_channel, GuildMessagable):
            return None

        return log_channel

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_messages_preview
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_messages_preview(self) -> bool:
        async with self.bot.db.execute(
            t"SELECT config_value FROM GuildConfig WHERE guild_id = {self.guild.id} AND config_key = {"messages_preview"}",
        ) as cursor:
            res = await cursor.fetchone()

        if not res:
            return False

        value = cast("int | None", res[0])
        return value is not None
