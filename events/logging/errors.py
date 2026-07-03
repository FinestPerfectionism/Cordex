import asyncio
import sys
import traceback
from asyncio import Task
from collections.abc import Coroutine
from typing import override

import aiohttp
from discord import Embed, Forbidden, Guild, HTTPException, NotFound, TextChannel
from discord.abc import User
from discord.app_commands import AppCommandError, CommandInvokeError
from discord.ext import commands
from discord.utils import utcnow

from bot import Cordex, Interaction, tree
from constants import (
    BOT_ERRORS_LOG_CHANNEL_ID,
    BOT_OWNER_ID,
    COLOR_RED,
)
from core.exceptions import (
    send_bad_environment_dms,
    send_bad_environment_guild,
    send_bad_environment_mainguild,
    send_bad_environment_mainguildordms,
    send_bad_permissions_command,
)
from core.permissions import (
    BadEnvironmentDMs,
    BadEnvironmentGuild,
    BadEnvironmentMainGuild,
    BadEnvironmentMainGuildOrDMs,
    BadPermissions,
)
from core.utilities import codeblock

MAX_ERRORS = 5
n_429      = 429

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Errors Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class ErrorLogger(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot             : Cordex            = bot
        self.tasks           : set[Task[object]] = set()
        self.rate_limit_hits : int               = 0
        tree.error(self.app_command_error_handler)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Central Error Sender
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def send_error(
        self,
        *,
        title           : str,
        user            : User  | None = None,
        guild           : Guild | None = None,
        command_display : str   | None = None,
        error_text      : str   | None = None,
        traceback_text  : str   | None = None,
    ) -> None:
        channel = self.bot.get_channel(BOT_ERRORS_LOG_CHANNEL_ID)
        if not isinstance(channel, TextChannel):
            return

        embed = Embed(
            title     = title,
            color     = COLOR_RED,
            timestamp = utcnow(),
        )

        if user:
            embed.add_field(
                name   =  "User",
                value  = (
                    f"`{user}`\n"
                    f"`{user.id}`"
                ),
                inline = True,
            )

        if guild:
            embed.add_field(
                name   =  "Guild",
                value  = (
                    f"`{guild}`\n"
                    f"`{guild.id}`"
                ),
                inline = True,
            )

        if command_display:
            embed.add_field(
                name   = "Command",
                value  = codeblock(command_display, language = None),
                inline = True,
            )

        if error_text:
            embed.add_field(
                name   = "Error",
                value  = codeblock(error_text),
                inline = False,
            )

        if traceback_text:
            embed.description = (
               f"**Traceback:**\n"
                "```py\n"
               f"{traceback_text[:3900]}\n"
                "```"
            )
        else:
            embed.description = None

        await channel.send(
            content = f"<@{BOT_OWNER_ID}>",
            embed   = embed,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # 429 / Rate Limit Guard
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def handle_rate_limit(self, source : str) -> None:
        self.rate_limit_hits += 1

        await self.send_error(
            title      = "Rate Limited (429)",
            error_text = (
                f"Source: {source}\n"
                f"Hit {self.rate_limit_hits}/{MAX_ERRORS} this session."
            ),
        )

        if self.rate_limit_hits >= MAX_ERRORS:
            await self.send_error(
                title      = "Auto-Shutdown: Too Many 429s",
                error_text = f"Received {MAX_ERRORS} rate limit responses this session. Shutting down to prevent an IP ban.",
            )
            await self.bot.close()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Discord Event Errors
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.Cog.listener("on_error")
    async def error_handler(
        self,
        event     : str,
        *_args    : str,
        **_kwargs : int,
    ) -> None:
        if event in {"on_command_error", "on_interaction"}:
            return

        exc_type, exc, tb = sys.exc_info()

        if isinstance(exc, commands.CommandNotFound):
            return

        if exc is None:
            await self.send_error(
                title      =  "Bot Event Error",
                error_text = f"{event}: Unknown exception",
            )
            return

        if isinstance(exc, HTTPException) and exc.status == n_429:
            await self.handle_rate_limit(f"event: {event}")
            return

        tb_text = "".join(traceback.format_exception(exc_type, exc, tb))

        await self.send_error(
            title          =  "Bot Event Error",
            error_text     = f"{event}: {exc}",
            traceback_text = tb_text,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Application Command Errors
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def app_command_error_handler(
        self,
        interaction : Interaction,
        error       : AppCommandError,
    ) -> None:
        actual_error = error.original if isinstance(error, CommandInvokeError) else error

        if isinstance(error, BadPermissions):
            await send_bad_permissions_command(interaction)
            return

        if isinstance(error, BadEnvironmentGuild):
            await send_bad_environment_guild(interaction)
            return

        if isinstance(error, BadEnvironmentDMs):
            await send_bad_environment_dms(interaction)
            return

        if isinstance(error, BadEnvironmentMainGuild):
            await send_bad_environment_mainguild(interaction)
            return

        if isinstance(error, BadEnvironmentMainGuildOrDMs):
            await send_bad_environment_mainguildordms(interaction)
            return

        if isinstance(actual_error, HTTPException) and actual_error.status == n_429:
            cmd      = interaction.command
            cmd_name = f"/{cmd.qualified_name}" if cmd else "Unknown"
            await self.handle_rate_limit(cmd_name)
            return

        tb_text = "".join(traceback.format_exception(type(error), error, error.__traceback__))

        await self.send_error(
            title           =  "Application Command Error",
            user            = interaction.user,
            guild           = interaction.guild,
            command_display = f"/{interaction.command.qualified_name}" if interaction.command else "Unknown",
            error_text      = str(error),
            traceback_text  = tb_text,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Extension Errors
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.Cog.listener("on_extension_error")
    async def extension_error_handler(
        self,
        extension : str,
        error     : commands.ExtensionError,
    ) -> None:
        tb_text = "".join(traceback.format_exception(type(error), error, error.__traceback__))

        await self.send_error(
            title          =  "Extension Error",
            error_text     = f"{extension}: {error}",
            traceback_text = tb_text,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # HTTP Errors
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def guard_http(self, coro : Coroutine[object, object, object]) -> object:
        try:
            return await coro
        except (
            Forbidden,
            NotFound,
            HTTPException,
            aiohttp.ClientError,
        ) as exc:
            if isinstance(exc, HTTPException) and exc.status == n_429:
                await self.handle_rate_limit("guard_http")
                raise

            tb_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

            await self.send_error(
                title          = "HTTP / REST Error",
                error_text     = str(exc),
                traceback_text = tb_text,
            )
            raise

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Task Errors
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def create_task(
        self,
        coro : Coroutine[object, object, object],
        *,
        name : str,
    ) -> Task[object]:
        task = asyncio.create_task(coro, name = name)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        task.add_done_callback(self.task_done)
        return task

    def task_done(self, task : Task[object]) -> None:
        if task.cancelled():
            return
        try:
            exc = task.exception()
        except asyncio.InvalidStateError:
            return

        if exc is None:
            return

        if isinstance(exc, HTTPException) and exc.status == n_429:
            self.create_task(
                self.handle_rate_limit(f"task: {task.get_name()}"),
                name = "task_ratelimit_reporter",
            )
            return

        tb_text = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__),
        )

        self.create_task(
            self.send_error(
                title          = "Background Task Error",
                error_text     = str(exc),
                traceback_text = tb_text,
            ),
            name = "task_error_reporter",
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Loop Exception Errors
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def loop_exception_handler(
        self,
        loop    : asyncio.AbstractEventLoop,
        context : dict[str, object],
    ) -> None:
        if loop.is_closed():
            return

        exc = context.get("exception")
        msg = context.get("message")
        msg_str = str(msg) if msg is not None else "No message"

        if isinstance(exc, BaseException):
            tb_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        else:
            tb_text = msg_str

        loop.create_task(
            self.send_error(
                title          = "Asyncio Event Loop Error",
                error_text     = msg_str,
                traceback_text = tb_text,
            ),
        )

    @override
    async def cog_load(self) -> None:
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(self.loop_exception_handler)

async def setup(bot : Cordex) -> None:
    cog = ErrorLogger(bot)
    await bot.add_cog(cog)
