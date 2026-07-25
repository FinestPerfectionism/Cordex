from typing import Self, final, override

from discord import Color
from discord.ui import ActionRow, Button, Item, Modal, TextInput, button

from bot import Interaction
from bot.ui import (
    Container,
    LayoutView,
    TextDisplay,
    VisibleLargeSeparator,
    green,
)

from .exceptions import send_bad_operation, send_bad_request

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Paginator
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class _PageJumpModal(Modal, title = "Jump to Page"):
    page_input : TextInput[Self]

    def __init__(self, paginator : "Paginator") -> None:
        super().__init__()
        self.paginator = paginator

        max_digits = len(str(len(paginator.pages)))

        self.page_input = TextInput(
            label       = "Enter a page number.",
            placeholder = "ex: 5",
            min_length  = 1,
            max_length  = max_digits,
        )
        self.add_item(self.page_input)

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        try:
            page = int(self.page_input.value) - 1

            # ⸻ You're already on this page!

            if page == self.paginator.current_page:
                return await send_bad_request(
                    interaction,
                    title    = "jump to page",
                    subtitle = "You are already viewing this page.",
                )

            # ⸻ Success..?

            if 0 <= page < len(self.paginator.pages):
                await self.paginator.turn(interaction, page)

            # ⸻ Must be within the bounds of 1 and the highest page!

            else:
                await send_bad_request(
                    interaction,
                    title    =  "jump to page",
                    subtitle = f"Please enter a page between 1 and {len(self.paginator.pages)}.",
                )

        # ⸻ Must be a positive integer greater than or equal to 1!

        except ValueError:
            await send_bad_request(
                interaction,
                title    = "jump to page",
                subtitle = "Please enter a positive integer greater than or equal to one.",
            )

        # ⸻ Unhandled error.

        except Exception:
            await send_bad_operation(interaction, title = "jump to page")
            raise

@final
class _PageRow(ActionRow["Paginator"]):
    def __init__(self, paginator : "Paginator") -> None:
        super().__init__()
        self.paginator = paginator

        # ⸻ Remove the first, page, and last buttons if we have 2 pages, and remove only the page button if we have 3 pages.

        if len(paginator.pages) == 2:
            self.remove_item(self.btn_first)
            self.remove_item(self.btn_page)
            self.remove_item(self.btn_last)
        elif len(paginator.pages) == 3:
            self.remove_item(self.btn_page)

        # ⸻ Update.

        self.update_states()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # update_states
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def update_states(self) -> None:
        current = self.paginator.current_page
        total   = len(self.paginator.pages)

        is_first = (current == 0)
        is_last  = (current == total - 1)

        if total >= 3:
            self.btn_first.disabled = is_first
            self.btn_last.disabled  = is_last
            self.btn_page.label     = f"{current + 1} / {total}"

        self.btn_backward.disabled = is_first
        self.btn_forward.disabled  = is_last

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Buttons
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @button(label = "<<")
    async def btn_first(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, 0)

    @button(label = "<")
    async def btn_backward(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, self.paginator.current_page - 1)

    @button(label = "1 / 1", style = green)
    async def btn_page(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await interaction.response.send_modal(_PageJumpModal(self.paginator))

    @button(label = ">")
    async def btn_forward(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, self.paginator.current_page + 1)

    @button(label = ">>")
    async def btn_last(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, len(self.paginator.pages) - 1)

@final
class Paginator(LayoutView):
    def __init__(
        self,
        title     : str,
        data      : list[str | Item[LayoutView]],
        /,
        *,
        data_name : str   | None = None,
        per_page  : int          = 5,
        color     : Color | None = None,
        container : bool         = False,
        force     : bool         = False,
    ) -> None:
        super().__init__(timeout = 600)
        self._title     = title
        self._data      = data
        self._data_name = data_name
        self._per_page  = per_page
        self._color     = color
        self._container = container
        self._force     = force

        self.pages        = [
            data[i:i + per_page]
            for i in range(0, len(data), per_page)
        ] or [["No content available."]]
        self.current_page = 0
        self._page_row    = _PageRow(self) if len(self.pages) >= 2 else None

        self._above_items : list[Item[LayoutView]] = []
        self._below_items : list[Item[LayoutView]] = []

        # ⸻ color is dependent on container.

        if color and not container:
            error = "color is dependent on container"
            raise ValueError(error)

        # ⸻ Only add a separator if there are buttons below it.

        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # _get_page_footer
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def _get_page_footer(self) -> str:
        return f"-# Page {self.current_page + 1} of {len(self.pages)} | {len(self._data)} {self._data_name}"

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
    # update_data
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def update_data(self, title : str, data : list[str | Item[LayoutView]]) -> None:
        self._title       = title
        self._data        = data
        self.current_page = 0

        self.pages = [
            data[i:i + self._per_page]
            for i in range(0, len(data), self._per_page)
        ] or [["No content available."]]

        self._page_row = _PageRow(self) if len(self.pages) >= 2 else None

        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # _render
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def _render(self) -> None:
        self.clear_items()

        # ⸻ Add all items above.

        for item in self._above_items:
            self.add_item(item)

        page_items : list[Item[LayoutView]] = []

        if self._force:
            page_items = [
                TextDisplay(item)
                if isinstance(item, str) else item
                for item in self.pages[self.current_page]
            ]
        else:
            accumulated : list[str] = []

            for item in self.pages[self.current_page]:
                if isinstance(item, str):
                    accumulated.append(item)
                else:
                    if accumulated:
                        page_items.append(TextDisplay("\n".join(accumulated)))
                        accumulated.clear()
                    page_items.append(item)

            if accumulated:
                page_items.append(TextDisplay("\n".join(accumulated)))

        items : list[TextDisplay[LayoutView] | VisibleLargeSeparator | _PageRow | Item[LayoutView]] = [
            TextDisplay(self._title),
            VisibleLargeSeparator(),
            *page_items,
            VisibleLargeSeparator(),
            TextDisplay(self._get_page_footer()),
        ]

        if self._page_row:
            self._page_row.update_states()
            items.append(self._page_row)

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
            self.current_page = target
            self._render()

            try:
                await interaction.response.edit_message(view = self)
            except Exception:
                await send_bad_operation(interaction, title = "turn page")
                raise
