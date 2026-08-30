
from bot import Interaction
from commands.moderation.primary._base import send_moderation_modal

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation quarantine remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_mod_primary_quarantine_remove(interaction : Interaction) -> None:
    await send_moderation_modal(interaction, "Quarantine Remove")
