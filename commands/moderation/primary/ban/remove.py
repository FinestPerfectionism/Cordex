from bot import Interaction
from commands.moderation.primary._base import send_moderation_modal
from core.exceptions import send_bad_argument

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation ban remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_mod_primary_ban_remove(interaction : Interaction, target : str) -> None:
    try:
        validated_target = int(target)
    except ValueError:
        await send_bad_argument(
            interaction,
            subtitle = {"target" : "`target` must be a valid integer ID between 17 and 19 characters long."},
        )
        return

    await send_moderation_modal(interaction, "Ban Remove", validated_target)
