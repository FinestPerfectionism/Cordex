from typing import Self, final, override

from discord.ui import ActionRow, Button, Item, Modal, TextInput, button

from bot import Interaction
from bot.ui import (
    Container,
    LayoutView,
    TextDisplay,
    VisibleLargeSeparator,
    green,
    grey,
)

from .exceptions import send_bad_operation, send_bad_request

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Paginator
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class PageJumpModal(Modal, title = "Jump to Page"):
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
class PageRow(ActionRow["Paginator"]):
    def __init__(self, paginator : "Paginator") -> None:
        super().__init__()
        self.paginator = paginator

        # ⸻ Only the forward and backward buttons matter.

        if len(paginator.pages) == 2:
            for button in [self.btn_first, self.btn_page, self.btn_last]:
                self.remove_item(button)

        # ⸻ Update.

        self.update_button_states()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # update_button_states
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def update_button_states(self) -> None:
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

    @button(label = "<<", style = grey)
    async def btn_first(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, 0)

    @button(label = "<", style = grey)
    async def btn_backward(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, self.paginator.current_page - 1)

    @button(label = "1 / 1", style = green)
    async def btn_page(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await interaction.response.send_modal(PageJumpModal(self.paginator))

    @button(label = ">", style = grey)
    async def btn_forward(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, self.paginator.current_page + 1)

    @button(label = ">>", style = grey)
    async def btn_last(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, len(self.paginator.pages) - 1)

@final
class Paginator(LayoutView):
    def __init__(
        self,
        title     : str,
        data      : list[str],
        /,
        *,
        data_name : str | None = None,
        show_page : bool       = True,
        per_page  : int        = 10,
        container : bool       = False,
    ) -> None:
        super().__init__(timeout = None)
        self.title     = title
        self.data      = data
        self.data_name = data_name
        self.container = container

        self.pages                       = [
            "\n".join(data[i:i + per_page])
            for i in range(0, len(data), per_page)
        ] or ["No content available."]
        self.current_page                = 0
        self.display : TextDisplay[Self] = TextDisplay(self.pages[0])
        self.page_row                    = PageRow(self) if len(self.pages) >= 2 else None

        self.above_items : list[Item[Self]] = []
        self.below_items : list[Item[Self]] = []

        if show_page and not data_name:
            error = "data_name must be provided if show_page is True"
            raise ValueError(error)

        # ⸻ Only add a separator if there are buttons below it.

        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # _get_page_footer
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def _get_page_footer(self) -> str:
        return f"-# Page {self.current_page + 1} of {len(self.pages)} | {len(self.data)} {self.data_name}"

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_above
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_above(self, *items : Item[Self]) -> None:
        self.above_items.extend(items)
        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_below
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_below(self, *items : Item[Self]) -> None:
        self.below_items.extend(items)
        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # _render
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def _render(self) -> None:
        self.clear_items()

        for item in self.above_items:
            self.add_item(item)

        items : list[TextDisplay[Self] | VisibleLargeSeparator | PageRow] = [
            TextDisplay(self.title),
            VisibleLargeSeparator(),
            TextDisplay(self.pages[self.current_page]),
            VisibleLargeSeparator(),
            TextDisplay(self._get_page_footer()),
        ]

        if self.page_row:
            self.page_row.update_button_states()
            items.append(self.page_row)

        if self.container:
            self.add_item(Container(*items))
        else:
            for item in items:
                self.add_item(item)

        for item in self.below_items:
            self.add_item(item)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # turn
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def turn(self, interaction : Interaction, target : int) -> None:
        if 0 <= target < len(self.pages):
            self.current_page = target
            self._render()

            await interaction.response.edit_message(view = self)
