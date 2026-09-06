from discord import NotFound

from bot import Interaction
from commands.moderation.primary._base import send_moderation_modal
from core.exceptions import send_bad_argument

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation ban remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_mod_primary_ban_remove(interaction : Interaction, target_id : str) -> None:
    guild = interaction.guild
    if not guild:
        return

    # ⸻ Validate that target_id is a valid ID,

    try:
        validated_target_id = int(target_id)
    except ValueError:
        await send_bad_argument(
            interaction,
            subtitle = {"target" : "`target` must be a valid integer ID between 17 and 19 characters long."},
        )
        return

    # ⸻ ...then try and fetch that target,

    try:
        target = await interaction.client.fetch_user(validated_target_id)
    except NotFound:
        await send_bad_argument(
            interaction,
            subtitle = {"target" : "Target could not be resolved."},
        )
        return

    # ⸻ ...then make sure that the target is actually banned.

    try:
        await guild.fetch_ban(target)
    except NotFound:
        await send_bad_argument(
            interaction,
            subtitle = {"target" : "Target is not banned."},
        )
        return

    await send_moderation_modal(interaction, "Ban Remove", target)
