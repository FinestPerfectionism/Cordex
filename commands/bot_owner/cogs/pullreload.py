from asyncio import create_subprocess_exec, subprocess

from bot import Cordex, Interaction, log
from commands.bot_owner import get_cogs
from core.exceptions import send_bad_operation
from core.responses import format_send

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner cog pull-reload Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_cogs_pullreload(bot : Cordex, interaction : Interaction) -> None:
    await interaction.response.defer(ephemeral = True)
    cogs : list[str] = get_cogs()

    proc = await create_subprocess_exec(
        "git", "pull", "origin", "main",
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    pull_output    = stdout.decode().strip() or stderr.decode().strip()

    if proc.returncode != 0:
        log.error("git pull failed (exit %s):\n%s", proc.returncode, pull_output)
        await send_bad_operation(
            interaction,
            title    =  "pull from git",
            subtitle = (
               f"Failed to pull from git:\n"
                "```py\n"
               f"{pull_output[:1800]}\n"
                "```"
            ),
        )
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
               f"Pull succeeded. {status}\n"
                "```py\n"
               f"{msg[:1800]}\n"
                "```"
            ),
        )
        return

    await format_send(
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
