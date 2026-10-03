from dataclasses import dataclass
from datetime import timedelta
from typing import Literal, cast, final

from discord import Forbidden, Guild, HTTPException, Message, Role
from discord.utils import format_dt, utcnow

from bot import Cordex, log
from bot.ui import LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_BLACK, COLOR_ORANGE, COLOR_YELLOW, WARNING_EMOJI
from core.paginator import UnnamedPaginator
from core.utilities import format_now, format_table

from .cases import CasesManager
from .payloads import (
    BanAddPayload,
    BanRemovePayload,
    KickPayload,
    LockdownAddPayload,
    LockdownRemovePayload,
    PurgePayload,
    QuarantineAddPayload,
    QuarantineRemovePayload,
    TimeoutAddPayload,
    TimeoutRemovePayload,
)

type ActionType = Literal[
    "Lockdown Add",
    "Lockdown Remove",
    "Ban Add",
    "Ban Remove",
    "Kick",
    "Quarantine Add",
    "Quarantine Remove",
    "Timeout Add",
    "Timeout Remove",
    "Purge",
]


@dataclass(frozen = True, slots = True)
class _ActionResult[T = None]:
    failed  : bool
    logged  : bool
    dmed    : bool | None
    data    : T    | None = None

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Actions
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class Actions:
    """
    A class for executing moderation actions.

    Parameters
    ----------
    bot : `Cordex`
        The bot instance.
    guild : `Guild`
        The guild in which moderation actions are being executed.
    """

    __slots__ = ("bot", "cases", "config", "guild")

    def __init__(self, bot : Cordex, guild : Guild) -> None:
        super().__init__()
        self.bot    = bot
        self.guild  = guild
        self.config = self.bot.config(guild)

        self.cases = CasesManager(bot, guild)

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
            "Ban Add"           : f"# {WARNING_EMOJI} You have been banned in the server {guild_name}.",
            "Ban Remove"        : f"# {WARNING_EMOJI} You have been un-banned from the server {guild_name}.",
            "Kick"              : f"# {WARNING_EMOJI} You have been kicked from the server {guild_name}.",
            "Quarantine Add"    : f"# {WARNING_EMOJI} You have been placed in quarantine in the server {guild_name}.",
            "Quarantine Remove" : f"# {WARNING_EMOJI} You have been removed from quarantine in the server {guild_name}.",
            "Timeout Add"       : f"# {WARNING_EMOJI} You have been placed in timeout in the server {guild_name}.",
            "Timeout Remove"    : f"# {WARNING_EMOJI} You have been removed from timeout in the server {guild_name}.",
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
                f"-# You were moderated at {format_now()}!\n",
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

    async def lockdown_add(self, action : LockdownAddPayload, /) -> _ActionResult:
        """
        Place a channel in lockdown.

        Parameters
        ----------
        action : `LockdownAddPayload`
            The data associated with the lockdown addition.

        Returns
        -------
        `ActionResult`
            The result of the lockdown addition.
        """
        channel   = action.channel
        everyone  = self.guild.default_role
        overwrite = channel.overwrites_for(everyone)

        try:
            await self.bot.db.execute(
                t"INSERT INTO Lockdowns (channel_id, guild_id) VALUES ({channel.id}, {self.guild.id}) "
                t"ON CONFLICT (channel_id, guild_id) DO NOTHING",
            )
            await self.bot.db.commit()

            overwrite.send_messages = False
            await channel.set_permissions(
                everyone,
                overwrite = overwrite,
                reason    = f"Locked down by {action.moderator.name}: {action.reason}",
            )
        except Forbidden:
            failed = True
        except HTTPException:
            failed = True
            self._log_failure("lockdown add")
        else:
            failed = False

        case = await self.cases.create_case(action)

        return _ActionResult(
            failed = failed,
            logged = case.successful,
            dmed   = None,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # lockdown_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def lockdown_remove(self, action : LockdownRemovePayload, /) -> _ActionResult:
        """
        Remove a channel from lockdown.

        Parameters
        ----------
        action : `LockdownRemovePayload`
            The data associated with the lockdown removal.

        Returns
        -------
        `ActionResult`
            The result of the lockdown removal.
        """
        channel  = action.channel
        everyone = self.guild.default_role

        await self.bot.db.execute(
            t"DELETE FROM Lockdowns WHERE channel_id = {channel.id} AND guild_id = {self.guild.id}",
        )
        await self.bot.db.commit()

        try:
            overwrite = channel.overwrites_for(everyone)
            overwrite.send_messages = None

            await channel.set_permissions(
                everyone,
                overwrite = overwrite,
                reason    = f"Unlocked by {action.moderator.name}: {action.reason}",
            )
        except Forbidden:
            failed = True
        except HTTPException:
            failed = True
            self._log_failure("lockdown removal")
        else:
            failed = False

        case = await self.cases.create_case(action)

        return _ActionResult(
            failed = failed,
            logged = case.successful,
            dmed   = None,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # ban_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def ban_add(self, action : BanAddPayload, /) -> _ActionResult:
        """
        Ban a member from the server.

        Parameters
        ----------
        action : `BanAddPayload`
            The data associated with the ban addition.

        Returns
        -------
        `ActionResult`
            The result of the ban addition.
        """
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

        case = await self.cases.create_case(action)

        return _ActionResult(
            failed = failed,
            logged = case.successful,
            dmed   = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # ban_view
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def ban_view(self) -> UnnamedPaginator:
        """
        Display a paginator (`UnnamedPaginator`) of all server bans.

        Returns
        -------
        `BanPaginator`
            The paginator displaying all server bans.
        """
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

    async def ban_remove(self, action : BanRemovePayload, /) -> _ActionResult:
        """
        Remove a ban from a member.

        Parameters
        ----------
        action : `BanRemovePayload`
            The data associated with the ban removal.

        Returns
        -------
        `ActionResult`
            The result of the ban removal.
        """
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

        case = await self.cases.create_case(action)

        return _ActionResult(
            failed = failed,
            logged = case.successful,
            dmed   = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # kick
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def kick(self, action : KickPayload, /) -> _ActionResult:
        """
        Kick a member from the server.

        Parameters
        ----------
        action : `KickPayload`
            The data associated with the kick.

        Returns
        -------
        `ActionResult`
            The result of the kick.
        """
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

        case = await self.cases.create_case(action)

        return _ActionResult(
            failed = failed,
            logged = case.successful,
            dmed   = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def quarantine_add(self, action : QuarantineAddPayload, /) -> _ActionResult:
        """
        Place a member in quarantine.

        Parameters
        ----------
        action : `QuarantineAddPayload`
            The data associated with the quarantine addition.

        Returns
        -------
        `ActionResult`
            The result of the quarantine addition.
        """
        quarantine_role = await self.config.get_moderation_quarantine_role()
        if not quarantine_role:
            return _ActionResult(
                failed = True,
                logged = False,
                dmed   = False,
            )

        if action.dm_user:
            success = await self._dm_target("Quarantine Add", action)
        else:
            success = None

        try:
            current_roles = [role for role in action.target.roles if not role.is_default()]
            roles_str     = ",".join(str(role.id) for role in current_roles)

            await self.bot.db.execute(
                t"INSERT INTO Quarantines (member_id, guild_id, old_roles) VALUES ({action.target.id}, {action.target.guild.id}, {roles_str}) "
                t"ON CONFLICT (member_id, guild_id) DO UPDATE SET old_roles = excluded.old_roles",
            )
            await self.bot.db.commit()

            await action.target.edit(
                roles  = [quarantine_role],
                reason = f"Quarantined by {action.moderator.name}: {action.reason}",
            )
        except Forbidden:
            failed = True
        except HTTPException:
            failed = True
            self._log_failure("quarantine add")
        else:
            failed = False

        case = await self.cases.create_case(action)

        return _ActionResult(
            failed = failed,
            logged = case.successful,
            dmed   = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_view
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def quarantine_view(self) -> UnnamedPaginator:
        """
        Display a paginator (`UnnamedPaginator`) of all members in quarantine.

        Returns
        -------
        `QuarantinePaginator`
            The paginator displaying all members in quarantine.
        """
        class QuarantinePaginator(UnnamedPaginator):
            def __init__(self) -> None:
                super().__init__(
                    "# Server Quarantines",
                    [],
                    data_name = "Quarantines",
                    per_page  = 10,
                    color     = COLOR_ORANGE,
                    container = True,
                )

        return QuarantinePaginator()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def quarantine_remove(self, action : QuarantineRemovePayload, /) -> _ActionResult:
        """
        Remove a member from quarantine.

        Parameters
        ----------
        action : `QuarantineRemovePayload`
            The data associated with the quarantine removal.

        Returns
        -------
        `ActionResult`
            The result of the quarantine removal.
        """
        quarantine_role = await self.config.get_moderation_quarantine_role()
        if not quarantine_role:
            return _ActionResult(
                failed = True,
                logged = False,
                dmed   = False,
            )

        if action.dm_user:
            success = await self._dm_target("Quarantine Remove", action)
        else:
            success = None

        async with self.bot.db.execute(
            t"SELECT old_roles FROM Quarantines WHERE member_id = {action.target.id} AND guild_id = {action.target.guild.id}",
        ) as cursor:
            res = await cursor.fetchone()

        roles : list[Role] | None = None
        if res:
            roles_str = cast("str", res[0])
            await self.bot.db.execute(
                t"DELETE FROM Quarantines WHERE member_id = {action.target.id} AND guild_id = {action.target.guild.id}",
            )
            await self.bot.db.commit()

            roles = []
            for role_id_str in roles_str.split(","):
                if role_id_str:
                    role = action.target.guild.get_role(int(role_id_str))
                    if role:
                        roles.append(role)

        try:
            if roles is not None:
                await action.target.edit(
                    roles  = roles,
                    reason = f"Unquarantined by {action.moderator.name}: {action.reason}",
                )
            else:
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

        case = await self.cases.create_case(action)

        return _ActionResult(
            failed = failed,
            logged = case.successful,
            dmed   = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def timeout_add(self, action : TimeoutAddPayload, /) -> _ActionResult:
        """
        Place a member in timeout.

        Parameters
        ----------
        action : `TimeoutAddPayload`
            The data associated with the timeout addition.
        /

        Returns
        -------
        `ActionResult`
            The result of the timeout addition.
        """
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

        case = await self.cases.create_case(action)

        return _ActionResult(
            failed = failed,
            logged = case.successful,
            dmed   = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_view
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def timeout_view(self) -> UnnamedPaginator:
        """
        Display a paginator (`UnnamedPaginator`) of all members in timeout.

        Returns
        -------
        `TimeoutPaginator`
            The paginator displaying all members in timeout.
        """
        class TimeoutPaginator(UnnamedPaginator):
            def __init__(self) -> None:
                super().__init__(
                    "# Server Timeouts",
                    [],
                    data_name = "Timeouts",
                    per_page  = 10,
                    color     = COLOR_YELLOW,
                    container = True,
                )

        return TimeoutPaginator()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def timeout_remove(self, action : TimeoutRemovePayload, /) -> _ActionResult:
        """
        Remove a member from timeout.

        Parameters
        ----------
        action : `TimeoutRemovePayload`
            The data associated with the timeout removal.
        /

        Returns
        -------
        `ActionResult`
            The result of the timeout removal.
        """
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

        case = await self.cases.create_case(action)

        return _ActionResult(
            failed = failed,
            logged = case.successful,
            dmed   = success,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # purge
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def purge(self, action : PurgePayload, /) -> _ActionResult[int]:
        """
        Purge messages.

        Parameters
        ----------
        action : `PurgePayload`
            The data associated with the purge.
        /

        Returns
        -------
        `ActionResult`
            The result of the purge.
        """
        target  = action.target
        reason  = action.reason
        channel = action.channel
        amount  = action.amount

        # ⸻ Helper.

        async def _purge() -> list[Message]:
            if not target:
                return await channel.purge(limit = amount, reason = reason)

            return await channel.purge(
                limit  = 1000 if action.force else amount,
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

        case = await self.cases.create_case(action)

        return _ActionResult(
            failed = failed,
            logged = case.successful,
            dmed   = None,
            data   = len(deleted),
        )
