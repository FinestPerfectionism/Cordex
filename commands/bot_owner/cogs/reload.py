from typing import TYPE_CHECKING

from bot import Interaction, log
from core.exceptions import send_bad_argument, send_bad_operation
from core.responses import send_custom_message

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner reload Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_cogs_reload(
    bot         : "Cordex",
    interaction : Interaction,
    cog         : str | None,
    cogs        : list[str],
) -> None:
    if cog:
        if cog not in cogs:
            await send_bad_argument(interaction, subtitle = {"cog" : f"Cog `{cog}` not found."})
            return
        try:
            await bot.reload_extension(cog)
            _ = await send_custom_message(
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
                    "```py\n"
                   f"{e}"
                    "```"
                ),
            )
            return
        return

    failed : list[tuple[str, Exception]] = []
    for c in cogs:
        try:
            await bot.reload_extension(c)
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
                "```py\n"
               f"{msg[:1800]}\n"
                "```"
            ),
        )
        return

    _ = await send_custom_message(
        interaction,
        msg_type = "success",
        title    = "reloaded cogs",
        subtitle = "Reloaded all cogs successfully.",
    )
