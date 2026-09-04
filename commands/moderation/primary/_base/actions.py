from datetime import timedelta
from typing import Literal, final

from discord import Guild, Message
from discord.utils import format_dt, utcnow

from bot import Cordex
from bot.ui import LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_BLACK, CONTESTED_EMOJI
from core.cases import (
    BanAddPayload,
    BanRemovePayload,
    KickPayload,
    PurgePayload,
    QuarantineAddPayload,
    QuarantineRemovePayload,
    TimeoutAddPayload,
    TimeoutRemovePayload,
)
from core.paginator import UnnamedPaginator
from core.utilities import format_now, format_table

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

        guild_name = self.guild.name

        type_map : dict[str, str] = {
            "Ban Add"           : f"# {CONTESTED_EMOJI} You have been banned in the server {guild_name} server.",
            "Ban Remove"        : f"# {CONTESTED_EMOJI} You have been un-banned the server {guild_name} server.",
            "Kick"              : f"# {CONTESTED_EMOJI} You have been kicked from the server {guild_name} server.",
            "Quarantine Add"    : f"# {CONTESTED_EMOJI} You have been placed in quarantine in the server {guild_name} server.",
            "Quarantine Remove" : f"# {CONTESTED_EMOJI} You have been removed from quarantine in the server {guild_name} server.",
            "Timeout Add"       : f"# {CONTESTED_EMOJI} You have been placed in timeout in the server {guild_name} server.",
            "Timeout Remove"    : f"# {CONTESTED_EMOJI} You have been removed from timeout in the server {guild_name} server.",
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

        guild = self.bot.get_guild(self.guild.id)
        if guild is not None:
            await guild.unban(action.target, reason = f"Unbanned by {action.moderator.name}: {action.reason}")

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
        guild = self.bot.get_guild(self.guild.id)
        if guild:
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
        guild = self.bot.get_guild(self.guild.id)
        if guild:
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
