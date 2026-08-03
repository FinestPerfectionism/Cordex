from typing import Self, final

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
    Modal,
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

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot UI
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# TextDisplay
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class TextDisplay[V : LayoutView](BaseTextDisplay[V]):
    def __init__(self, content : str, /) -> None:
        super().__init__(content)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# LayoutView
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class LayoutView(BaseLayoutView):
    def __init__(self, *, timeout : float | None = 600) -> None:
        super().__init__(timeout = timeout)

    def add_text(self, text : str, /) -> None:
        self.add_item(TextDisplay(text))

    def add_items(self, *items : Item[Self]) -> None:
        for item in items:
            self.add_item(item)

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

    def add_text(self, text : str, /) -> None:
        self.add_item(TextDisplay(text))

    def add_items(self, *items : Item[V]) -> None:
        for item in items:
            self.add_item(item)

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
