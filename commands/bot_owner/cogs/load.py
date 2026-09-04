from bot import Interaction, log
from commands.bot_owner._base import get_cogs
from core.exceptions import send_bad_argument, send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner cog load Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_cog_load(interaction : Interaction, cog : str) -> None:
    client = interaction.client

    await interaction.response.defer(ephemeral = True)

    cogs = get_cogs()

    if cog not in cogs:
        await send_bad_argument(interaction, subtitle = {"cog" : f"Cog `{cog}` not found."})
        return
    if cog in client.extensions:
        await send_bad_argument(interaction, subtitle = {"cog" : f"Cog `{cog}` is already loaded."})
        return
    try:
        await client.load_extension(cog)
        await client.tree.sync()
        await client.rebuild_commands_cache()
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
                f"{codeblock(e)}"
            ),
        )
        return
