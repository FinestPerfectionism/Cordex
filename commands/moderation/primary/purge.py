from discord import Member

from bot import Interaction
from bot.types import GuildMessagable
from core.moderation import ActionType

from ._base import send_moderation_modal

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation purge Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_mod_primary_purge(interaction : Interaction, target : Member | None = None) -> None:
    """
    Purge messages from a channel or member.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    target : `Member | None = None`
        The member to purge messages from.
    """
    if not isinstance(interaction.channel, GuildMessagable):
        return

    await send_moderation_modal(interaction, ActionType.purge, interaction.channel, target)
