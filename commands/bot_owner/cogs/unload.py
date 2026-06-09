from typing import TYPE_CHECKING

from bot import Interaction, log
from core import exceptions
from core.responses import send_custom_message

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner unload Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_cogs_unload(
    bot         : "Cordex",
    interaction : Interaction,
    cog         : str,
    cogs        : list[str],
) -> None:
    if cog == "commands.bot_owner._group_cog":
        raise exceptions.AppBadArgument({"cog": "You may not explicitly unload the bot-owner cog."})

    if cog not in cogs:
        raise exceptions.AppBadArgument({"cog" : f"Cog `{cog}` not found."})

    if cog not in bot.extensions:
        raise exceptions.AppBadArgument({"cog" : f"Cog `{cog}` is not currently loaded."})

    try:
        await bot.unload_extension(cog)
        _ = await send_custom_message(
            interaction,
            msg_type =  "success",
            title    =  "unloaded cog",
            subtitle = f"Unloaded cog `{cog}`.",
        )
        log.info("Unloaded cog %s", cog)
    except Exception as e:
        log.exception("Failed to unload cog %s", cog)
        raise exceptions.AppBadOperation(
            title    = "unload cog",
            subtitle = (
               f"Failed to unload cog `{cog}`:\n"
                "```py\n"
               f"{e}"
                "```"
            ),
        ) from None
