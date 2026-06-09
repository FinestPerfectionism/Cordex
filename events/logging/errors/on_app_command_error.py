from discord import app_commands

from bot import Interaction, log, tree
from core import exceptions as e
from core.responses import send_custom_message

from ._base import (
    get_bad_argument_subtitle,
    get_bad_operation_subtitle,
    get_bad_operation_title,
    get_bad_permissions_subtitle,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# App Command Error Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@tree.error
async def app_command_error_handling(
    interaction : Interaction,
    error       : app_commands.AppCommandError,
) -> None:
    unwrapped = error.original if isinstance(error, app_commands.CommandInvokeError) else error

    match unwrapped:
        case e.AppUnknownError():
            _ = await send_custom_message(
                interaction,
                msg_type          = "error",
                title             = "run command",
                subtitle          = "An unknown exception occurred while running this command.",
                footer            = "Unknown error",
                contact_bot_owner = True,
            )
            return

        case e.AppBadOperation():
            _ = await send_custom_message(
                interaction,
                msg_type = "error",
                title    = get_bad_operation_title(unwrapped.title),
                subtitle = get_bad_operation_subtitle(unwrapped.subtitle),
                footer   = "Bad operation",
            )
            return

        case e.AppBadArgument():
            _ = await send_custom_message(
                interaction,
                msg_type = "warning",
                title    = "run command",
                subtitle = get_bad_argument_subtitle(unwrapped.subtitle),
                footer   = "Bad argument",
            )
            return

        case e.AppBadPermissionsCommand():
            _ = await send_custom_message(
                interaction,
                msg_type = "error",
                title    = "run command",
                subtitle = "You are not authorized to run this command.",
                footer   = "Bad request",
            )
            return

        case e.AppBadPermissionsArgument():
            _ = await send_custom_message(
                interaction,
                msg_type = "error",
                title    = "run command",
                subtitle = get_bad_permissions_subtitle(unwrapped.arguments),
                footer   = "Bad request",
            )
            return

        case e.AppBadEnvironmentDMs():
            _ = await send_custom_message(
                interaction,
                msg_type = "warning",
                title    = "run command",
                subtitle = "This command can only be run in a guild.",
                footer   = "Bad environment",
            )
            return

        case e.AppBadEnvironmentChannel():
            _ = await send_custom_message(
                interaction,
                msg_type = "warning",
                title    = "run command",
                subtitle = "This command cannot be run in this channel or thread.",
                footer   = "Bad environment",
            )
            return

        case _:
            pass

    log.error("Unhandled command error: %s", unwrapped)
    raise error
