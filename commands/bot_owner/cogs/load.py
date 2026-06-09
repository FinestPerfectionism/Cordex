from typing import TYPE_CHECKING

from bot import Interaction, log
from core import exceptions
from core.responses import send_custom_message

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner load Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_cogs_load(
    bot         : "Cordex",
    interaction : Interaction,
    cog         : str,
    cogs        : list[str],
) -> None:
    if cog not in cogs:
        raise exceptions.AppBadArgument({"cog" : f"Cog `{cog}` not found."})
    if cog in bot.extensions:
        raise exceptions.AppBadArgument({"cog" : f"Cog `{cog}` is already loaded."})
    try:
        await bot.load_extension(cog)
        _ = await send_custom_message(
            interaction,
            msg_type =  "success",
            title    =  "loaded cog",
            subtitle = f"Loaded cog `{cog}`.",
        )
        log.info("Loaded cog %s", cog)
    except Exception as e:
        log.exception("Failed to load cog %s", cog)
        raise exceptions.AppBadOperation(
            title    = "load cog",
            subtitle = (
               f"Failed to load cog `{cog}`:\n"
                "```py\n"
               f"{e}"
                "```"
            ),
        ) from None
