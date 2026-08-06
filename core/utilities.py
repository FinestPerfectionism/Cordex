from collections.abc import Callable
from operator import eq, ge, gt, le, lt
from typing import Literal

from discord import Member, Role
from discord.app_commands import check

from bot import Interaction, bot

from .exceptions import UnimplementedCommand

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Utilities Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @unimplemented
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def unimplemented[F : Callable[..., object]]() -> Callable[[F], F]:
    def predicate(_interaction : Interaction) -> bool:
        raise UnimplementedCommand

    def decorator(func : F) -> F:
        check(predicate)(func)
        return func

    return decorator

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

def format_table(table : dict[str, str], /, *, padding : int = 1) -> str:
    biggest_key = max([len(str(key)) for key in table], default = 0)
    width       = biggest_key + padding

    rows = [
        f"`{key : > {width}}:` {value}"
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
    items = [f"{wrap}{item}{wrap}" for item in items]

    if not use_conj:
        return divider.join(items)

    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {conj} {items[1]}"

    return f"{divider.join(items[:-1])}{divider.rstrip()} {conj} {items[-1]}"

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# check_hierarchy
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def check_hierarchy(
    *,
    actor      : Member,
    target     : Member,
    comparison : Literal[">", "<", "=", ">=", "<="],
) -> bool:

    # ⸻ Owner vs Owner

    if actor.guild.owner_id == actor.id:
        if target.guild.owner_id == target.id:
            return comparison in {"=", ">=", "<="}
        return comparison in {">", ">="}

    # ⸻ Actor vs Owner

    if target.guild.owner_id == target.id:
        return comparison in {"<", "<="}

    actor_role  = actor.top_role
    target_role = target.top_role

    ops : dict[str, Callable[[Role, Role], bool]] = {
        ">"  : gt,
        "<"  : lt,
        "="  : eq,
        ">=" : ge,
        "<=" : le,
    }

    return ops[comparison](actor_role, target_role)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# codeblock
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def codeblock(code : str, /, *, language : str | None = "py") -> str:
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
