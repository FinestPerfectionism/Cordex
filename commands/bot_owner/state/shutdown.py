import contextlib

import discord

from bot import Cordex, Context
from core.responses import send_custom_message

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .shutdown Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_shutdown(bot : "Cordex", ctx : Context) -> None:
    with contextlib.suppress(discord.HTTPException, discord.Forbidden):
        await ctx.message.delete()

    _ = await send_custom_message(
        ctx,
        msg_type     = "information",
        title        = "Shutting down bot",
        subtitle     = "Shutting down bot...",
        delete_after = 1,
    )

    await bot.close()
