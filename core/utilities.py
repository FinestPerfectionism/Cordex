from operator import eq, ge, gt, le, lt
from typing import TYPE_CHECKING, Literal

from discord import Member, Role

if TYPE_CHECKING:
    from collections.abc import Callable

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Utilities Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

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
