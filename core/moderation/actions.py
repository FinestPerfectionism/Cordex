from asyncio import Semaphore, gather
from contextlib import suppress
from datetime import timedelta
from typing import Literal, cast, final

from discord import Forbidden, Guild, Message, Role
from discord.abc import GuildChannel
from discord.utils import format_dt, utcnow

from bot import Cordex
from bot.ui import LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_BLACK, CONTESTED_EMOJI
from core.paginator import UnnamedPaginator
from core.utilities import format_now, format_table

from .cases import (
    BanAddPayload,
    BanRemovePayload,
    KickPayload,
    PurgePayload,
    QuarantineAddPayload,
    QuarantineRemovePayload,
    TimeoutAddPayload,
    TimeoutRemovePayload,
)

type ActionType = Literal[
    "Ban Add",
    "Ban Remove",
    "Kick",
    "Quarantine Add",
    "Quarantine Remove",
    "Timeout Add",
    "Timeout Remove",
    "Purge",
]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Actions Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class Actions:
    def __init__(self, bot : Cordex, guild : Guild) -> None:
        super().__init__()
        self.bot   = bot
        self.guild = guild

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_quarantine_role
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_quarantine_role(self) -> Role | None:
        async with self.bot.db.execute(
            t"SELECT config_value FROM GuildConfig WHERE guild_id = {self.guild.id} AND config_key = {"quarantine_role"}",
        ) as cursor:
            res = await cursor.fetchone()

        if not res:
            return None

        if role_id := cast("int | None", res[0]) is None:
            return None

        return self.guild.get_role(role_id)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_enforce
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    type EnforceTypes = Literal["Channel", "Role"]

    async def quarantine_enforce(self, enforce_type : EnforceTypes) -> None:
        quarantine_role = await self.get_quarantine_role()

        if not quarantine_role:
            return

        if enforce_type == "Channel":
            semaphore = Semaphore(5)

            async def edit_channel(channel : GuildChannel) -> None:
                async with semaphore:
                    with suppress(Forbidden):
                        overwrites = channel.overwrites_for(quarantine_role)

                        overwrites.send_messages_in_threads = False
                        overwrites.create_instant_invite    = False
                        overwrites.send_messages            = False
                        overwrites.create_public_threads    = False
                        overwrites.create_private_threads   = False
                        overwrites.read_messages            = False

                        await channel.set_permissions(
                            quarantine_role,
                            overwrite = overwrites,
                            reason    = "Scheduled quarantine enforce.",
                        )

            await gather(*(edit_channel(c) for c in self.guild.channels))

        if enforce_type == "Role":
            my_role = self.guild.self_role or self.guild.me.top_role

            with suppress(Forbidden):
                await quarantine_role.edit(position = my_role.position - 1)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # _dm_target
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def _dm_target(
        self,
        action_type : ActionType,
        action      : (
            BanAddPayload
            | BanRemovePayload
            | KickPayload
            | QuarantineAddPayload
            | QuarantineRemovePayload
            | TimeoutAddPayload
            | TimeoutRemovePayload
        ),
    ) -> None:
        moderator = action.moderator
        target    = action.target

        guild_name = f"'{self.guild.name}'"

        type_map : dict[str, str] = {
            "Ban Add"           : f"# {CONTESTED_EMOJI} You have been banned in the server {guild_name}.",
            "Ban Remove"        : f"# {CONTESTED_EMOJI} You have been un-banned the server {guild_name}.",
            "Kick"              : f"# {CONTESTED_EMOJI} You have been kicked from the server {guild_name}.",
            "Quarantine Add"    : f"# {CONTESTED_EMOJI} You have been placed in quarantine in the server {guild_name}.",
            "Quarantine Remove" : f"# {CONTESTED_EMOJI} You have been removed from quarantine in the server {guild_name}.",
            "Timeout Add"       : f"# {CONTESTED_EMOJI} You have been placed in timeout in the server {guild_name}.",
            "Timeout Remove"    : f"# {CONTESTED_EMOJI} You have been removed from timeout in the server {guild_name}.",
        }

        title  = type_map[action_type]
        length = getattr(action, "length", None)

        line = ""
        if isinstance(length, int):
            end_time = utcnow() + timedelta(seconds = length)
            line = f"-# This action will be undone {format_dt(end_time, style = "F")} | {format_dt(end_time, style = "R")}."

        view = LayoutView()
        view.add_items(
            TextDisplay[LayoutView](
                (
                    f"{title}\n"
                    f"-# You were moderated in the server {guild_name} by at {format_now()}!\n"
                ),
            ),
            VisibleLargeSeparator[LayoutView](),
            TextDisplay[LayoutView](
                (
                    f"{
                        format_table(
                            {
                                "Moderator" : f"{moderator.mention} | {moderator.id}",
                                "Reason"    : action.reason,
                            }
                        )
                    }\n\n"
                    f"{line}"
                ),
            ),
        )

        await target.send(view = view)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # lockdown_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def lockdown_add(self) -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # lockdown_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def lockdown_remove(self) -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # ban_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def ban_add(self, action : BanAddPayload) -> None:
        if action.dm_user:
            await self._dm_target("Ban Add", action)

        await action.target.ban(
            reason                 = f"Banned by {action.moderator.name}: {action.reason}",
            delete_message_seconds = 86400,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # ban_view
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def ban_view(self) -> UnnamedPaginator:
        class BanPaginator(UnnamedPaginator):
            def __init__(self) -> None:
                super().__init__(
                    "# Server Bans",
                    [],
                    data_name = "Bans",
                    per_page  = 10,
                    color     = COLOR_BLACK,
                    container = True,
                )

        return BanPaginator()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # ban_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def ban_remove(self, action : BanRemovePayload) -> None:
        if action.dm_user:
            await self._dm_target("Ban Remove", action)

        await self.guild.unban(action.target, reason = f"Unbanned by {action.moderator.name}: {action.reason}")

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # kick
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def kick(self, action : KickPayload) -> None:
        if action.dm_user:
            await self._dm_target("Kick", action)

        await action.target.kick(reason = f"Kicked by {action.moderator.name}: {action.reason}")

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    """
    async def quarantine_add(self, action : QuarantineAddPayload) -> None:
        quarantine_role = guild.get_role(QUARANTINE_ROLE_ID)
        if quarantine_role:
            await action.target.add_roles(quarantine_role)

        if action.dm_user:
            await self._dm_target("Quarantine Add", action)
    """

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_view
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def quarantine_view(self) -> UnnamedPaginator:
        class QuarantinePaginator(UnnamedPaginator):
            def __init__(self) -> None:
                super().__init__(
                    "# Server Quarantines",
                    [],
                    data_name = "Quarantines",
                    per_page  = 10,
                    color     = COLOR_BLACK,
                    container = True,
                )

        return QuarantinePaginator()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    """
    async def quarantine_remove(self, action : QuarantineRemovePayload) -> None:
        quarantine_role = guild.get_role(QUARANTINE_ROLE_ID)
        if quarantine_role:
            await action.target.remove_roles(quarantine_role)

        if action.dm_user:
            await self._dm_target("Quarantine Remove", action)
    """

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def timeout_add(self, action : TimeoutAddPayload) -> None:
        await action.target.edit(
            timed_out_until = utcnow() + timedelta(seconds = action.length),
            reason          = f"Timed out by {action.moderator.name}: {action.reason}",
        )

        if action.dm_user:
            await self._dm_target("Timeout Add", action)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_view
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def timeout_view(self) -> UnnamedPaginator:
        class TimeoutPaginator(UnnamedPaginator):
            def __init__(self) -> None:
                super().__init__(
                    "# Server Timeouts",
                    [],
                    data_name = "Timeouts",
                    per_page  = 10,
                    color     = COLOR_BLACK,
                    container = True,
                )

        return TimeoutPaginator()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def timeout_remove(self, action : TimeoutRemovePayload) -> None:
        await action.target.edit(
            timed_out_until = None,
            reason          = f"Untimed out by {action.moderator.name}: {action.reason}",
        )

        if action.dm_user:
            await self._dm_target("Timeout Remove", action)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # purge
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def purge(self, action : PurgePayload) -> list[Message]:
        target  = action.target
        channel = action.channel
        amount  = action.amount

        if not target:
            deleted = await channel.purge(limit = amount)
        elif not action.force:
            deleted = await channel.purge(
                limit = amount,
                check = lambda msg : msg.author == target,
            )
        else:
            messages : list[Message] = []

            async for message in channel.history(limit = 2000):
                if message.author == target:
                    messages.append(message)
                    if len(messages) == amount:
                        break

            if messages:
                message_set = set(messages)
                deleted     = await channel.purge(
                    limit = 2000,
                    check = lambda msg : msg in message_set,
                )
            else:
                deleted = []

        return deleted
