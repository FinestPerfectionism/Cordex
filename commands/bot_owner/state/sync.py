from bot import Cordex, Interaction, tree
from core.exceptions import send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner state sync Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_sync(bot : Cordex, interaction : Interaction) -> None:
    try:
        bot.destroy_commands_cache()
        await tree.sync()
        bot.build_commands_cache()
        await format_send(
            interaction,
            msg_type = "success",
            title    = "synced app command tree",
            subtitle = "Successfully globally synced the app command tree.",
        )
    except Exception as e:
        await send_bad_operation(
            interaction,
            title    = "sync app command tree",
            subtitle = codeblock(f"{e}"),
        )
        return
