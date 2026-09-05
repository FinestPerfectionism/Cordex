from collections.abc import Callable

from discord import Member
from discord.app_commands import CheckFailure, check

from bot import Interaction
from core.exceptions import BadEnvironmentGuild
from core.moderation import Actions, ActionType

from .select import ModerationModal

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Utilites Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class UnconfiguredQuarantine(CheckFailure):
    pass

def quarantine_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    async def predicate(interaction : Interaction) -> bool:
        if not interaction.guild:
            raise BadEnvironmentGuild

        actions = Actions(interaction.client, interaction.guild)

        if not await actions.get_quarantine_role():
            raise UnconfiguredQuarantine

        return True

    def decorator(func : F) -> F:
        check(predicate)(func)
        return func

    return decorator

async def send_moderation_modal(interaction : Interaction, action_type : ActionType, target : Member) -> None:
    modal_dict : dict[ActionType, ModerationModal] = {
        "Ban Add"           : ModerationModal("Ban Add",           target),
        "Ban Remove"        : ModerationModal("Ban Remove",        target),
        "Kick"              : ModerationModal("Kick",              target),
        "Quarantine Add"    : ModerationModal("Quarantine Add",    target),
        "Quarantine Remove" : ModerationModal("Quarantine Remove", target),
        "Timeout Add"       : ModerationModal("Timeout Add",       target),
        "Timeout Remove"    : ModerationModal("Timeout Remove",    target),
    }

    modal = modal_dict[action_type]

    await interaction.response.send_modal(modal)
