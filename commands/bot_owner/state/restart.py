from asyncio import all_tasks, current_task, gather, get_running_loop, sleep, wait_for
from logging import Logger
from os import execv
from sys import argv, executable, stderr, stdout

from discord import CustomActivity, DiscordException, Message, Status

from bot import Cordex, Interaction, log
from core.exceptions import send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner state restart Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_state_restart(bot : Cordex, interaction : Interaction) -> None:
    restarting : list[bool] = [False]

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

    loop         = get_running_loop()
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
    confirm_msg    : Message | None = None,
) -> None:
    try:
        await bot.change_presence(
            status   = Status.idle,
            activity = CustomActivity(name = "Restarting..."),
        )

        await sleep(1)
        await bot.close()

        pending = [
            t for t in all_tasks()
            if not t.done() and
            t is not current_task()
        ]

        if pending:
            for task in pending:
                task.cancel()
            try:
                await wait_for(
                    gather(
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

        stdout.flush()
        stderr.flush()

        execv(  # noqa: S606
            executable,
            [executable, *argv],
        )

    except (OSError, DiscordException) as e:
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
