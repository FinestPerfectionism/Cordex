from discord import Member

from bot import Interaction
from commands.moderation.primary._base import send_moderation_modal
from core.moderation import ActionType

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation ban add Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_mod_primary_ban_add(interaction : Interaction, target : Member) -> None:
    """
    Ban a member from the server.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    target : `Member`
        The member to ban.
    """
    await send_moderation_modal(interaction, ActionType.ban_add, target)
