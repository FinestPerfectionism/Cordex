from bot import Interaction, log
from commands.bot_owner._base import get_cogs
from core.exceptions import send_bad_argument, send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner cog reload Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_cog_reload(interaction : Interaction, cog : str | None = None) -> None:
    client = interaction.client

    await interaction.response.defer(ephemeral = True)

    cogs = get_cogs()

    if cog:
        if cog not in cogs:
            await send_bad_argument(interaction, subtitle = {"cog" : f"Cog `{cog}` not found."})
            return
        try:
            await client.reload_extension(cog)
            await client.tree.sync()
            await client.rebuild_commands_cache()
            await format_send(
                interaction,
                msg_type =  "success",
                title    =  "reloaded cog",
                subtitle = f"Reloaded cog `{cog}`.",
            )
            log.info("Reloaded cog %s", cog)
        except Exception as e:
            log.exception("Failed to reload cog %s", cog)
            await send_bad_operation(
                interaction,
                title    =  "reload cog",
                subtitle = (
                    f"Failed to reload cog `{cog}`:\n"
                    f"{codeblock(f"{e}")}"
                ),
            )
            return
        return

    failed : list[tuple[str, Exception]] = []
    for c in cogs:
        try:
            await client.reload_extension(c)
            log.info("Reloaded cog %s", c)
        except Exception as e:
            failed.append((c, e))
            log.exception("Failed to reload cog %s", c)

    if failed:
        msg = "\n".join(f"{c}: {e}" for c, e in failed)
        if len(failed) == len(cogs):
            status = "All cogs failed to reload."
        elif len(failed) > 1:
            status = "Multiple cogs failed to reload."
        else:
            status = "A cog failed to reload."
        amount = "cogs" if len(cogs) > 1 else "cog"
        await send_bad_operation(
            interaction,
            title    = f"reload {amount}",
            subtitle = (
                f"{status}\n"
                f"{codeblock(msg[:1800])}"
            ),
        )
        return

    await format_send(
        interaction,
        msg_type = "success",
        title    = "reloaded cogs",
        subtitle = "Reloaded all cogs successfully.",
    )
