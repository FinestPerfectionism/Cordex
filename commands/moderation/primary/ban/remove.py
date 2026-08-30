
from bot import Interaction
from commands.moderation.primary._base import send_moderation_modal

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation ban remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_mod_primary_ban_remove(interaction : Interaction) -> None:
    await send_moderation_modal(interaction, "Ban Remove")
