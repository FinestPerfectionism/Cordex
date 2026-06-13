from core.responses import send_custom_message

from bot import CtxOrInteraction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Exceptions Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Unknown Error Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_unknown_error(target : CtxOrInteraction) -> None:
    _ = await send_custom_message(
        target,
        msg_type          = "error",
        title             = "run command",
        subtitle          = "An unknown exception occurred while running this command.",
        footer            = "Unknown error",
        contact_bot_owner = True,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Operation Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_operation(
    target   : CtxOrInteraction,
    *,
    title    : str,
    subtitle : str | None = "An exception occured while running this command.",
) -> None:
    _ = await send_custom_message(
        target,
        msg_type = "error",
        title    = title,
        subtitle = subtitle if subtitle else "An exception occurred while running this command.",
        footer   = "Bad operation",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Argument Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_argument(target : CtxOrInteraction, *, subtitle : dict[str, str]) -> None:
    _ = await send_custom_message(
        target,
        msg_type = "warning",
        title    = "run command",
        subtitle = "\n".join(f"`{arg}`: {notice}" for arg, notice in subtitle.items()),
        footer   = "Bad argument",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Permissions Command Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_permissions_command(target : CtxOrInteraction) -> None:
    _ = await send_custom_message(
        target,
        msg_type = "error",
        title    = "run command",
        subtitle = "You are not authorized to run this command.",
        footer   = "Bad request",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Permissions Argument Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_permissions_argument(target : CtxOrInteraction, *args : str) -> None:
    arguments : tuple[str, ...] = args
    formatted_args = [f"`{arg}`" for arg in arguments]
    if len(formatted_args) == 1:
        subtitle = f"You are not authorized to use the {formatted_args[0]} argument."
    subtitle = f"You are not authorized to use these arguments: {', '.join(formatted_args)}"
    
    _ = await send_custom_message(
        target,
        msg_type = "error",
        title    = "run command",
        subtitle = subtitle,
        footer   = "Bad request",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment Guild Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_environment_guild(target : CtxOrInteraction) -> None:
    _ = await send_custom_message(
        target,
        msg_type = "warning",
        title    = "run command",
        subtitle = "This command can only be run in DMs",
        footer   = "Bad environment",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment Channel Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_environment_channel(target : CtxOrInteraction) -> None:
    _ = await send_custom_message(
        target,
        msg_type = "warning",
        title    = "run command",
        subtitle = "This command cannot be run in this channel or thread.",
        footer   = "Bad environment",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment DMs Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_environment_dms(target : CtxOrInteraction) -> None:
    _ = await send_custom_message(
        target,
        msg_type = "warning",
        title    = "run command",
        subtitle = "This command can only be run in a guild.",
        footer   = "Bad environment",
    )
