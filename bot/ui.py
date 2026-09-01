from logging import getLogger as get_logger
from typing import TYPE_CHECKING, Self, final, override

from discord import (
    ButtonStyle,
    Color,
    SeparatorSpacing,
)
from discord.ui import (
    ActionRow,
    Button,
    ChannelSelect,
    Checkbox,
    CheckboxGroup,
    File,
    FileUpload,
    Item,
    Label,
    MediaGallery,
    MentionableSelect,
    RadioGroup,
    RoleSelect,
    Section,
    Select,
    Separator,
    TextInput,
    Thumbnail,
    UserSelect,
    View,
    button,
    select,
)
from discord.ui import Container as BaseContainer
from discord.ui import LayoutView as BaseLayoutView
from discord.ui import Modal as BaseModal
from discord.ui import TextDisplay as BaseTextDisplay

__all__ = [
    "ActionRow",
    "BaseContainer",
    "BaseLayoutView",
    "Button",
    "ChannelSelect",
    "Checkbox",
    "CheckboxGroup",
    "File",
    "FileUpload",
    "Item",
    "Label",
    "MediaGallery",
    "MentionableSelect",
    "Modal",
    "RadioGroup",
    "RoleSelect",
    "Section",
    "Select",
    "Separator",
    "TextInput",
    "Thumbnail",
    "UserSelect",
    "View",
    "button",
    "select",
]

if TYPE_CHECKING:
    from .bot import Interaction

log = get_logger("Cordex")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot UI
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# LayoutView
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class LayoutView(BaseLayoutView):
    def __init__(self, *, timeout : float | None = 600) -> None:
        super().__init__(timeout = timeout)

    def add_text(self, text : str, /) -> Self:
        self.add_item(TextDisplay(text))

        return self

    def add_items(self, *items : Item[BaseLayoutView | Self]) -> Self:
        if len(items) == 1:
            log.warning("Prefer LayoutView.add_item over LayoutView.add_items")

        for item in items:
            self.add_item(item)

        return self

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Modal
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class Modal(BaseModal):
    @override
    async def on_submit(self, interaction : "Interaction", /) -> None:  # type: ignore[reportIncompatibleMethodOverride] # ruff: ignore[quoted-annotation]
        ...

    def add_text(self, text : str, /) -> Self:
        self.add_item(TextDisplay(text))

        return self

    def add_items(self, *items : Item[Modal | Self]) -> Self:
        if len(items) == 1:
            log.warning("Prefer Modal.add_item over Modal.add_items")

        for item in items:
            self.add_item(item)

        return self

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# TextDisplay
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class TextDisplay[V : LayoutView | Modal](BaseTextDisplay[V]):
    def __init__(self, content : str, /) -> None:
        super().__init__(content)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Container
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class Container[V : LayoutView](BaseContainer[V]):
    def __init__(
        self,
        *children : Item[V],
        color     : Color | None = None,
        spoiler   : bool         = False,
    ) -> None:
        super().__init__(*children, accent_color = color, spoiler = spoiler)

    @property
    def color(self) -> Color | None:
        return self.accent_color

    @color.setter
    def color(self, value : Color | None, /) -> None:
        self.accent_color : Color | None = value

    def add_text(self, text : str, /) -> Self:
        self.add_item(TextDisplay(text))
        return self

    def add_items(self, *items : Item[V]) -> Self:
        if len(items) == 1:
            log.warning("Prefer Container.add_item over Container.add_items")

        for item in items:
            self.add_item(item)

        return self

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Separator Sizes
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


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

@final
class VisibleLargeSeparator[V : LayoutView](Separator[V]):
    def __init__(self) -> None:
        super().__init__(visible = True, spacing = large)

@final
class VisibleSmallSeparator[V : LayoutView](Separator[V]):
    def __init__(self) -> None:
        super().__init__(visible = True, spacing = small)

@final
class HiddenLargeSeparator[V : LayoutView](Separator[V]):
    def __init__(self) -> None:
        super().__init__(visible = False, spacing = large)

@final
class HiddenSmallSeparator[V : LayoutView](Separator[V]):
    def __init__(self) -> None:
        super().__init__(visible = False, spacing = small)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Section Variants
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class ButtonSection[V : LayoutView](Section[V]):
    def __init__(self, *args : str | TextDisplay[V], button : Button[V]) -> None:
        super().__init__(*args, accessory = button)
        self.button : Button[V] = button

class ThumbnailSection[V : LayoutView](Section[V]):
    def __init__(self, *args : str | TextDisplay[V], thumbnail : Thumbnail[V]) -> None:
        super().__init__(*args, accessory = thumbnail)
        self.thumbnail : Thumbnail[V] = thumbnail
