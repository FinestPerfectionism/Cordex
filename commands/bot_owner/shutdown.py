from bot import Context
from constants import COG_EMOJI

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .shutdown Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_bo_shutdown(ctx : Context) -> None:
    await ctx.send(
       f"{COG_EMOJI} **Shutting down bot.**\n"
        "Shutting down bot...",
    )
    await ctx.bot.close()
