from discord import NotFound, User

from bot import Interaction
from commands.moderation._base import send_moderation_modal
from core.exceptions import send_bad_argument
from core.moderation import ActionType

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation ban remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_moderation_ban_remove(interaction : Interaction, target : User) -> None:
    """
    Remove a ban from a member.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    target : `User`
        The member to unban.
    """
    guild = interaction.guild
    if not guild:
        return

    # ⸻ Make sure that the target is actually banned.

    try:
        await guild.fetch_ban(target)
    except NotFound:
        await send_bad_argument(
            interaction,
            subtitle = {"target" : f"{target.mention} is not banned."},
        )
        return

    await send_moderation_modal(interaction, ActionType.ban_remove, target)
