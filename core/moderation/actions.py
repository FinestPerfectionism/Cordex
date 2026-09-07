from asyncio import Semaphore, gather
from dataclasses import dataclass
from datetime import timedelta
from typing import Literal, cast, final

from discord import Forbidden, Guild, HTTPException, Member, Message, Role
from discord.abc import GuildChannel
from discord.utils import format_dt, utcnow

from bot import Cordex, log
from bot.ui import LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_BLACK, CONTESTED_EMOJI
from core.paginator import UnnamedPaginator
from core.utilities import format_now, format_table

from .cases import (
    BanAddPayload,
    BanRemovePayload,
    KickPayload,
    NoteAddPayload,
    NoteEditPayload,
    NoteRemovePayload,
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

@dataclass(frozen = True)
class ActionResult[T = None]:
    failed  : bool
    dm_sent : bool | None
    data    : T    | None = None

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Actions Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ruff: disable[too-many-public-methods]
@final
class Actions:
    def __init__(self, bot : Cordex, guild : Guild) -> None:
        super().__init__()
        self.bot   = bot
        self.guild = guild

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_quarantined_members
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_quarantined_members(self) -> list[Member] | None:
        ...

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

        role_id = cast("int | None", res[0])
        if role_id is None:
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
                    overwrites = channel.overwrites_for(quarantine_role)

                    overwrites.update(
                        send_messages_in_threads = False,
                        create_instant_invite    = False,
                        send_messages            = False,
                        create_public_threads    = False,
                        create_private_threads   = False,
                        read_messages            = False,
                    )

                    try:
                        await channel.set_permissions(
                            quarantine_role,
                            overwrite = overwrites,
                            reason    = "Scheduled quarantine enforce.",
                        )
                    except Forbidden:
                        pass
                    except HTTPException:
                        log.exception("Failure during quarantine enforcement in guild %s, %s — Channel", self.guild.name, self.guild.id)

            await gather(*(edit_channel(channel) for channel in self.guild.channels))

        if enforce_type == "Role":
            me = self.guild.me
            if not me or not me.guild_permissions.manage_roles:
                return

            my_role = me.top_role
            if my_role.position > 1 and quarantine_role.position != my_role.position - 1:
                try:
                    await quarantine_role.edit(position = my_role.position - 1)
                except Forbidden:
                    pass
                except HTTPException:
                    log.exception("Failure during quarantine enforcement in guild %s, %s — Role", self.guild.name, self.guild.id)

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
    ) -> bool:
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
                f"{title}\n"
                f"-# You were moderated in the server {guild_name} by at {format_now()}!\n",
            ),
            VisibleLargeSeparator[LayoutView](),
            TextDisplay[LayoutView](
                f"{
                    format_table(
                        {
                            "Moderator" : f"{moderator.mention} | {moderator.id}",
                            "Reason"    : action.reason,
                        }
                    )
                }\n\n"
                f"{line}",
            ),
        )

        try:
            await target.send(view = view)
        except Forbidden, HTTPException:
            return False
        else:
            return True

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # lockdown_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def lockdown_add(self) -> ActionResult:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # lockdown_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def lockdown_remove(self) -> ActionResult:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # ban_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def ban_add(self, action : BanAddPayload) -> ActionResult:
        if action.dm_user:
            success = await self._dm_target("Ban Add", action)
        else:
            success = None

        try:
            await action.target.ban(
                reason                 = f"Banned by {action.moderator.name}: {action.reason}",
                delete_message_seconds = action.seconds_to_delete,
            )
        except Forbidden:
            failed = True
        except HTTPException:
            failed = True
            log.exception("Failure during ban add in guild %s, %s", self.guild.name, self.guild.id)
        else:
            failed = False

        return ActionResult(
            failed  = failed,
            dm_sent = success,
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

    async def ban_remove(self, action : BanRemovePayload) -> ActionResult:
        if action.dm_user:
            success = await self._dm_target("Ban Remove", action)
        else:
            success = None

        try:
            await self.guild.unban(
                action.target,
                reason = f"Unbanned by {action.moderator.name}: {action.reason}",
            )
        except Forbidden:
            failed = True
        except HTTPException:
            failed = True
            log.exception("Failure during ban removal in guild %s, %s", self.guild.name, self.guild.id)
        else:
            failed = False

        return ActionResult(
            failed  = failed,
            dm_sent = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # kick
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def kick(self, action : KickPayload) -> ActionResult:
        if action.dm_user:
            success = await self._dm_target("Kick", action)
        else:
            success = None

        try:
            await self.guild.kick(
                action.target,
                reason = f"Kicked by {action.moderator.name}: {action.reason}",
            )
        except Forbidden:
            failed = True
        except HTTPException:
            failed = True
            log.exception("Failure during kick in guild %s, %s", self.guild.name, self.guild.id)
        else:
            failed = False

        return ActionResult(
            failed  = failed,
            dm_sent = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def quarantine_add(self, action : QuarantineAddPayload) -> ActionResult:
        quarantine_role = await self.get_quarantine_role()
        if not quarantine_role:
            return ActionResult(
                failed  = True,
                dm_sent = False,
            )

        if action.dm_user:
            success = await self._dm_target("Quarantine Add", action)
        else:
            success = None

        try:
            await action.target.add_roles(
                quarantine_role,
                reason = f"Quarantined by {action.moderator.name}: {action.reason}",
            )
        except Forbidden:
            failed = True
        except HTTPException:
            failed = True
            log.exception("Failure during quarantine add in guild %s, %s", self.guild.name, self.guild.id)
        else:
            failed = False

        return ActionResult(
            failed  = failed,
            dm_sent = success,
        )

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

    async def quarantine_remove(self, action : QuarantineRemovePayload) -> ActionResult:
        quarantine_role = await self.get_quarantine_role()
        if not quarantine_role:
            return ActionResult(
                failed  = True,
                dm_sent = False,
            )

        if action.dm_user:
            success = await self._dm_target("Quarantine Remove", action)
        else:
            success = None

        try:
            await action.target.remove_roles(
                quarantine_role,
                reason = f"Unquarantined by {action.moderator.name}: {action.reason}",
            )
        except Forbidden:
            failed = True
        except HTTPException:
            failed = True
            log.exception("Failure during quarantine removal in guild %s, %s", self.guild.name, self.guild.id)
        else:
            failed = False

        return ActionResult(
            failed  = failed,
            dm_sent = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def timeout_add(self, action : TimeoutAddPayload) -> ActionResult:
        if action.dm_user:
            success = await self._dm_target("Timeout Add", action)
        else:
            success = None

        try:
            await action.target.edit(
                timed_out_until = utcnow() + timedelta(seconds = action.length),
                reason          = f"Timed out by {action.moderator.name}: {action.reason}",
            )
        except Forbidden:
            failed = True
        except HTTPException:
            failed = True
            log.exception("Failure during timeout add in guild %s, %s", self.guild.name, self.guild.id)
        else:
            failed = False

        return ActionResult(
            failed  = failed,
            dm_sent = success,
        )

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

    async def timeout_remove(self, action : TimeoutRemovePayload) -> ActionResult:
        if action.dm_user:
            success = await self._dm_target("Timeout Remove", action)
        else:
            success = None

        try:
            await action.target.edit(
                timed_out_until = None,
                reason          = f"Untimed out by {action.moderator.name}: {action.reason}",
            )
        except Forbidden:
            failed = True
        except HTTPException:
            failed = True
            log.exception("Failure during timeout removal in guild %s, %s", self.guild.name, self.guild.id)
        else:
            failed = False

        return ActionResult(
            failed  = failed,
            dm_sent = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # purge
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def purge(self, action : PurgePayload) -> ActionResult[int]:
        target  = action.target
        channel = action.channel
        amount  = action.amount

        # ⸻ Helper.

        async def _purge() -> list[Message]:
            if not target:
                return await channel.purge(limit = amount)

            limit = 1000 if action.force else amount
            return await channel.purge(
                limit = limit,
                check = lambda m : m.author == target,
            )

        # ⸻ Logic.

        try:
            deleted = await _purge()
        except Forbidden, HTTPException:
            failed  = True
            deleted = []
            log.exception("Failure during purge in guild %s, %s", self.guild.name, self.guild.id)
        else:
            failed = False

        return ActionResult(
            failed  = failed,
            dm_sent = None,
            data    = len(deleted),
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # note_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def note_add(self, _action : NoteAddPayload) -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # note_edit
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def note_edit(self, _action : NoteEditPayload) -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # note_view
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def note_view(self, _action : Member)  -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # note_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def note_remove(self, _action : NoteRemovePayload) -> None:
        ...

# ruff: enable[too-many-public-methods]
