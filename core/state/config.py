from collections.abc import Sequence
from typing import TYPE_CHECKING, cast, final

from discord import Guild, Member, Role, User

from bot.types import GuildMessagable

from .restrictions import Restriction

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
    # reset
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def reset(self) -> None:
        await self.bot.db.execute(t"DELETE FROM Config WHERE guild_id = {self.guild.id}")
        await self.bot.db.commit()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_command_allowed
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_command_allowed(self, command_name : str, /) -> list[Role | Member]:
        restriction = self.bot.get_restriction(self.guild.id, command_name)
        if restriction is None:
            return []

        roles   = [role for role_id in sorted(restriction.role_ids) if (role := self.guild.get_role(role_id)) is not None]
        members = [member for user_id in sorted(restriction.user_ids) if (member := self.guild.get_member(user_id)) is not None]

        return [*roles, *members]

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # set_command_allowed
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def set_command_allowed(self, command_name : str, allowed : Sequence[Role | Member | User], /) -> None:
        role_ids = frozenset(target.id for target in allowed if isinstance(target, Role))
        user_ids = frozenset(target.id for target in allowed if not isinstance(target, Role))

        try:
            await self.bot.db.execute(
                t"DELETE FROM CommandRestrictions WHERE guild_id = {self.guild.id} AND command_name = {command_name}",
            )

            for role_id in role_ids:
                await self.bot.db.execute(
                    t"INSERT INTO CommandRestrictions (guild_id, command_name, target_type, target_id) VALUES ({self.guild.id}, {command_name}, {"role"}, {role_id})",
                )

            for user_id in user_ids:
                await self.bot.db.execute(
                    t"INSERT INTO CommandRestrictions (guild_id, command_name, target_type, target_id) VALUES ({self.guild.id}, {command_name}, {"user"}, {user_id})",
                )

            await self.bot.db.commit()
        except Exception:
            await self.bot.db.rollback()
            raise

        self.bot.set_restriction(
            self.guild.id,
            command_name,
            Restriction(user_ids, role_ids) if (role_ids or user_ids) else None,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_moderation_quarantine_role
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_moderation_quarantine_role(self) -> Role | None:
        async with self.bot.db.execute(
            t"SELECT config_value FROM Config WHERE guild_id = {self.guild.id} AND config_key = {"moderation_quarantine_role"}",
        ) as cursor:
            res = await cursor.fetchone()
            if not res:
                return None

        role_id = cast("int | None", res[0])
        if role_id is None:
            return None

        return self.guild.get_role(role_id)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # set_moderation_quarantine_role
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def set_moderation_quarantine_role(self, role : Role) -> None:
        await self.bot.db.execute(
            t"INSERT INTO Config (guild_id, config_key, config_value) VALUES ({self.guild.id}, {"moderation_quarantine_role"}, {role.id}) "
            t"ON CONFLICT (guild_id, config_key) DO UPDATE SET config_value = excluded.config_value",
        )
        await self.bot.db.commit()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_moderation_logging_channel
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_moderation_logging_channel(self) -> GuildMessagable | None:
        async with self.bot.db.execute(
            t"SELECT config_value FROM Config WHERE guild_id = {self.guild.id} AND config_key = {"moderation_logging_channel"}",
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
    # set_moderation_logging_channel
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def set_moderation_logging_channel(self, channel : GuildMessagable) -> None:
        await self.bot.db.execute(
            t"INSERT INTO Config (guild_id, config_key, config_value) VALUES ({self.guild.id}, {"moderation_logging_channel"}, {channel.id}) "
            t"ON CONFLICT (guild_id, config_key) DO UPDATE SET config_value = excluded.config_value",
        )
        await self.bot.db.commit()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_messages_delete_logging_channel
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_messages_delete_logging_channel(self) -> GuildMessagable | None:
        async with self.bot.db.execute(
            t"SELECT config_value FROM Config WHERE guild_id = {self.guild.id} AND config_key = {"messages_delete_channel"}",
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
    # set_messages_delete_logging_channel
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def set_messages_delete_logging_channel(self, channel : GuildMessagable) -> None:
        await self.bot.db.execute(
            t"INSERT INTO Config (guild_id, config_key, config_value) VALUES ({self.guild.id}, {"messages_delete_channel"}, {channel.id}) "
            t"ON CONFLICT (guild_id, config_key) DO UPDATE SET config_value = excluded.config_value",
        )
        await self.bot.db.commit()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_messages_edit_logging_channel
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_messages_edit_logging_channel(self) -> GuildMessagable | None:
        async with self.bot.db.execute(
            t"SELECT config_value FROM Config WHERE guild_id = {self.guild.id} AND config_key = {"messages_edit_channel"}",
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
    # set_messages_edit_logging_channel
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def set_messages_edit_logging_channel(self, channel : GuildMessagable) -> None:
        await self.bot.db.execute(
            t"INSERT INTO Config (guild_id, config_key, config_value) VALUES ({self.guild.id}, {"messages_edit_channel"}, {channel.id}) "
            t"ON CONFLICT (guild_id, config_key) DO UPDATE SET config_value = excluded.config_value",
        )
        await self.bot.db.commit()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_messages_preview
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_messages_preview(self) -> bool:
        async with self.bot.db.execute(
            t"SELECT config_value FROM Config WHERE guild_id = {self.guild.id} AND config_key = {"messages_preview"}",
        ) as cursor:
            res = await cursor.fetchone()
            if not res:
                return False

        return bool(cast("int | None", res[0]))

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # set_messages_preview
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def set_messages_preview(self, *, enabled : bool) -> None:
        await self.bot.db.execute(
            t"INSERT INTO Config (guild_id, config_key, config_value) VALUES ({self.guild.id}, {"messages_preview"}, {int(enabled)}) "
            t"ON CONFLICT (guild_id, config_key) DO UPDATE SET config_value = excluded.config_value",
        )
        await self.bot.db.commit()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_moderation_quarantine_enforce_channels
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_moderation_quarantine_enforce_channels(self) -> bool:
        async with self.bot.db.execute(
            t"SELECT config_value FROM Config WHERE guild_id = {self.guild.id} AND config_key = {"moderation_quarantine_enforce_channels"}",
        ) as cursor:
            res = await cursor.fetchone()
            if not res:
                return False

        return bool(cast("int | None", res[0]))

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # set_moderation_quarantine_enforce_channels
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def set_moderation_quarantine_enforce_channels(self, *, enabled : bool) -> None:
        await self.bot.db.execute(
            t"INSERT INTO Config (guild_id, config_key, config_value) VALUES ({self.guild.id}, {"moderation_quarantine_enforce_channels"}, {int(enabled)}) "
            t"ON CONFLICT (guild_id, config_key) DO UPDATE SET config_value = excluded.config_value",
        )
        await self.bot.db.commit()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_moderation_quarantine_enforce_roles
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_moderation_quarantine_enforce_roles(self) -> bool:
        async with self.bot.db.execute(
            t"SELECT config_value FROM Config WHERE guild_id = {self.guild.id} AND config_key = {"moderation_quarantine_enforce_roles"}",
        ) as cursor:
            res = await cursor.fetchone()
            if not res:
                return False

        return bool(cast("int | None", res[0]))

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # set_moderation_quarantine_enforce_roles
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def set_moderation_quarantine_enforce_roles(self, *, enabled : bool) -> None:
        await self.bot.db.execute(
            t"INSERT INTO Config (guild_id, config_key, config_value) VALUES ({self.guild.id}, {"moderation_quarantine_enforce_roles"}, {int(enabled)}) "
            t"ON CONFLICT (guild_id, config_key) DO UPDATE SET config_value = excluded.config_value",
        )
        await self.bot.db.commit()
