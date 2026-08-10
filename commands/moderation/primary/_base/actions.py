from datetime import timedelta
from typing import Literal, final

from discord import Member
from discord.utils import format_dt, utcnow

from bot import Cordex
from bot.ui import LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_BLACK, CONTESTED_EMOJI, MAIN_GUILD_ID, QUARANTINE_ROLE_ID
from core.cases import (
    BanAddPayload,
    BanRemovePayload,
    KickPayload,
    QuarantineAddPayload,
    QuarantineRemovePayload,
    TimeoutAddPayload,
    TimeoutRemovePayload,
)
from core.paginator import UnnamedPaginator
from core.utilities import format_now, format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Actions Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class BaseActions:
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    async def _dm_target(
        self,
        action_type : Literal[
            "Ban Add",
            "Ban Remove",
            "Kick",
            "Quarantine Add",
            "Quarantine Remove",
            "Timeout Add",
            "Timeout Remove",
        ],
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

        type_map : dict[str, str] = {
            "Ban Add"           : f'# {CONTESTED_EMOJI} You have been banned in the "goobers" server.',
            "Ban Remove"        : f'# {CONTESTED_EMOJI} You have been un-banned the "goobers" server.',
            "Kick"              : f'# {CONTESTED_EMOJI} You have been kicked from the "goobers" server.',
            "Quarantine Add"    : f'# {CONTESTED_EMOJI} You have been placed in quarantine in the "goobers" server.',
            "Quarantine Remove" : f'# {CONTESTED_EMOJI} You have been removed from quarantine in the "goobers" server.',
            "Timeout Add"       : f'# {CONTESTED_EMOJI} You have been placed in timeout in the "goobers" server.',
            "Timeout Remove"    : f'# {CONTESTED_EMOJI} You have been removed from timeout in the "goobers" server.',
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
                    f"-# You were moderated in the goobers by at {format_now()}!\n"
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

    async def ban_add(self, targets : list[BanAddPayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target

            try:
                if action.dm_user:
                    await self._dm_target("Ban Add", action)

                await target.ban(
                    reason                 = f"Banned by {action.moderator.name}: {action.reason}",
                    delete_message_seconds = 86400,
                )

            except Exception as error:
                errors.append((target, str(error)))

        return errors

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

    async def ban_remove(self, targets : list[BanRemovePayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target
            guild  = self.bot.get_guild(MAIN_GUILD_ID)

            try:
                if action.dm_user:
                    await self._dm_target("Ban Remove", action)

                if guild is not None:
                    await guild.unban(target, reason = f"Unbanned by {action.moderator.name}: {action.reason}")

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # kick
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def kick(self, targets : list[KickPayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target

            try:
                if action.dm_user:
                    await self._dm_target("Kick", action)

                await target.kick(reason = f"Kicked by {action.moderator.name}: {action.reason}")

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def quarantine_add(self, targets : list[QuarantineAddPayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target
            guild  = self.bot.get_guild(MAIN_GUILD_ID)

            try:
                if guild:
                    quarantine_role = guild.get_role(QUARANTINE_ROLE_ID)
                    if quarantine_role:
                        await target.add_roles(quarantine_role)

                if action.dm_user:
                    await self._dm_target("Quarantine Add", action)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

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

    async def quarantine_remove(self, targets : list[QuarantineRemovePayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target
            guild  = self.bot.get_guild(MAIN_GUILD_ID)

            try:
                if guild:
                    quarantine_role = guild.get_role(QUARANTINE_ROLE_ID)
                    if quarantine_role:
                        await target.remove_roles(quarantine_role)

                if action.dm_user:
                    await self._dm_target("Quarantine Remove", action)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def timeout_add(self, targets : list[TimeoutAddPayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target

            try:
                await target.edit(
                    timed_out_until = utcnow() + timedelta(seconds = action.length),
                    reason          = f"Timed out by {action.moderator.name}: {action.reason}",
                )

                if action.dm_user:
                    await self._dm_target("Timeout Add", action)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

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

    async def timeout_remove(self, targets : list[TimeoutRemovePayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target

            try:
                await target.edit(timed_out_until = None, reason = f"Untimed out by {action.moderator.name}: {action.reason}")

                if action.dm_user:
                    await self._dm_target("Timeout Remove", action)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # purge
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def purge(self) -> None:

        # ~~~ TODO: Switch from raw /purge command logic to a proper BaseActions.purge call

        ...
