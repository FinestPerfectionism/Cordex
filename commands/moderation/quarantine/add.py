from discord import Member

from bot import Interaction
from commands.moderation._base import send_moderation_modal
from core.moderation import ActionType

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation quarantine add Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_moderation_quarantine_add(interaction : Interaction, target : Member) -> None:
    """
    Add a member to quarantine.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    target : `Member`
        The member to place in quarantine.
    """
    await send_moderation_modal(interaction, ActionType.quarantine_add, target)
