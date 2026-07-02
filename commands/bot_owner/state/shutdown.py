from bot import Cordex, Interaction
from core.responses import send_custom_message

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /shutdown Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_shutdown(bot : Cordex, interaction : Interaction) -> None:
    await send_custom_message(
        interaction,
        msg_type     = "information",
        title        = "Shutting down bot",
        subtitle     = "Shutting down bot...",
    )
    await bot.close()
