from typing import TYPE_CHECKING, Self, final, override

from discord.ui import ActionRow, Button, Modal, TextInput, button

from bot import Interaction
from bot.ui import LayoutView, TextDisplay, VisibleLargeSeparator, green, grey

from .exceptions import send_bad_operation, send_bad_request

if TYPE_CHECKING:
    from discord import Message

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Paginator
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class PageJumpModal(Modal, title = "Jump to Page"):
    page_input : TextInput[Self] = TextInput(
        label       = "Enter a page number.",
        placeholder = "ex: 5",
        min_length  = 1,
        max_length  = 2,
    )

    def __init__(self, paginator : "Paginator") -> None:
        super().__init__()
        self.paginator = paginator

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
        data                   : list[str],
        *,
        data_name              : str,
        show_page              : bool       = True,
        per_page               : int        = 10,
        timeout                : int | None = None,
        reset_upon_interaction : bool       = True,
    ) -> None:
        super().__init__(timeout = timeout)
        self.data                         = data
        self.data_name                    = data_name
        self.response : Message | None    = None
        self.pages                        = [
            "\n".join(data[i:i + per_page])
            for i in range(0, len(data), per_page)
        ] or ["No content available."]
        self.current_page                 = 0
        self.display  : TextDisplay[Self] = TextDisplay(self.pages[0])
        self.original_timeout             = timeout
        self.reset_upon_interaction       = reset_upon_interaction
        self.page_row                     = PageRow(self) if len(self.pages) >= 2 else None

        self.add_item(self.display)

        # ⸻ Only add a separator if there are buttons below it.

        if self.page_row:
            self.add_item(VisibleLargeSeparator())
            if show_page:
                self.add_text(self.get_page_footer())
            self.add_item(self.page_row)

    @override
    async def interaction_check(self, interaction : Interaction) -> bool:
        if self.reset_upon_interaction and self.timeout:
            self.timeout = self.original_timeout
        return True

    @override
    async def on_timeout(self) -> None:

        # ⸻ Recursively disable every button.

        for child in self.walk_children():
            if isinstance(child, Button):
                child.disabled = True

        if self.response:
            await self.response.edit(view = self)

    def get_page_footer(self) -> str:
        return f"-# Page {self.current_page + 1} of {len(self.pages)} | {len(self.data)} {self.data_name}"

    async def turn(self, interaction : Interaction, target : int) -> None:
        if 0 <= target < len(self.pages):
            self.current_page = target
            self.clear_items()
            self.display = TextDisplay(self.pages[target])
            self.add_item(self.display)
            self.add_item(VisibleLargeSeparator())
            self.add_text(self.get_page_footer())

            if self.page_row:
                self.page_row.update_button_states()
                self.add_item(self.page_row)

            await interaction.response.edit_message(view = self)
