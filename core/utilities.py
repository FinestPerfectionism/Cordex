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
    return target.id in DEVELOPER_IDS

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @unimplemented
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def unimplemented[F]() -> Callable[[F], F]:
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
    return format_dt(utcnow(), style)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_command
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def format_command(bot : Cordex, path : str, /) -> str:
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
    return (
       f"```{language or ""}\n"
       f"{code}\n"
        "```"
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# truncate
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def truncate(text : str, /, *, length : int = 2000) -> str:
    if not len(text) > length:
        return text

    if text.endswith("```"):
        return text[: length - 6] + "..." + text[-3 :]
    return text[: length - 3] + "..."
