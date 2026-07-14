from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Self

from discord import ButtonStyle, SeparatorSpacing
from discord.ui import (
    Button,
    LayoutView,
    Section,
    Separator,
    TextDisplay,
    Thumbnail,
    View,
    button,
)

if TYPE_CHECKING:
    from . import Interaction

__all__ = ["TextDisplay"]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot UI
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

large = SeparatorSpacing.large
small = SeparatorSpacing.small

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Button Colors
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

blurple = ButtonStyle.blurple
grey    = ButtonStyle.grey
green   = ButtonStyle.green
red     = ButtonStyle.red
link    = ButtonStyle.link

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Separator Variants
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

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

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Section Variants
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class ButtonSection(Section[LayoutView]):
    def __init__(self, *args : str, button : Button[LayoutView]) -> None:
        super().__init__(*args, accessory = button)
        self.button : Button[LayoutView] = button

class ThumbnailSection(Section[LayoutView]):
    def __init__(self, *args : str, thumbnail : Thumbnail[LayoutView]) -> None:
        super().__init__(*args, accessory = thumbnail)
        self.thumbnail : Thumbnail[LayoutView] = thumbnail

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Eval Tools
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


type Inter = Callable[["Interaction"], Coroutine[None, None, None]]

class ViewButton(View):
    def __init__(self, callback : Inter, /) -> None:
        super().__init__(timeout = None)
        self.callback : Inter = callback

    @button(label = "Click me!")
    async def btn_basic(self, interaction : "Interaction", _button : Button[Self]) -> None:
        await self.callback(interaction)
