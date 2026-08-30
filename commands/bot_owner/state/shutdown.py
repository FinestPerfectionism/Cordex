from typing import TYPE_CHECKING

from core.responses import format_send

if TYPE_CHECKING:
    from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner state shutdown Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_shutdown(interaction : Interaction) -> None:
    await format_send(
        interaction,
        msg_type = "information",
        title    = "Shutting down bot",
        subtitle = "Shutting down bot...",
    )
    await interaction.client.close()
