from typing import Protocol, final

from discord import Color

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

__all__ = ["NamedPaginator"]

type _ItemsOrStrList = list[str | Item[LayoutView]]
type _NamesList      = list[dict[str, _ItemsOrStrList]]
type _ItemsList      = list[Item[LayoutView]]

class _InteractionCallback(Protocol):
    async def __call__(self, interaction : Interaction) -> None: ...

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Named Paginator
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class _NameRow(ActionRow["NamedPaginator"]):
    def __init__(self, paginator : "NamedPaginator", indices : range) -> None:
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
            entry = self.paginator.pages[index]
            name  = next(iter(entry))

            is_current = index == self.paginator.current_page
            btn : Button[LayoutView] = (
                Button(label = name, style = blurple, disabled = is_current)
                if is_current
                else Button(label = name)
            )
            btn.callback = self._make_callback(index)
            self.add_item(btn)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # _make_callback
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def _make_callback(self, index : int) -> _InteractionCallback:
        async def callback(interaction : Interaction) -> None:
            await self.paginator.turn(interaction, index)
        return callback

@final
class NamedPaginator(LayoutView):
    def __init__(
        self,
        data      : _NamesList,
        /,
        *,
        color     : Color | None = None,
        container : bool         = False,
        force     : bool         = False,
    ) -> None:
        super().__init__()
        self._data      = data
        self._color     = color
        self._container = container
        self._force     = force

        # ⸻ data must contain more than one dictionary.

        if len(data) == 1:
            error = "data must contain more than one dictionary"
            raise ValueError(error)

        self.pages        = data or [{"No content available." : ["No content available."]}]
        self.current_page = 0
        self._name_rows   = [
            _NameRow(self, range(i, min(i + 5, len(self.pages))))
            for i in range(0, len(self.pages), 5)
        ] if len(self.pages) >= 2 else []

        self._above_items : _ItemsList = []
        self._below_items : _ItemsList = []

        # ⸻ color is dependent on container.

        if color and not container:
            error = "color is dependent on container"
            raise ValueError(error)

        # ⸻ Render.

        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_above
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_above(self, *items : Item[LayoutView]) -> None:
        self._above_items.extend(items)
        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_below
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_below(self, *items : Item[LayoutView]) -> None:
        self._below_items.extend(items)
        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # _render
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def _render(self) -> None:
        self.clear_items()

        # ⸻ Add all items above.

        for item in self._above_items:
            self.add_item(item)

        entry     = self.pages[self.current_page]
        name      = next(iter(entry))
        page_data = entry[name]

        page_items : _ItemsList = []

        if self._force:
            page_items = [
                TextDisplay(item)
                if isinstance(item, str) else item
                for item in page_data
            ]
        else:
            accumulated : list[str] = []

            for item in page_data:
                if isinstance(item, str):
                    accumulated.append(item)
                else:
                    if accumulated:
                        page_items.append(TextDisplay("\n".join(accumulated)))
                        accumulated.clear()
                    page_items.append(item)

            if accumulated:
                page_items.append(TextDisplay("\n".join(accumulated)))

        items : _ItemsList = [*page_items, VisibleLargeSeparator()]

        for name_row in self._name_rows:
            name_row.update_states()
            items.append(name_row)

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
            self._render()

            try:
                await interaction.response.edit_message(view = self)
            except Exception:
                self.current_page = previous_page
                self._render()
                await send_bad_operation(interaction, title = "turn page")
                raise
