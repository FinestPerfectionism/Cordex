import asyncio
import contextlib
import logging
import sys
from os import execv
from typing import TYPE_CHECKING

import discord

from bot import Context
from constants import DENIED_EMOJI
from core.exceptions import BadOperation
from core.responses import send_custom_message

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .restart Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_restart(
    bot            : "Cordex",
    ctx            : Context,
    restarting_ref : list[bool],
    log            : logging.Logger,
) -> None:
    if restarting_ref[0]:
        raise BadOperation(
            title    = "restart bot",
            subtitle = "A restart is already in progress.",
        )

    restarting_ref[0] = True
    
    with contextlib.suppress(discord.Forbidden):
        await ctx.message.delete()
        
    confirm_msg = await send_custom_message(
        ctx,
        msg_type     = "information",
        title        = "Restarting bot.",
        subtitle     = "Restarting bot...",
        delete_after = 1,
    )

    loop         = asyncio.get_running_loop()
    restart_task = loop.create_task(
        restart_bot(
            bot,
            log,
            restarting_ref,
            confirm_msg,
        ),
    )
    restart_task.add_done_callback(lambda t : t.exception() if not t.cancelled() else None)

async def restart_bot(
    bot            : "Cordex",
    log            : logging.Logger,
    restarting_ref : list[bool],
    confirm_msg    : discord.Message | None = None,
) -> None:
    try:
        await bot.change_presence(
            status   = discord.Status.idle,
            activity = discord.CustomActivity(name = "Restarting..."),
        )

        await asyncio.sleep(1)
        await bot.close()

        pending = [
            t for t in asyncio.all_tasks()
            if not t.done() and t is not asyncio.current_task()
        ]

        if pending:
            for task in pending:
                _ = task.cancel()
            try:
                _ = await asyncio.wait_for(
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

        _ = sys.stdout.flush()
        _ = sys.stderr.flush()

        execv( # noqa: S606
            sys.executable,
            [sys.executable, *sys.argv],
        )

    except (OSError, discord.DiscordException) as e:
        log.exception("Received fatal error during restart")
        restarting_ref[0] = False

        if confirm_msg:
            _ = await confirm_msg.edit(
                content = (
                   f"{DENIED_EMOJI} **Failed to restart bot!**\n"
                    "Restart failed:\n"
                    "```py\n"
                   f"{e}\n"
                    "```"
                ),
            )

        await bot.change_presence(status = discord.Status.online)
