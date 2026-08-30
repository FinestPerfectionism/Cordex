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
    AllowedMentions,
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

from bot import Context, Cordex, Interaction
from bot.ui import Container, LayoutView, TextDisplay, VisibleLargeSeparator
from constants import (
    BOT_ERRORS_LOG_CHANNEL_ID,
    BOTWORKS_MENTION,
    COLOR_RED,
)
from core.exceptions import (
    BadEnvironmentDMs,
    BadEnvironmentGuild,
    BadPermissionsCommand,
    UnimplementedCommand,
    send_bad_environment_dms,
    send_bad_environment_guild,
    send_bad_operation,
    send_bad_permissions_command,
    send_unimplemented_command,
)
from core.responses import format_send
from core.utilities import codeblock, format_command, format_now, format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Errors Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class ErrorLogger(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot = bot
        self.bot.tree.error(self.command_error_handler)

        self.tasks : set[Task[object]] = set()

    @override
    async def cog_load(self) -> None:
        loop = get_running_loop()
        loop.set_exception_handler(self.loop_exception_handler)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Central Error Sender
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def _send_error(
        self,
        *,
        title       : str,
        user        : User | Member | None = None,
        guild       : Guild         | None = None,
        interaction : Interaction   | None = None,
        error       : str           | None = None,
        traceback   : str           | None = None,
    ) -> None:
        channel = self.bot.get_channel(BOT_ERRORS_LOG_CHANNEL_ID)

        if not isinstance(channel, TextChannel):
            return

        view = LayoutView()

        container = Container[view](
            TextDisplay(
                (
                    f"# {title}\n"
                    f"{BOTWORKS_MENTION}, an unexpected exception has occured."
                ),
            ),
            color = COLOR_RED,
        )

        if traceback:
            container.add_item(
                TextDisplay(
                    (
                        f"## Traceback\n"
                        f"{codeblock(traceback[:2000])}"
                    ),
                ),
            )

        if user:
            table = format_table(
                {
                    "User"     : user.mention,
                    "Username" : user.name,
                    "User ID"  : str(user.id),
                },
            )

            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    (
                        "## User\n"
                       f"{table}"
                    ),
                ),
            )

        if guild:
            table = format_table(
                {
                    "Guild Name" : guild.name,
                    "Guild ID"   : str(guild.id),
                },
            )

            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    (
                        "## Guild\n"
                       f"{table}"
                    ),
                ),
            )

        if interaction and interaction.command:
            qualified_name = interaction.command.qualified_name
            command_id     = interaction.command_id

            table = format_table(
                {
                    "Command"      : format_command(qualified_name),
                    "Command Name" : qualified_name,
                    "Command ID"   : str(command_id),
                },
            )

            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    (
                        "## Command\n"
                       f"{table}"
                    ),
                ),
            )

        if error:
            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    (
                        "## Error\n"
                       f"{codeblock(error)}"
                    ),
                ),
            )

        container.add_items(
            VisibleLargeSeparator(),
            TextDisplay(format_now()),
        )

        view.add_item(container)

        await channel.send(
            view             = view,
            allowed_mentions = AllowedMentions(users = False, roles = True),
        )

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
        exc_type, exc, tb = exc_info()

        if exc is None:
            await self._send_error(
                title  =  "Bot Event Error",
                error  = f"{event}: Unknown exception",
            )
            return

        traceback = "".join(format_exception(exc_type, exc, tb))

        await self._send_error(
            title     =  "Bot Event Error",
            error     = f"{event}: {exc}",
            traceback = traceback,
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

        if isinstance(error, UnimplementedCommand):
            await send_unimplemented_command(interaction)
            return

        await send_bad_operation(interaction)

        traceback = "".join(format_exception(type(error), error, error.__traceback__))

        await self._send_error(
            title       = "Command Error",
            user        = interaction.user,
            guild       = interaction.guild,
            interaction = interaction,
            error       = str(error),
            traceback   = traceback,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # "Prefix Command Errors"
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.Cog.listener("on_command_error")
    async def prefix_command_error_handler(self, _ctx : Context, _error : commands.CommandError) -> None:
        pass  # ⸻ Literally just pass since only eval uses prefix and we shouldn't care.

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Extension Errors
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.Cog.listener("on_extension_error")
    async def extension_error_handler(
        self,
        extension : str,
        error     : commands.ExtensionError,
    ) -> None:
        traceback = "".join(format_exception(type(error), error, error.__traceback__))

        await self._send_error(
            title     =  "Extension Error",
            error     = f"{extension}: {error}",
            traceback = traceback,
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
        ) as e:
            traceback = "".join(format_exception(type(e), e, e.__traceback__))

            await self._send_error(
                title     = "HTTP / REST Error",
                error     = str(e),
                traceback = traceback,
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

        traceback = "".join(format_exception(type(exc), exc, exc.__traceback__))

        self.create_task(
            self._send_error(
                title     = "Background Task Error",
                error     = str(exc),
                traceback = traceback,
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
            traceback = "".join(format_exception(type(exc), exc, exc.__traceback__))
        else:
            traceback = msg_str

        loop.create_task(
            self._send_error(
                title     = "Asyncio Event Loop Error",
                error     = msg_str,
                traceback = traceback,
            ),
        )

async def setup(bot : Cordex) -> None:
    cog = ErrorLogger(bot)
    await bot.add_cog(cog)
