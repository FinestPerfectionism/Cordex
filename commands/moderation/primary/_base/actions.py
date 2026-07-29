from datetime import timedelta
from typing import Literal, final

from discord import Member
from discord.utils import utcnow

from bot import Interaction, bot
from bot.ui import Button, View, button
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


@final
class _AppealableView(View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @button(label = "Appeal")
    async def btn_appeal(self, interaction : Interaction, _button : Button[View]) -> None:
        await interaction.response.send_message("This button does nothing right now. :[")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Actions Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class BaseActions:
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    async def _dm_target(
        cls,
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

        title = type_map[action_type]

        table_data : dict[str, str] = {"Reason" : action.reason}

        length : object | None = getattr(action, "length", None)
        if length is not None:
            table_data["Length"]    = str(length)
            table_data["Moderator"] = f"{moderator.mention} | {moderator.id}"

        content = (
            f"{title}\n"
            f"{action.reason}"
        )

        if hasattr(action, "appealable"):
            await target.send(content, view = _AppealableView())
        else:
            await target.send(content)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # lockdown_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def lockdown_add(cls) -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # lockdown_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def lockdown_remove(cls) -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # ban_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def ban_add(cls, targets : list[BanAddPayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target

            try:
                if action.dm_user:
                    await cls._dm_target("Ban Add", action)

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

    @classmethod
    async def ban_view(cls) -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # ban_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def ban_remove(cls, targets : list[BanRemovePayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target
            guild  = bot.get_guild(MAIN_GUILD_ID)

            try:
                if action.dm_user:
                    await cls._dm_target("Ban Remove", action)

                if guild is not None:
                    await guild.unban(target, reason = action.reason)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # kick
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def kick(cls, targets : list[KickPayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target

            try:
                if action.dm_user:
                    await cls._dm_target("Kick", action)

                await target.kick(reason = action.reason)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def quarantine_add(cls, targets : list[QuarantineAddPayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target
            guild  = bot.get_guild(MAIN_GUILD_ID)

            try:
                if guild:
                    quarantine_role = guild.get_role(QUARANTINE_ROLE_ID)
                    if quarantine_role:
                        await target.add_roles(quarantine_role)

                if action.dm_user:
                    await cls._dm_target("Quarantine Add", action)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_view
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def quarantine_view(cls) -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def quarantine_remove(cls, targets : list[QuarantineRemovePayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target
            guild  = bot.get_guild(MAIN_GUILD_ID)

            try:
                if guild:
                    quarantine_role = guild.get_role(QUARANTINE_ROLE_ID)
                    if quarantine_role:
                        await target.remove_roles(quarantine_role)

                if action.dm_user:
                    await cls._dm_target("Quarantine Remove", action)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def timeout_add(cls, targets : list[TimeoutAddPayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target

            try:
                await target.edit(
                    timed_out_until = utcnow() + timedelta(seconds = action.length),
                    reason          = action.reason,
                )

                if action.dm_user:
                    await cls._dm_target("Timeout Add", action)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_view
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def timeout_view(cls) -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # timeout_remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def timeout_remove(cls, targets : list[TimeoutRemovePayload]) -> list[tuple[Member, str]]:
        errors : list[tuple[Member, str]] = []

        for action in targets:
            target = action.target

            try:
                await target.edit(timed_out_until = None, reason = action.reason)

                if action.dm_user:
                    await cls._dm_target("Timeout Remove", action)

            except Exception as error:
                errors.append((target, str(error)))

        return errors

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # purge
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @classmethod
    async def purge(cls) -> None:
        ...
