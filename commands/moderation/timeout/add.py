from discord import Member

from bot import Interaction
from commands.moderation._base import send_moderation_modal
from core.moderation import ActionType

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation timeout add Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_moderation_timeout_add(interaction : Interaction, target : Member) -> None:
    """
    Add a member to timeout.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    target : `Member`
        The member to place in timeout.
    """
    await send_moderation_modal(interaction, ActionType.timeout_add, target)
