from dataclasses import dataclass
from typing import Protocol, final, override

from discord import Color, Message

from bot import Interaction
from bot.ui import (
    ActionRow,
    Button,
    Container,
    Item,
    LayoutView,
    TextDisplay,
    VisibleLargeSeparator,
    blurple,
)
from core.exceptions import send_bad_operation

__all__ = ["NamedPaginator", "PageData"]

@dataclass(slots = True)
class PageData:
    name    : str
    content : list[str | Item[LayoutView]]


type _ItemsList = list[Item[LayoutView]]

class _InteractionCallback(Protocol):
    async def __call__(self, interaction : Interaction) -> None: ...

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Named Paginator
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class _NameRow(ActionRow["NamedPaginator"]):
    def __init__(self, paginator : NamedPaginator, indices : range) -> None:
        super().__init__()
        self.paginator = paginator
        self.indices   = indices
        self.update_states()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # update_states
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def update_states(self) -> None:
        self.clear_items()

        for index in self.indices:
            page = self.paginator.pages[index]

            is_current = index == self.paginator.current_page

            button : Button[LayoutView] = (
                Button(label = page.name, style = blurple, disabled = is_current)
                if is_current else
                Button(label = page.name)
            )
            button.callback = self._make_callback(index)

            self.add_item(button)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # _make_callback
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def _make_callback(self, index : int) -> _InteractionCallback:
        async def callback(interaction : Interaction) -> None:
            await self.paginator.turn(interaction, index)
        return callback

class NamedPaginator(LayoutView):
    def __init__(
        self,
        data      : list[PageData],
        /,
        *,
        color     : Color | None = None,
        container : bool         = False,
        force     : bool         = False,
        timeout   : int   | None = 600,
    ) -> None:
        super().__init__(timeout = timeout)
        self.message : Message | None = None

        self._data      : list[PageData] = data
        self._color     : Color | None   = color
        self._container : bool           = container
        self._force     : bool           = force

        # ⸻ data must contain more than one page.

        if len(data) == 1:
            error = "data must contain more than one page"
            raise ValueError(error)

        self.pages        : list[PageData] = data or [PageData("No content available.", ["No content available."])]
        self.current_page : int            = 0
        self._name_rows   : list[_NameRow] = [
            _NameRow(self, range(i, min(i + 5, len(self.pages))))
            for i in range(0, len(self.pages), 5)
        ] if len(self.pages) >= 2 else []

        self._above_items : _ItemsList = []
        self._over_items  : _ItemsList = []
        self._under_items : _ItemsList = []
        self._below_items : _ItemsList = []

        # ⸻ color is dependent on container.

        if color and not container:
            error = "color is dependent on container"
            raise ValueError(error)

        # ⸻ Render.

        self.render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # on_timeout
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @override
    async def on_timeout(self) -> None:
        if self.timeout is not None:
            for item in self.walk_children():
                if isinstance(item, Button):
                    item.disabled = True

        if self.message:
            await self.message.edit(view = self)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_above
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_above(self, *items : Item[LayoutView]) -> None:
        self._above_items.extend(items)
        self.render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_over
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_over(self, *items : Item[LayoutView]) -> None:
        self._over_items.extend(items)
        self.render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_under
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_under(self, *items : Item[LayoutView]) -> None:
        self._under_items.extend(items)
        self.render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_below
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_below(self, *items : Item[LayoutView]) -> None:
        self._below_items.extend(items)
        self.render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # render
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def render(self) -> None:
        self.clear_items()

        # ⸻ Add all items above.

        for item in self._above_items:
            self.add_item(item)

        page = self.pages[self.current_page]

        page_items : _ItemsList = []

        if self._force:
            page_items = [
                TextDisplay(item)
                if isinstance(item, str) else item
                for item in page.content
            ]
        else:
            accumulated : list[str] = []

            for item in page.content:
                if isinstance(item, str):
                    accumulated.append(item)
                else:
                    if accumulated:
                        page_items.append(TextDisplay("\n".join(accumulated)))
                        accumulated.clear()
                    page_items.append(item)

            if accumulated:
                page_items.append(TextDisplay("\n".join(accumulated)))

        items : _ItemsList = [*self._over_items, *page_items, VisibleLargeSeparator()]

        self._name_rows = [
            _NameRow(self, range(i, min(i + 5, len(self.pages))))
            for i in range(0, len(self.pages), 5)
        ] if len(self.pages) >= 2 else []

        for name_row in self._name_rows:
            name_row.update_states()
            items.append(name_row)

        items.extend(self._under_items)

        # ⸻ Add all items to the container if chosen or directly to the view if not.

        if self._container:
            self.add_item(Container(*items, color = self._color))
        else:
            for item in items:
                self.add_item(item)

        # ⸻ Add all items below.

        for item in self._below_items:
            self.add_item(item)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # turn
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def turn(self, interaction : Interaction, target : int) -> None:
        if 0 <= target < len(self.pages):
            previous_page = self.current_page

            self.current_page = target
            self.render()

            try:
                await interaction.response.edit_message(view = self)
            except Exception:
                self.current_page = previous_page
                self.render()
                await send_bad_operation(interaction, title = "turn page")
                raise
