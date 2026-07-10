import asyncio
import sys
from logging import Logger
from os import execv

import discord
from discord import CustomActivity, Status

from bot import Cordex, Interaction
from core.exceptions import send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /restart Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_restart(
    bot        : Cordex,
    interaction: Interaction,
    restarting : list[bool],
    log        : Logger,
) -> None:
    if restarting[0]:
        await send_bad_operation(
            interaction,
            title    = "restart bot",
            subtitle = "A restart is already in progress.",
        )
        return

    restarting[0] = True

    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral = True)

    confirm_msg = await format_send(
        interaction,
        msg_type     = "information",
        title        = "Restarting bot.",
        subtitle     = "Restarting bot...",
    )

    loop         = asyncio.get_running_loop()
    restart_task = loop.create_task(
        restart_bot(
            interaction,
            bot,
            log,
            restarting,
            confirm_msg,
        ),
    )
    restart_task.add_done_callback(lambda t : t.exception() if not t.cancelled() else None)

async def restart_bot(
    interaction    : Interaction,
    bot            : Cordex,
    log            : Logger,
    restarting_ref : list[bool],
    confirm_msg    : discord.Message | None = None,
) -> None:
    try:
        await bot.change_presence(
            status   = Status.idle,
            activity = CustomActivity(name = "Restarting..."),
        )

        await asyncio.sleep(1)
        await bot.close()

        pending = [
            t for t in asyncio.all_tasks()
            if not t.done() and
            t is not asyncio.current_task()
        ]

        if pending:
            for task in pending:
                task.cancel()
            try:
                await asyncio.wait_for(
                    asyncio.gather(
                        *pending,
                        return_exceptions = True,
                    ),
                    timeout = 5.0,
                )
            except TimeoutError:
                log.exception("Some tasks did not cancel in time")

        for handler in log.handlers:
            if hasattr(handler, "flush"):
                handler.flush()

        sys.stdout.flush()
        sys.stderr.flush()

        execv(  # noqa: S606
            sys.executable,
            [sys.executable, *sys.argv],
        )

    except (OSError, discord.DiscordException) as e:
        log.exception("Received fatal error during restart")
        restarting_ref[0] = False

        if confirm_msg:
            await format_send(
                interaction,
                message  = confirm_msg,
                msg_type = "error",
                title    = "restart bot",
                subtitle = codeblock(f"{e}"),
            )

        await bot.change_presence(status = Status.online)
