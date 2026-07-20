from operator import eq, ge, gt, le, lt
from typing import TYPE_CHECKING, Literal

from discord import Guild, Member, Role

from bot import Cordex

if TYPE_CHECKING:
    from collections.abc import Callable

    from discord.app_commands import AppCommand

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Utilities Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_command
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def format_command(
    bot   : Cordex,
    path  : str,
    guild : Guild | None = None,
) -> str:
    parts : list[str] = path.strip().split()

    if not parts:
        return "`Invalid Command`"

    root_name : str              = parts[0]
    commands  : list[AppCommand] = []

    if guild:
        commands = await bot.tree.fetch_commands(guild = guild)

    if not any(cmd.name == root_name for cmd in commands):
        commands = await bot.tree.fetch_commands()

    root_id : int | None = None

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

def format_table(table : dict[str, str], *, padding : int = 1) -> str:
    biggest_key = max(len(key) for key in table)

    rows = [
        f"`{key.rjust(biggest_key + padding)}:` {value}"
        for key, value in table.items()
    ]

    return "\n".join(rows)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_values
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def format_values(
    items    : list[str],
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

def check_role_hierarchy(
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


def codeblock(code : str, language : str | None = "py") -> str:
    return (
       f"```{language or ""}\n"
       f"{code}\n"
        "```"
    )
