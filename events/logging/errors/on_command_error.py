from typing import TYPE_CHECKING

from discord.ext import commands

from bot import Context
from core import exceptions as e
from core.responses import send_custom_message

from ._base import (
    get_bad_argument_subtitle,
    get_bad_operation_subtitle,
    get_bad_operation_title,
    get_bad_permissions_subtitle,
)

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Command Error Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot : "Cordex") -> None:
        self.bot : "Cordex" = bot
        super().__init__()

    @commands.Cog.listener("on_command_error")
    async def command_error_handling(self, ctx : Context, error : commands.CommandError) -> None:
        if isinstance(error, e.UnknownError):
            _ = await send_custom_message(
                ctx,
                msg_type          = "error",
                title             = "run command",
                subtitle          = "An unknown exception occured while running this command.",
                footer            = "Unknown error",
                contact_bot_owner = True,
            )
            return

        if isinstance(error, e.BadOperation):
            _ = await send_custom_message(
                ctx,
                msg_type = "error",
                title    = get_bad_operation_title(error.title),
                subtitle = get_bad_operation_subtitle(error.subtitle),
                footer   = "Bad operation",
            )
            return

        if isinstance(error, e.BadArgument):
            _ = await send_custom_message(
                ctx,
                msg_type = "warning",
                title    = "run command",
                subtitle = get_bad_argument_subtitle(error.subtitle),
                footer   = "Bad argument",
            )
            return

        if isinstance(error, e.BadPermissionsCommand):
            _ = await send_custom_message(
                ctx,
                msg_type = "error",
                title    = "run command",
                subtitle = "You are not authorized to run this command.",
                footer   = "Bad request",
            )
            return

        if isinstance(error, e.BadPermissionsArgument):
            _ = await send_custom_message(
                ctx,
                msg_type = "error",
                title    = "run command",
                subtitle = get_bad_permissions_subtitle(error.arguments),
                footer   = "Bad request",
            )
            return

        if isinstance(error, e.BadEnvironmentDMs):
            _ = await send_custom_message(
                ctx,
                msg_type = "warning",
                title    = "run command",
                subtitle = "This command can only be run in a guild.",
                footer   = "Bad environment",
            )
            return

        if isinstance(error, e.BadEnvironmentChannel):
            _ = await send_custom_message(
                ctx,
                msg_type = "warning",
                title    = "run command",
                subtitle = "This command cannot be run in this channel or thread.",
                footer   = "Bad environment",
            )
            return

async def setup(bot : "Cordex") -> None:
    cog = CommandErrorHandler(bot)
    await bot.add_cog(cog)
