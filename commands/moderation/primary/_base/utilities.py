from bot import Interaction

from .select import ActionType

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Utilites Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_moderation_modal(interaction : Interaction, action_type : ActionType) -> None:
    await interaction.response.send_message("...")
