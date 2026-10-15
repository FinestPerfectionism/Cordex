from discord import Member

from bot import Interaction
from core.moderation import ActionType

from ._base import send_moderation_modal

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation kick Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_moderation_kick(interaction : Interaction, target : Member) -> None:
    """
    Kick a member from the server.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    target : `Member`
        The member to kick.
    """
    await send_moderation_modal(interaction, ActionType.kick, target)
