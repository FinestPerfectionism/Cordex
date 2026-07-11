from discord import DiscordException

from bot import Interaction, tree
from core.exceptions import send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /sync Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_sync(interaction : Interaction) -> None:
    try:
        await tree.sync()
        await format_send(
            interaction,
            msg_type = "success",
            title    = "synced app command tree",
            subtitle = "Successfully globally synced the app command tree.",
        )

    except DiscordException as e:
        await send_bad_operation(
            interaction,
            title    = "sync app command tree",
            subtitle = codeblock(f"{e}"),
        )
        return
