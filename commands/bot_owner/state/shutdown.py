from bot import Cordex, Interaction
from core.responses import format_send

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner state shutdown Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_shutdown(bot : Cordex, interaction : Interaction) -> None:
    await format_send(
        interaction,
        msg_type = "information",
        title    = "Shutting down bot",
        subtitle = "Shutting down bot...",
    )
    await bot.close()
