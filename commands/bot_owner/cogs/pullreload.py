from asyncio import create_subprocess_exec, subprocess

from bot import Interaction, log
from commands.bot_owner._base import get_cogs
from core.exceptions import send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner cog pull-reload Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_cog_pullreload(interaction : Interaction) -> None:
    client = interaction.client

    await interaction.response.defer(ephemeral = True)

    cogs = get_cogs()

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
                f"{codeblock(pull_output[:1800])}"
            ),
        )
        return

    failed : list[tuple[str, Exception]] = []
    for cog in cogs:
        try:
            await client.reload_extension(cog)
            await client.tree.sync()
            await client.rebuild_commands_cache()
            log.info("Reloaded cog %s", cog)
        except Exception as e:
            failed.append((cog, e))
            log.exception("Failed to reload cog %s", cog)

    if failed:
        msg = "\n".join(f"{c}: {e}" for c, e in failed)

        if len(failed) == len(cogs):
            status = "All cogs failed to reload."
        elif len(failed) > 1:
            status = "Multiple cogs failed to reload."
        else:
            status = "A cog failed to reload."

        s = "s" if len(cogs) > 1 else ""

        await send_bad_operation(
            interaction,
            title    = f"reload cog{s}",
            subtitle = (
                f"Pull succeeded. {status}\n"
                f"{codeblock(msg[:1800])}"
            ),
        )
        return

    await format_send(
        interaction,
        msg_type = "success",
        title    = "reloaded cogs",
        subtitle = (
            f"Pulled from git and reloaded all cogs.\n"
            f"{codeblock(pull_output[:1800])}"
        ),
    )
