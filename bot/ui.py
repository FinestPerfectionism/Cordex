from typing import final

from discord import (
    ButtonStyle,
    ChannelType,
    Color,
    Member,
    Role,
    SelectDefaultValue,
    SelectOption,
    SeparatorSpacing,
    User,
)
from discord.app_commands import AppCommandChannel, AppCommandThread
from discord.ui import (
    Button,
    ChannelSelect,
    Item,
    Label,
    MentionableSelect,
    Modal,
    RoleSelect,
    Section,
    Select,
    Separator,
    TextDisplay,
    Thumbnail,
    UserSelect,
)
from discord.ui import Container as BaseContainer
from discord.ui import LayoutView as BaseLayoutView

__all__ = ["TextDisplay"]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot UI
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# LayoutView
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class LayoutView(BaseLayoutView):
    def __init__(self, *, timeout : float | None = None) -> None:
        super().__init__(timeout = timeout)

    def add_text(self, text : str, /) -> None:
        self.add_item(TextDisplay(text))

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Container
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class Container[V : BaseLayoutView = LayoutView](BaseContainer[V]):
    def __init__(
        self,
        *children: Item[V],
        color     : Color | None = None,
        spoiler   : bool = False,
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
# Modal Select Variants
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class ModalSelect(Label[Modal]):
    def __init__(
        self,
        *,
        placeholder : str | None = None,
        min_values  : int        = 1,
        max_values  : int        = 1,
        options     : list[SelectOption],
        required    : bool       = True,
        text        : str,
        description : str | None = None,
    ) -> None:
        component : Select[Modal] = Select(
            placeholder = placeholder,
            min_values  = min_values,
            max_values  = max_values,
            options     = options,
            required    = required,
        )
        super().__init__(
            text        = text,
            description = description,
            component   = component,
        )
        self._underlying_component = component

    @property
    def values(self) -> list[str]:
        return self._underlying_component.values

@final
class UserModalSelect(Label[Modal]):
    def __init__(
        self,
        *,
        placeholder    : str | None = None,
        min_values     : int        = 1,
        max_values     : int        = 1,
        required       : bool       = True,
        text           : str,
        description    : str | None = None,
        default_values : list[SelectDefaultValue],
    ) -> None:
        component : UserSelect[Modal] = UserSelect(
            placeholder    = placeholder,
            min_values     = min_values,
            max_values     = max_values,
            required       = required,
            default_values = default_values,
        )
        super().__init__(
            text        = text,
            description = description,
            component   = component,
        )
        self._underlying_component = component

    @property
    def values(self) -> list[User | Member]:
        return self._underlying_component.values

@final
class RoleModalSelect(Label[Modal]):
    def __init__(
        self,
        *,
        placeholder    : str | None = None,
        min_values     : int        = 1,
        max_values     : int        = 1,
        required       : bool       = True,
        text           : str,
        description    : str | None = None,
        default_values : list[SelectDefaultValue],
    ) -> None:
        component : RoleSelect[Modal] = RoleSelect(
            placeholder    = placeholder,
            min_values     = min_values,
            max_values     = max_values,
            required       = required,
            default_values = default_values,
        )
        super().__init__(
            text        = text,
            description = description,
            component   = component,
        )
        self._underlying_component = component

    @property
    def values(self) -> list[Role]:
        return self._underlying_component.values

@final
class MentionableModalSelect(Label[Modal]):
    def __init__(
        self,
        *,
        placeholder    : str | None = None,
        min_values     : int        = 1,
        max_values     : int        = 1,
        required       : bool       = True,
        text           : str,
        description    : str | None = None,
        default_values : list[SelectDefaultValue],
    ) -> None:
        component : MentionableSelect[Modal] = MentionableSelect(
            placeholder    = placeholder,
            min_values     = min_values,
            max_values     = max_values,
            required       = required,
            default_values = default_values,
        )
        super().__init__(
            text        = text,
            description = description,
            component   = component,
        )
        self._underlying_component = component

    @property
    def values(self) -> list[Role | User | Member]:
        return self._underlying_component.values

@final
class ChannelModalSelect(Label[Modal]):
    def __init__(
        self,
        *,
        channel_types  : list[ChannelType],
        placeholder    : str | None = None,
        min_values     : int        = 1,
        max_values     : int        = 1,
        required       : bool       = True,
        text           : str,
        description    : str | None = None,
        default_values : list[SelectDefaultValue],
    ) -> None:
        component : ChannelSelect[Modal] = ChannelSelect(
            channel_types  = channel_types,
            placeholder    = placeholder,
            min_values     = min_values,
            max_values     = max_values,
            required       = required,
            default_values = default_values,
        )
        super().__init__(
            text        = text,
            description = description,
            component   = component,
        )
        self._underlying_component = component

    @property
    def values(self) -> list[AppCommandChannel | AppCommandThread]:
        return self._underlying_component.values

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Section Variants
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class ButtonSection(Section[LayoutView]):
    def __init__(self, *args : str | TextDisplay[LayoutView], button : Button[LayoutView]) -> None:
        super().__init__(*args, accessory = button)
        self.button : Button[LayoutView] = button

class ThumbnailSection(Section[LayoutView]):
    def __init__(self, *args : str | TextDisplay[LayoutView], thumbnail : Thumbnail[LayoutView]) -> None:
        super().__init__(*args, accessory = thumbnail)
        self.thumbnail : Thumbnail[LayoutView] = thumbnail
