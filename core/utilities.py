from collections.abc import Callable
from typing import Literal

from discord.app_commands import check
from discord.utils import format_dt, utcnow

from bot import Interaction, bot

from .exceptions import UnimplementedCommand

type _Styles = Literal["f", "F", "d", "D", "t", "T", "s", "S", "R"]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Utilities Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

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

def format_command(path : str, /) -> str:
    parts : list[str] = path.strip().split()

    if not parts:
        return "`Invalid Command`"

    root_name : str        = parts[0]
    root_id   : int | None = None

    commands = bot.get_app_commands_cache()

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

def format_table[K, V](table : dict[K, V], /, *, padding : int = 1) -> str:
    biggest_key = max([len(str(key)) for key in table], default = 0)
    width       = biggest_key + padding

    rows = [
        f"`{key!s:>{width}}:` {value}"
        for key, value in table.items()
    ]

    return "\n".join(rows)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_values
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def format_values(
    items    : list[str],
    /,
    *,
    divider  : str  = ", ",
    use_conj : bool = True,
    conj     : str  = "and",
    wrap     : str  = "",
) -> str:
    if not items:
        return ""

    items = [f"{wrap}{item}{wrap}" for item in items]

    if not use_conj or len(items) == 1:
        return divider.join(items)

    if len(items) == 2:
        return f"{items[0]} {conj} {items[1]}"

    return f"{divider.join(items[:-1])}{divider} {conj} {items[-1]}"

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
    return (text)[:length - 3] + "..." if len(text) > length else text
