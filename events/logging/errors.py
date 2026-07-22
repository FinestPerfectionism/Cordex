from asyncio import (
    AbstractEventLoop,
    InvalidStateError,
    Task,
    create_task,
    get_running_loop,
)
from collections.abc import Coroutine
from secrets import randbelow
from sys import exc_info
from traceback import format_exception
from typing import final, override

from aiohttp import ClientError
from discord import (
    Embed,
    Forbidden,
    Guild,
    HTTPException,
    Member,
    NotFound,
    TextChannel,
    User,
)
from discord.app_commands import AppCommandError
from discord.ext import commands
from discord.utils import utcnow

from bot import Cordex, Interaction, tree
from constants import (
    BOT_ERRORS_LOG_CHANNEL_ID,
    BOT_OWNER_ID,
    COLOR_RED,
)
from core.exceptions import (
    BadEnvironmentDMs,
    BadEnvironmentGuild,
    BadEnvironmentMainGuild,
    BadEnvironmentMainGuildOrDMs,
    BadPermissionsCommand,
    send_bad_environment_dms,
    send_bad_environment_guild,
    send_bad_environment_mainguild,
    send_bad_environment_mainguildordms,
    send_bad_operation,
    send_bad_permissions_command,
)
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Errors Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class ErrorLogger(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot                       = bot
        self.tasks : set[Task[object]] = set()
        tree.error(self.command_error_handler)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Central Error Sender
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def send_error(
        self,
        *,
        title           : str,
        user            : User | Member | None = None,
        guild           : Guild         | None = None,
        command_display : str           | None = None,
        error_text      : str           | None = None,
        traceback_text  : str           | None = None,
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
                name   = "User",
                value  = (
                    f"`{user}`\n"
                    f"`{user.id}`"
                ),
                inline = True,
            )

        if guild:
            embed.add_field(
                name   = "Guild",
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

        await channel.send(f"<@{BOT_OWNER_ID}>", embed = embed)

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
        if event == "on_interaction":
            return

        exc_type, exc, tb = exc_info()

        if isinstance(exc, commands.CommandNotFound):
            return

        if isinstance(exc, commands.MissingRequiredArgument):
            return

        if exc is None:
            await self.send_error(
                title      =  "Bot Event Error",
                error_text = f"{event}: Unknown exception",
            )
            return

        traceback_text = "".join(format_exception(exc_type, exc, tb))

        await self.send_error(
            title          =  "Bot Event Error",
            error_text     = f"{event}: {exc}",
            traceback_text = traceback_text,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Command Errors
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def command_error_handler(
        self,
        interaction : Interaction,
        error       : AppCommandError,
    ) -> None:
        if isinstance(error, BadPermissionsCommand):
            if randbelow(10) == 0:
                await format_send(
                    interaction,
                    msg_type  = "error",
                    title     = "I'm sorry, Dave,",
                    subtitle  = "I'm afraid I can't do that.",
                    footer    = "You are not authorized to run this command — Bad request.",
                    override  = True,
                    ephemeral = False,
                )
            else:
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

        await send_bad_operation(interaction)

        traceback_text = "".join(format_exception(type(error), error, error.__traceback__))

        await self.send_error(
            title           =  "Command Error",
            user            = interaction.user,
            guild           = interaction.guild,
            command_display = f"/{interaction.command.qualified_name}" if interaction.command else "Unknown",
            error_text      = str(error),
            traceback_text  = traceback_text,
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
        traceback_text = "".join(format_exception(type(error), error, error.__traceback__))

        await self.send_error(
            title          =  "Extension Error",
            error_text     = f"{extension}: {error}",
            traceback_text = traceback_text,
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
            ClientError,
        ) as exc:
            traceback_text = "".join(format_exception(type(exc), exc, exc.__traceback__))

            await self.send_error(
                title          = "HTTP / REST Error",
                error_text     = str(exc),
                traceback_text = traceback_text,
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
        task = create_task(coro, name = name)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        task.add_done_callback(self.task_done)
        return task

    def task_done(self, task : Task[object]) -> None:
        if task.cancelled():
            return
        try:
            exc = task.exception()
        except InvalidStateError:
            return

        if exc is None:
            return

        traceback_text = "".join(format_exception(type(exc), exc, exc.__traceback__))

        self.create_task(
            self.send_error(
                title          = "Background Task Error",
                error_text     = str(exc),
                traceback_text = traceback_text,
            ),
            name = "task_error_reporter",
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Loop Exception Errors
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def loop_exception_handler(
        self,
        loop    : AbstractEventLoop,
        context : dict[str, object],
    ) -> None:
        if loop.is_closed():
            return

        exc = context.get("exception")
        msg = context.get("message")
        msg_str = str(msg) if msg is not None else "No message"

        if isinstance(exc, BaseException):
            traceback_text = "".join(format_exception(type(exc), exc, exc.__traceback__))
        else:
            traceback_text = msg_str

        loop.create_task(
            self.send_error(
                title          = "Asyncio Event Loop Error",
                error_text     = msg_str,
                traceback_text = traceback_text,
            ),
        )

    @override
    async def cog_load(self) -> None:
        loop = get_running_loop()
        loop.set_exception_handler(self.loop_exception_handler)

async def setup(bot : Cordex) -> None:
    cog = ErrorLogger(bot)
    await bot.add_cog(cog)
