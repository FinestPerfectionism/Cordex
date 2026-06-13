from collections.abc import Callable
from discord import ButtonStyle, Role, SeparatorSpacing, Member
from discord.ui import Separator, LayoutView
from typing import TypeAlias, Literal

import operator

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Utilities Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Layout Helpers
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

LVSep : TypeAlias = Separator[LayoutView]

large = SeparatorSpacing.large
small = SeparatorSpacing.small

blurple = ButtonStyle.blurple
grey    = ButtonStyle.grey
green   = ButtonStyle.green
red     = ButtonStyle.red
link    = ButtonStyle.link

class VisibleLargeSeparator(LVSep):
    def __init__(self) -> None:
        super().__init__(visible = True, spacing = large)

class VisibleSmallSeparator(LVSep):
    def __init__(self) -> None:
        super().__init__(visible = True, spacing = small)

class HiddenLargeSeparator(LVSep):
    def __init__(self) -> None:
        super().__init__(visible = False, spacing = large)

class HiddenSmallSeparator(LVSep):
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

    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {conj} {items[1]}"

    return f"{divider.join(items[:-1])}{divider.rstrip()} {conj} {items[-1]}"

def check_role_hierarchy(
    actor      : Member, 
    target     : Member, 
    comparison : Literal[">", "<", "=", ">=", "<="]
) -> bool:
    actor_role  = actor.top_role
    target_role = target.top_role
    
    ops : dict[str, Callable[[Role, Role], bool]] = {
        ">"  : operator.gt,
        "<"  : operator.lt,
        "="  : operator.eq,
        ">=" : operator.ge,
        "<=" : operator.le
    }

    return ops[comparison](actor_role, target_role)

def codeblock(text : str, language : str = "py") -> str:
    return (
       f"```{language}\n"
       f"{text}\n"
        "```"
    )