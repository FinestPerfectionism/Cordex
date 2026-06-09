import asyncio
from typing import TYPE_CHECKING

from bot import Interaction, log
from core import exceptions
from core.responses import send_custom_message

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner pull-reload Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_cogs_pullreload(
    bot         : "Cordex",
    interaction : Interaction,
    cogs        : list[str],
) -> None:
    _ = await interaction.response.defer(ephemeral = True)
    proc = await asyncio.create_subprocess_exec(
        "git", "pull", "origin", "main",
        stdout = asyncio.subprocess.PIPE,
        stderr = asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    pull_output    = stdout.decode().strip() or stderr.decode().strip()

    if proc.returncode != 0:
        log.error("git pull failed (exit %s):\n%s", proc.returncode, pull_output)
        raise exceptions.AppBadOperation(
            title    =  "pull from git",
            subtitle = (
               f"Failed to pull from git:\n"
                "```py\n"
               f"{pull_output[:1800]}\n"
                "```"
            ),
        )

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
        raise exceptions.AppBadOperation(
            title    =  "reload cog",
            subtitle = (
               f"Pull succeeded. {status}\n"
                "```py\n"
               f"{msg[:1800]}\n"
                "```"
            ),
        )

    _ = await send_custom_message(
        interaction,
        msg_type = "success",
        title    = "reloaded cogs",
        subtitle = (
           f"Pulled from git and reloaded all cogs.\n"
            "```py\n"
           f"{pull_output[:1800]}\n"
            "```"
        ),
    )
