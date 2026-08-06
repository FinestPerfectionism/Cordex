from datetime import timedelta
from typing import Literal, final

from discord import Member
from discord.utils import format_dt, utcnow

from bot import Cordex
from constants import CONTESTED_EMOJI, MAIN_GUILD_ID, QUARANTINE_ROLE_ID
from core.cases import (
    BanAddPayload,
    BanRemovePayload,
    KickPayload,
    QuarantineAddPayload,
    QuarantineRemovePayload,
    TimeoutAddPayload,
    TimeoutRemovePayload,
)
from core.utilities import format_table

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

        content = [
            (
                f"{title}\n"
                f"-# You were moderated in the goobers by at {format_dt(utcnow())}!\n"
                f"{
                    format_table(
                        {
                            "Moderator" : f"{moderator.mention} | {moderator.id}",
                            "Reason"    : action.reason,
                        }
                    )
                }"
            ),
        ]

        if isinstance(length, int):
            end_time = utcnow() + timedelta(seconds = length)
            content.append(f"\nThis action will be undone {format_dt(end_time, style = "F")} | {format_dt(end_time, style = "R")}.")

        await target.send("".join(content))

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
                    reason                 = action.reason,
                    delete_message_seconds = 86400,
                )

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # ban_view
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def ban_view(self) -> None:
        ...

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
                    await guild.unban(target, reason = action.reason)

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

                await target.kick(reason = action.reason)

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

    async def quarantine_view(self) -> None:
        ...

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
                    reason          = action.reason,
                )

                if action.dm_user:
                    await self._dm_target("Timeout Add", action)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_view
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def timeout_view(self) -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def timeout_remove(self, targets : list[TimeoutRemovePayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target

            try:
                await target.edit(timed_out_until = None, reason = action.reason)

                if action.dm_user:
                    await self._dm_target("Timeout Remove", action)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # purge
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def purge(self) -> None:
        ...
