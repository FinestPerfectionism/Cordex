from asyncio import sleep
from os import execv
from sys import argv, executable, stderr, stdout

from discord import CustomActivity, DiscordException, Status

from bot import Interaction, log
from core.exceptions import send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner state restart Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_restart(interaction : Interaction) -> None:
    client = interaction.client

    await interaction.response.defer(ephemeral = True)

    if client.restarting:
        await send_bad_operation(
            interaction,
            title    = "restart bot",
            subtitle = "A restart is already in progress.",
        )
        return

    client.restarting = True

    confirm_msg = await format_send(
        interaction,
        msg_type = "information",
        title    = "Restarting bot.",
        subtitle = "Restarting bot...",
    )

    log.info("Attempting a restart.")

    try:
        await client.change_presence(
            status   = Status.idle,
            activity = CustomActivity(name = "Restarting..."),
        )
        await sleep(1)
    except Exception:
        log.info("Couldn't set presence while restarting. Continuing...")

    try:
        for handler in log.handlers:
            if hasattr(handler, "flush"):
                handler.flush()

        stdout.flush()
        stderr.flush()
    except Exception:
        log.exception("Couldn't flush logs. Continuing...")

    try:
        await client.close()
    except Exception:
        log.exception("Received fatal error during restart.")

    try:
        execv(  # ruff: ignore[start-process-with-no-shell]
            executable,
            [executable, *argv[1:]],
        )

    except (OSError, DiscordException) as e:
        log.exception("Received fatal error during restart")
        client.restarting = False

        if confirm_msg and not client.is_closed():
            await format_send(
                interaction,
                message  = confirm_msg,
                msg_type = "error",
                title    = "restart bot",
                subtitle = codeblock(f"{e}"),
            )
            await client.change_presence(status = Status.online)
