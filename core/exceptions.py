from discord.app_commands import CheckFailure

from bot import Interaction

from .responses import format_send

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Exceptions Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class UnconfiguredQuarantine(CheckFailure):
    """The exception raised when a user tries to run a quarantine command, but the server has not configured quarantine."""


# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Operation Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def send_bad_operation(
    target   : Interaction,
    /,
    *,
    title    : str = "run command",
    subtitle : str = "An exception occurred during this interaction",
    footer   : str = "Bad operation",
) -> None:
    """
    Warn a user when an operation executed fails.

    Parameters
    ----------
    target : `Interaction`
        The interaction context to send the warning with.
    /
    *
    title : `str = "run command"`
        The title of the error.
    subtitle : `str = "An exception occurred during this interaction"`
        The subtitle of the error.
    footer : `str = "Bad operation"`
        The footer of the error.
    """
    await format_send(
        target,
        msg_type = "error",
        title    = title,
        subtitle = subtitle,
        footer   = footer,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Request Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def send_bad_request(
    target   : Interaction,
    /,
    *,
    title    : str = "run command",
    subtitle : str = "The requested operation is invalid",
    footer   : str = "Bad request",
) -> None:
    """
    Warn a user when they request an invalid operation.

    Parameters
    ----------
    target : `Interaction`
        The interaction context to send the warning with.
    /
    *
    title : `str = "run command"`
        The title of the warning.
    subtitle : `str = "The requested operation is invalid"`
        The subtitle of the warning.
    footer : `str = "Bad request"`
        The footer of the warning.
    """
    await format_send(
        target,
        msg_type = "warning",
        title    = title,
        subtitle = subtitle,
        footer   = footer,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Argument Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def send_bad_argument(
    target   : Interaction,
    /,
    *,
    title    : str = "run command",
    subtitle : dict[str | tuple[str, ...] | None, str],
    footer   : str = "Bad argument",
) -> None:
    """
    Warn a user when they pass one or more invalid arguments.

    Parameters
    ----------
    target : `Interaction`
        The interaction context to send the warning with.
    /
    *
    title : `str = "run command"`
        The title of the warning.
    subtitle : `dict[str | tuple[str, ...] | None, str]`
        The subtitle of the warning.

        - If `dict[str, str]` is passed, it will appear as "`Key`: Value".
        - If `dict[tuple[str, ...], str]` is passed, it will appear as "`Key1, Key2, ...`: Value".
        - If `dict[None, str]` is passed, it will appear as "Value".

    footer : `str = "Bad argument"`
        The footer of the warning.
    """
    issues : list[str] = []

    for argument, notice in subtitle.items():
        match argument:
            case None:
                issues.append(notice)
            case tuple() as arguments:
                issues.append(f"{", ".join(f"`{arg}`" for arg in arguments)}: {notice}")
            case _:
                issues.append(f"`{argument}`: {notice}")

    await format_send(
        target,
        msg_type = "warning",
        title    = title,
        subtitle = "\n".join(issues),
        footer   = footer,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Unimplemented Command Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class UnimplementedCommand(CheckFailure):
    """The exception raised when a command is unimplemented."""


async def send_unimplemented_command(target : Interaction) -> None:
    """
    Warn a user when they run a command that is not implemented.

    Parameters
    ----------
    target : `Interaction`
        The interaction context to send the warning with.
    /
    """
    await format_send(
        target,
        msg_type = "error",
        title    = "run command",
        subtitle = "This command is currently unimplemented",
        footer   = "Bad request",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Permissions Command Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class BadPermissionsCommand(CheckFailure):
    """The exception raised when a user runs a command they are not authorized to use."""


async def send_bad_permissions_command(target : Interaction) -> None:
    """
    Warn a user when they run a command when they are not authorized to do so.

    Parameters
    ----------
    target : `Interaction`
        The interaction context to send the warning with.
    /
    """
    await format_send(
        target,
        msg_type = "error",
        title    = "run command",
        subtitle = "You are not authorized to run this command",
        footer   = "Bad request",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment Guild Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class BadEnvironmentGuild(CheckFailure):
    """The exception raised when a user runs a command in DMs when they must do so in a guild."""


async def send_bad_environment_guildonly(target : Interaction) -> None:
    """
    Warn a user when they run a command in DMs when they must do so in a guild.

    Parameters
    ----------
    target : `Interaction`
        The interaction context to send the warning with.
    /
    """
    await format_send(
        target,
        msg_type = "warning",
        title    = "run command",
        subtitle = "This command can only be run in a guild",
        footer   = "Bad environment",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment DMs Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class BadEnvironmentDMs(CheckFailure):
    """The exception raised when a user runs a command in guild when they must do so in DMs."""


async def send_bad_environment_dmsonly(target : Interaction) -> None:
    """
    Warn a user when they run a command in a guild when they must do so in DMs.

    Parameters
    ----------
    target : `Interaction`
        The interaction context to send the warning with.
    /
    """
    await format_send(
        target,
        msg_type = "warning",
        title    = "run command",
        subtitle = "This command can only be run in DMs",
        footer   = "Bad environment",
    )
