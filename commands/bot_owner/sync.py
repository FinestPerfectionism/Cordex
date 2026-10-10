from bot import Context, log
from core.exceptions import send_bad_operation
from core.responses import MessageType, format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .sync Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_bo_sync(ctx : Context) -> None:
    bot = ctx.bot

    try:
        log.info("Attempting a tree sync.")
        synced = await bot.tree.sync()
        await bot.rebuild_api_commands_cache()
        await format_send(
            ctx,
            MessageType.success,
            title    = "synced app command tree",
            subtitle = "Successfully globally synced the app command tree",
        )
    except Exception as e:
        log.exception("An exxception occurred during the tree sync.")
        await send_bad_operation(
            ctx,
            title    = "sync app command tree",
            subtitle = codeblock(e),
        )
    else:
        log.info("Tree sync complete. %s commands synced.", len(synced))
