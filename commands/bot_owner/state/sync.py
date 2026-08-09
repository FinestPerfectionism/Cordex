from bot import Interaction, log
from core.exceptions import send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner state sync Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_sync(interaction : Interaction) -> None:
    client = interaction.client

    try:
        log.info("Starting a tree sync.")
        synced = await client.tree.sync()
        await client.rebuild_commands_cache()
        await format_send(
            interaction,
            msg_type = "success",
            title    = "synced app command tree",
            subtitle = "Successfully globally synced the app command tree.",
        )
    except Exception as e:
        log.exception("An exxception occurred during the tree sync.")
        await send_bad_operation(
            interaction,
            title    = "sync app command tree",
            subtitle = codeblock(f"{e}"),
        )
        return
    else:
        log.info("Tree sync finished. %s commands synced.", len(synced))
