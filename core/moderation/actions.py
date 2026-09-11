from dataclasses import dataclass
from datetime import timedelta
from typing import Literal, final

from discord import Forbidden, Guild, HTTPException, Member, Message
from discord.utils import format_dt, utcnow

from bot import Cordex, log
from bot.ui import LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_BLACK, CONTESTED_EMOJI
from core.paginator import UnnamedPaginator
from core.utilities import format_now, format_table

from .cases import (
    BanAddPayload,
    BanRemovePayload,
    Cases,
    KickPayload,
    LockdownAddPayload,
    LockdownRemovePayload,
    NoteAddPayload,
    NoteEditPayload,
    NoteRemovePayload,
    PurgePayload,
    QuarantineAddPayload,
    QuarantineRemovePayload,
    TimeoutAddPayload,
    TimeoutRemovePayload,
)
from .managers import LockdownManager, QuarantineManager

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
    # logged  : bool
    dmed    : bool | None
    data    : T    | None = None

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Actions
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class Actions:
    def __init__(self, bot : Cordex, guild : Guild) -> None:
        super().__init__()
        self.bot    = bot
        self.guild  = guild
        self.config = self.bot.config(guild)

        self._cases              = Cases(bot, guild)
        self._lockdown_manager   = LockdownManager(bot, guild)
        self._quarantine_manager = QuarantineManager(bot, guild)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # _log_failure
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def _log_failure(self, msg : str, /) -> None:
        log.exception("Failure during %s in guild %s, %s", msg, self.guild.name, self.guild.id)

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

    async def lockdown_add(self, _action : LockdownAddPayload) -> ActionResult:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # lockdown_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def lockdown_remove(self, _action : LockdownRemovePayload) -> ActionResult:
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
            self._log_failure("ban add")
        else:
            failed = False

        return ActionResult(
            failed = failed,
            dmed   = success,
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
            self._log_failure("ban removal")
        else:
            failed = False

        return ActionResult(
            failed = failed,
            dmed   = success,
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
            self._log_failure("kick")
        else:
            failed = False

        return ActionResult(
            failed = failed,
            dmed   = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def quarantine_add(self, action : QuarantineAddPayload) -> ActionResult:
        quarantine_role = await self.config.get_moderation_quarantine_role()
        if not quarantine_role:
            return ActionResult(
                failed = True,
                dmed   = False,
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
            self._log_failure("quarantine add")
        else:
            failed = False

        return ActionResult(
            failed = failed,
            dmed   = success,
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
        quarantine_role = await self.config.get_moderation_quarantine_role()
        if not quarantine_role:
            return ActionResult(
                failed = True,
                dmed   = False,
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
            self._log_failure("quarantine removal")
        else:
            failed = False

        return ActionResult(
            failed = failed,
            dmed   = success,
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
            self._log_failure("timeout add")
        else:
            failed = False

        return ActionResult(
            failed = failed,
            dmed   = success,
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
            self._log_failure("timeout removal")
        else:
            failed = False

        return ActionResult(
            failed = failed,
            dmed   = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # purge
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def purge(self, action : PurgePayload) -> ActionResult[int]:
        target  = action.target
        reason  = action.reason
        channel = action.channel
        amount  = action.amount

        # ⸻ Helper.

        async def _purge() -> list[Message]:
            if not target:
                return await channel.purge(limit = amount, reason = reason)

            limit = 1000 if action.force else amount
            return await channel.purge(
                limit  = limit,
                check  = lambda m : m.author == target,
                reason = reason,
            )

        # ⸻ Logic.

        try:
            deleted = await _purge()
        except Forbidden, HTTPException:
            failed  = True
            deleted = []
            self._log_failure("purge")
        else:
            failed = False

        return ActionResult(
            failed = failed,
            dmed   = None,
            data   = len(deleted),
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
