from discord import Member

from bot import Interaction
from commands.moderation.primary._base import send_moderation_modal
from core.moderation import ActionType

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation quarantine remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_mod_primary_quarantine_remove(interaction : Interaction, target : Member) -> None:
    """
    Remove a member from quarantine.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    target : `Member`
        The member to remove from quarantine.
    """
    await send_moderation_modal(interaction, ActionType.quarantine_remove, target)
