from typing import TypeAlias

from discord import Button, ButtonStyle, SeparatorSpacing, Emoji, PartialEmoji
from discord.ui import Separator, button, LayoutView

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Utilities Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Layout Helpers
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

LVSep : TypeAlias = Separator[LayoutView]
LVBtn : TypeAlias = Button

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
