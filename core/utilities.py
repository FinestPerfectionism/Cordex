import operator
from typing import TYPE_CHECKING, Literal

from discord import ButtonStyle, Member, Role, SeparatorSpacing
from discord.ui import LayoutView, Separator

if TYPE_CHECKING:
    from collections.abc import Callable

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Utilities Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Layout Helpers
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

large = SeparatorSpacing.large
small = SeparatorSpacing.small

blurple = ButtonStyle.blurple
grey    = ButtonStyle.grey
green   = ButtonStyle.green
red     = ButtonStyle.red
link    = ButtonStyle.link

class VisibleLargeSeparator(Separator[LayoutView]):
    def __init__(self) -> None:
        super().__init__(visible = True, spacing = large)

class VisibleSmallSeparator(Separator[LayoutView]):
    def __init__(self) -> None:
        super().__init__(visible = True, spacing = small)

class HiddenLargeSeparator(Separator[LayoutView]):
    def __init__(self) -> None:
        super().__init__(visible = False, spacing = large)

class HiddenSmallSeparator(Separator[LayoutView]):
    def __init__(self) -> None:
        super().__init__(visible = False, spacing = small)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# General Helpers
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def format_values(
    items    : list[str],
    *,
    divider  : str  = ", ",
    use_conj : bool = True,
    conj     : str  = "and",
    wrap     : str  = "",
) -> str:
    if wrap:
        items = [f"{wrap}{item}{wrap}" for item in items]

    if not items:
        return ""

    if not use_conj:
        return divider.join(items)

    two = 2
    if len(items) == 1:
        return items[0]
    if len(items) == two:
        return f"{items[0]} {conj} {items[1]}"

    return f"{divider.join(items[:-1])}{divider.rstrip()} {conj} {items[-1]}"

def check_role_hierarchy(
    actor      : Member,
    target     : Member,
    comparison : Literal[">", "<", "=", ">=", "<="],
) -> bool:
    actor_role  = actor.top_role
    target_role = target.top_role

    ops : dict[str, Callable[[Role, Role], bool]] = {
        ">"  : operator.gt,
        "<"  : operator.lt,
        "="  : operator.eq,
        ">=" : operator.ge,
        "<=" : operator.le,
    }

    return ops[comparison](actor_role, target_role)

def codeblock(text : str, language : str | None = "py") -> str:
    return (
       f"```{language or ''}\n"
       f"{text}\n"
        "```"
    )
