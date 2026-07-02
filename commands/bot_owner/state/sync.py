import discord

from core.exceptions import send_bad_operation
from core.responses import send_custom_message
from core.utilities import codeblock
from bot import Interaction, tree

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /sync Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_sync(interaction : Interaction) -> None:
    try:
        await tree.sync()
        await send_custom_message(
            interaction,
            msg_type = "success",
            title    = "synced app command tree",
            subtitle = "Successfully globally synced the app command tree.",
        )

    except discord.DiscordException as e:
        await send_bad_operation(
            interaction,
            title    = "sync app command tree",
            subtitle = codeblock(f"{e}"),
        )
        return