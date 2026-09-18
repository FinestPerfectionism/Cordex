
from bot import Interaction
from constants import COG_EMOJI

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner state shutdown Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_bo_state_shutdown(interaction : Interaction) -> None:
    await interaction.response.send_message(
       f"{COG_EMOJI} **Shutting down bot.**\n"
        "Shutting down bot...",
    )
    await interaction.client.close()
