from discord import Member

from bot import Interaction
from commands.moderation.primary._base import send_moderation_modal
from core.moderation import ActionType

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation timeout remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_mod_primary_timeout_remove(interaction : Interaction, target : Member) -> None:
    """
    Remove a member from timeout.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    target : `Member`
        The member to remove from timeout.
    """
    await send_moderation_modal(interaction, ActionType.timeout_remove, target)
