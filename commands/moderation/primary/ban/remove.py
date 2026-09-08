from discord import NotFound, User

from bot import Interaction
from commands.moderation.primary._base import send_moderation_modal
from core.exceptions import send_bad_argument

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation ban remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_mod_primary_ban_remove(interaction : Interaction, target : User) -> None:
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

    await send_moderation_modal(interaction, "Ban Remove", target)
