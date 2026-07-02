from bot import ContextOrInteraction
from core.responses import send_custom_message

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Exceptions Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Unknown Error Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_unknown_error(target : ContextOrInteraction) -> None:
    await send_custom_message(
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
    target   : ContextOrInteraction,
    *,
    title    : str,
    subtitle : str | None = "An exception occured while running this command.",
) -> None:
    await send_custom_message(
        target,
        msg_type = "error",
        title    = title,
        subtitle = subtitle or "An exception occurred while running this command.",
        footer   = "Bad operation",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Argument Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_argument(
    target   : ContextOrInteraction,
    *,
    subtitle : dict[
        str | tuple[str, ...] | set[str] | None,
        str,
    ],
    footer   : str | None = None
) -> None:
    formatted_lines : list[str] = []
    
    for arg, notice in subtitle.items():
        if arg is None:
            formatted_lines.append(notice)
        elif isinstance(arg, set | tuple | list):
            joined_args = ", ".join(f"`{a}`" for a in arg)
            formatted_lines.append(f"{joined_args}: {notice}")
        else:
            formatted_lines.append(f"`{arg}`: {notice}")

    await send_custom_message(
        target,
        msg_type = "warning",
        title    = "run command",
        subtitle = "\n".join(formatted_lines),
        footer   = footer or "Bad argument",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Permissions Command Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_permissions_command(target : ContextOrInteraction) -> None:
    await send_custom_message(
        target,
        msg_type = "error",
        title    = "run command",
        subtitle = "You are not authorized to run this command.",
        footer   = "Bad request",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Permissions Argument Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_permissions_argument(target : ContextOrInteraction, *args : str) -> None:
    arguments : tuple[str, ...] = args
    formatted_args = [f"`{arg}`" for arg in arguments]
    if len(formatted_args) == 1:
        subtitle = f"You are not authorized to use the {formatted_args[0]} argument."
    subtitle = f"You are not authorized to use these arguments: {', '.join(formatted_args)}"

    await send_custom_message(
        target,
        msg_type = "error",
        title    = "run command",
        subtitle = subtitle,
        footer   = "Bad request",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment Guild Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_environment_guild(target : ContextOrInteraction) -> None:
    await send_custom_message(
        target,
        msg_type = "warning",
        title    = "run command",
        subtitle = "This command can only be run in DMs",
        footer   = "Bad environment",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment Channel Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_environment_channel(target : ContextOrInteraction) -> None:
    await send_custom_message(
        target,
        msg_type = "warning",
        title    = "run command",
        subtitle = "This command cannot be run in this channel or thread.",
        footer   = "Bad environment",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment DMs Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_bad_environment_dms(target : ContextOrInteraction) -> None:
    await send_custom_message(
        target,
        msg_type = "warning",
        title    = "run command",
        subtitle = "This command can only be run in a guild.",
        footer   = "Bad environment",
    )
