from typing import Self, final, override

from discord.ui import ActionRow, Button, LayoutView, Modal, TextInput, button

from bot import Interaction
from bot.ui import TextDisplay, VisibleLargeSeparator, green, grey

from .exceptions import send_bad_operation, send_bad_request

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
            p = int(self.page_input.value) - 1
            if p == self.paginator.current_page:
                return await send_bad_request(
                    interaction,
                    title    = "jump to page",
                    subtitle = "You are already viewing this page.",
                )
            if 0 <= p < len(self.paginator.pages):
                await self.paginator.turn(interaction, p)
            else:
                await send_bad_request(
                    interaction,
                    title    =  "jump to page",
                    subtitle = f"Please enter a page between 1 and {len(self.paginator.pages)}.",
                )
        except ValueError:
            await send_bad_request(
                interaction,
                title    = "jump to page",
                subtitle = "Please enter an integer.",
            )
        except Exception:
            await send_bad_operation(interaction, title = "jump to page")

@final
class PageRow(ActionRow["Paginator"]):
    def __init__(self, paginator : "Paginator") -> None:
        super().__init__()
        self.paginator = paginator

        if len(paginator.pages) == 2:
            for b in [self.btn_first, self.btn_page, self.btn_last]:
                self.remove_item(b)

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
        self.btn_previous.disabled = is_first
        self.btn_next.disabled     = is_last

    @button(label = "<<", style = grey)
    async def btn_first(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, 0)

    @button(label = "<", style = grey)
    async def btn_previous(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, self.paginator.current_page - 1)

    @button(label = "1 / 1", style = green)
    async def btn_page(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await interaction.response.send_modal(PageJumpModal(self.paginator))

    @button(label = ">", style = grey)
    async def btn_next(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, self.paginator.current_page + 1)

    @button(label = ">>", style = grey)
    async def btn_last(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator.turn(interaction, len(self.paginator.pages) - 1)

@final
class Paginator(LayoutView):
    def __init__(self, data : list[str], *, per_page : int) -> None:
        super().__init__(timeout = None)
        self.pages                       = ["\n".join(data[i:i + per_page]) for i in range(0, len(data), per_page)] or ["No content available."]
        self.current_page                = 0
        self.display : TextDisplay[Self] = TextDisplay(self.pages[0])

        self.add_item(self.display)
        self.page_row = PageRow(self) if len(self.pages) >= 2 else None

        if self.page_row:
            self.add_item(VisibleLargeSeparator())
            self.add_item(self.page_row)

    async def turn(self, interaction : Interaction, target : int) -> None:
        if 0 <= target < len(self.pages):
            self.current_page = target
            self.clear_items()
            self.display = TextDisplay(self.pages[target])
            self.add_item(self.display)
            self.add_item(VisibleLargeSeparator())

            if self.page_row:
                self.page_row.update_button_states()
                self.add_item(self.page_row)

            await interaction.response.edit_message(view = self)
