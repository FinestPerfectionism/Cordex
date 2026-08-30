from typing import TYPE_CHECKING

from commands.moderation.primary._base import send_moderation_modal

if TYPE_CHECKING:
    from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation timeout remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_mod_primary_timeout_remove(interaction : Interaction) -> None:
    await send_moderation_modal(interaction, "Timeout Remove")
