from bot import Cordex, Interaction, log, tree
from commands.bot_owner import get_cogs
from core.exceptions import send_bad_argument, send_bad_operation
from core.responses import format_send

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner cog load Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_cogs_load(
    bot         : Cordex,
    interaction : Interaction,
    cog         : str,
) -> None:
    await interaction.response.defer(ephemeral = True)

    cogs : list[str] = get_cogs()

    if cog not in cogs:
        await send_bad_argument(interaction, subtitle = {"cog" : f"Cog `{cog}` not found."})
        return
    if cog in bot.extensions:
        await send_bad_argument(interaction, subtitle = {"cog" : f"Cog `{cog}` is already loaded."})
        return
    try:
        await bot.load_extension(cog)
        await tree.sync()
        await bot.rebuild_commands_cache()
        await format_send(
            interaction,
            msg_type =  "success",
            title    =  "loaded cog",
            subtitle = f"Loaded cog `{cog}`.",
        )
        log.info("Loaded cog %s", cog)
    except Exception as e:
        log.exception("Failed to load cog %s", cog)
        await send_bad_operation(
            interaction,
            title    = "load cog",
            subtitle = (
               f"Failed to load cog `{cog}`:\n"
                "```py\n"
               f"{e}"
                "```"
            ),
        )
        return
