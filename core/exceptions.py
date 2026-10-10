# pyright: reportImportCycles = false

from discord.app_commands import CheckFailure
from discord.ext import commands

from bot import ContextOrInteraction

from .responses import FormatOverride, MessageType, PunctuationOverride, format_send
from .utilities import format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Exceptions Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class UnconfiguredQuarantine(CheckFailure):
    """The exception raised when a user tries to run a quarantine command, but the server has not configured quarantine."""


# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Operation Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def send_bad_operation(
    target   : ContextOrInteraction,
    /,
    *,
    title    : str = "run command",
    subtitle : str = "An exception occurred while processing this request",
    footer   : str = "Bad operation",
) -> None:
    """
    Warn a user when an operation executed fails.

    Parameters
    ----------
    target : `Context | Interaction`
        The interaction or prefix context to send the warning with.
    /
    *
    title : `str = "run command"`
        The title of the error.
    subtitle : `str = "An exception occurred while processing this request"`
        The subtitle of the error.
    footer : `str = "Bad operation"`
        The footer of the error.
    """
    await format_send(
        target,
        MessageType.error,
        title    = title,
        subtitle = subtitle,
        footer   = footer,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Request Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def send_bad_request(
    target   : ContextOrInteraction,
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
    target : `Context | Interaction`
        The interaction or prefix context to send the warning with.
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
        MessageType.warning,
        title    = title,
        subtitle = subtitle,
        footer   = footer,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Argument Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def send_bad_argument(
    target   : ContextOrInteraction,
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
    target : `Context | Interaction`
        The interaction or prefix context to send the warning with.
    /
    *
    title : `str = "run command"`
        The title of the warning.
    subtitle : `dict[str | tuple[str, ...] | None, str]`
        The subtitle of the warning.

        - If `dict[str, str]` is passed, it will appear as "`Key`: Value".
        - If `dict[tuple[str, ...], str]` is passed, it will appear as "`Key1, Key2, ...`: Value".
        - If `dict[None, str]` is passed, it will appear as "Value" and be at the very top of all warnings.

        Note that only one `None` type key may be passed or the most recent one will be overridden.

    footer : `str = "Bad argument"`
        The footer of the warning.
    """
    argument_nones : list[str]      = []
    argument_table : dict[str, str] = {}
    for argument, notice in subtitle.items():
        match argument:
            case None:
                argument_nones.append(notice)
            case tuple() as arguments:
                argument_table[f"{", ".join(arg for arg in arguments)}"] = notice
            case _:
                argument_table[argument] = notice

    table     = format_table(argument_table, padding = 0 if len(argument_table) == 1 else 1)
    nones_str = "\n".join(argument_nones)
    await format_send(
        target,
        MessageType.warning,
        title    = title,
        subtitle = "\n".join(filter(None, (nones_str, table))),
        footer   = footer,
        override = FormatOverride(punctuation = PunctuationOverride(subtitle = False)),
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Unimplemented Command Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class UnimplementedCommand(CheckFailure):
    """The exception raised when a command is unimplemented."""


async def send_unimplemented_command(target : ContextOrInteraction, /) -> None:
    """
    Warn a user when they run a command that is not implemented.

    Parameters
    ----------
    target : `Context | Interaction`
        The interaction or prefix context to send the warning with.
    /
    """
    await format_send(
        target,
        MessageType.error,
        title    = "run command",
        subtitle = "This command is currently unimplemented",
        footer   = "Bad request",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Permissions Command Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class BadPermissionsPrefixCommand(commands.CheckFailure):
    """The exception raised when a user runs a prefix command they are not authorized to use."""


class BadPermissionsCommand(CheckFailure):
    """The exception raised when a user runs a command they are not authorized to use."""


async def send_bad_permissions_command(target : ContextOrInteraction, /) -> None:
    """
    Warn a user when they run a command when they are not authorized to do so.

    Parameters
    ----------
    target : `Context | Interaction`
        The interaction or prefix context to send the warning with.
    /
    """
    await format_send(
        target,
        MessageType.error,
        title    = "run command",
        subtitle = "You are not authorized to run this command",
        footer   = "Bad request",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment Guild Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class BadEnvironmentGuild(CheckFailure):
    """The exception raised when a user runs a command in DMs when they must do so in a guild."""


async def send_bad_environment_guildonly(target : ContextOrInteraction, /) -> None:
    """
    Warn a user when they run a command in DMs when they must do so in a guild.

    Parameters
    ----------
    target : `Context | Interaction`
        The interaction or prefix context to send the warning with.
    /
    """
    await format_send(
        target,
        MessageType.warning,
        title    = "run command",
        subtitle = "This command can only be run in a guild",
        footer   = "Bad environment",
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment DMs Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class BadEnvironmentDMs(CheckFailure):
    """The exception raised when a user runs a command in guild when they must do so in DMs."""


async def send_bad_environment_dmsonly(target : ContextOrInteraction, /) -> None:
    """
    Warn a user when they run a command in a guild when they must do so in DMs.

    Parameters
    ----------
    target : `Context | Interaction`
        The interaction or prefix context to send the warning with.
    /
    """
    await format_send(
        target,
        MessageType.warning,
        title    = "run command",
        subtitle = "This command can only be run in DMs",
        footer   = "Bad environment",
    )
