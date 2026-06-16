from bot import Cordex, Interaction, log
from core.exceptions import send_bad_argument, send_bad_operation
from core.responses import send_custom_message

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner unload Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_cogs_unload(
    bot         : Cordex,
    interaction : Interaction,
    cog         : str,
    cogs        : list[str],
) -> None:
    if cog == "commands.bot_owner._group_cog":
        await send_bad_argument(interaction, subtitle = {"cog": "You may not explicitly unload the bot-owner cog."})
        return

    if cog not in cogs:
        await send_bad_argument(interaction, subtitle = {"cog" : f"Cog `{cog}` not found."})
        return

    if cog not in bot.extensions:
        await send_bad_argument(interaction, subtitle = {"cog" : f"Cog `{cog}` is not currently loaded."})
        return

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
        await send_bad_operation(
            interaction,
            title    = "unload cog",
            subtitle = (
               f"Failed to unload cog `{cog}`:\n"
                "```py\n"
               f"{e}"
                "```"
            ),
        )
        return
