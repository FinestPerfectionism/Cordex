from discord import Member

from bot import Interaction

from .actions import ActionType
from .select import ModerationModal

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Utilites Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

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
