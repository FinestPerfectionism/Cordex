from collections.abc import Callable
from typing import Literal

from discord import Member, User
from discord.app_commands import check
from discord.utils import format_dt, utcnow

from bot import Cordex, Interaction
from constants import DEVELOPER_IDS

from .exceptions import UnimplementedCommand

type _Styles = Literal["f", "F", "d", "D", "t", "T", "s", "S", "R"]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Utilities Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# is_bot_owner
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def is_bot_owner(target : User | Member, /) -> bool:
    """
    Check if a user or member is a bot owner.

    Parameters
    ----------
    target : User | Member
        The user or member to check.

    Returns
    -------
    bool
        Whether the user or member was a bot owner or not.
    """
    return target.id in DEVELOPER_IDS

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @unimplemented
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def unimplemented[F]() -> Callable[[F], F]:
    """
    Mark a command as unimplemented.

    Returns
    -------
    Callable[[F], F]
        The decorator function.
    """
    def predicate(_interaction : Interaction) -> bool:
        raise UnimplementedCommand

    def decorator(func : F) -> F:
        check(predicate)(func)
        return func

    return decorator

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_now
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def format_now(style : _Styles = "F", /) -> str:
    """
    Format `utcnow` into a discord timestamp.

    Parameters
    ----------
    style : ["f", "F", "d", "D", "t", "T", "s", "S", "R"]
        The style of the timestamp to create.

    Returns
    -------
    str
        The timestamp.
    """
    return format_dt(utcnow(), style)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_command
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def format_command(bot : Cordex, path : str, /) -> str:
    """
    Format a command path into a clickable mention.

    Parameters
    ----------
    bot : Cordex
        The bot.
    path : str
        The path of the command to format.
    /

    Returns
    -------
    str
        The formatted command.
    """
    parts : list[str] = path.strip().split()

    if not parts:
        return "`Invalid Command`"

    root_name : str        = parts[0]
    root_id   : int | None = None

    commands = bot.get_api_commands_cache()

    for cmd in commands:
        if cmd.name == root_name:
            root_id = cmd.id
            break

    if root_id:
        return f"</{path}:{root_id}>"
    return f"`/{path}`"

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_table
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def format_table[K, V](table : dict[K, V], /, *, padding : int = 1, code : bool = False) -> str:
    """
    Format a dictionary into a table.

    Parameters
    ----------
    table : dict[K, V]
        The table to format.
    /
    *
    padding : int = 1
        The spacing to apply on the left side of the table.
    code : bool = False
        Whether the entire table should be in a codeblock.

    Returns
    -------
    str
        The formatted table.
    """
    biggest_key = max([len(str(key)) for key in table], default = 0)
    width       = biggest_key + padding

    rows = [
        f"{key!s:>{width}}: {value}"
        if code else
        f"`{key!s:>{width}}:` {value}"
        for key, value in table.items()
    ]

    output = "\n".join(rows)
    return codeblock(output) if code else output

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_values
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def format_values(
    items   : list[str],
    /,
    *,
    divider : str = ", ",
    conj    : str = "and",
    wrap    : str = "",
) -> str:
    """
    Format a list of items into a readable, oxford-comma style string.

    Parameters
    ----------
    items : list[str]
        The list of strings to format.
    /
    *
    divider : str = ", "
        The divider between every item.
    conj : str = "and"
        The conjunction to use before the very last item.
    wrap : str = ""
        The string to wrap every item in.

    Returns
    -------
    str
        The formatted values.
    """
    if not items:
        return ""

    items = [f"{wrap}{item}{wrap}" for item in items]

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} {conj} {items[1]}"

    return f"{divider.join(items[:-1])}{divider.rstrip()} {conj} {items[-1]}"

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# codeblock
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def codeblock(code : str | Exception, /, *, language : str | None = "py") -> str:
    """
    Format a string or exception into a codbelock.

    Parameters
    ----------
    code : str | Exception
        The string or exception to place in a codeblock.
    /
    *
    language : str | None = "py"
        The language of the codeblock to use for markdown.

    Returns
    -------
    str
        The text in a codeblock.
    """
    return (
       f"```{language or ""}\n"
       f"{code}\n"
        "```"
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# truncate
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def truncate(text : str, /, *, limit : int = 2000) -> str:
    """
    Truncate a block of text by replacing the last 3 characters before the limit with an ellipsis (...).

    If `text` ends with three backticks, then it will replace the three characters *before* said bacticks to prevent codeblocks from breaking.

    Parameters
    ----------
    text : str
        The text to truncate.
    /
    *
    limit : int = 2000
        The limit to truncate at.

    Returns
    -------
    str
        The truncated text.
    """
    if not len(text) > limit:
        return text

    if limit < 3 or (text.endswith("```") and limit < 6):
        return "..."

    if text.endswith("```"):
        return text[: limit - 6] + "..." + text[-3 :]
    return text[: limit - 3] + "..."
