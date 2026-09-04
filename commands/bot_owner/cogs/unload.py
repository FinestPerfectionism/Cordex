from bot import Interaction, log
from commands.bot_owner._base import get_cogs
from core.exceptions import send_bad_argument, send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner cog unload Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_cog_unload(interaction : Interaction, cog : str) -> None:
    client = interaction.client

    await interaction.response.defer(ephemeral = True)

    cogs = get_cogs()

    if cog not in cogs:
        await send_bad_argument(interaction, subtitle = {"cog" : f"Cog `{cog}` not found."})
        return

    if cog not in client.extensions:
        await send_bad_argument(interaction, subtitle = {"cog" : f"Cog `{cog}` is not currently loaded."})
        return

    try:
        await client.unload_extension(cog)
        await client.tree.sync()
        await client.rebuild_commands_cache()
        await format_send(
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
                f"{codeblock(e)}"
            ),
        )
        return
