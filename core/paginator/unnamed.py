# ruff: file-ignore[private-member-access]
# pyright: reportPrivateUsage = false

from contextlib import suppress
from typing import Self, final, override
from warnings import warn

from discord import Color, HTTPException, Message, NotFound

from bot import Interaction
from bot.ui import (
    ActionRow,
    Button,
    Container,
    Item,
    Label,
    LayoutView,
    Modal,
    TextDisplay,
    TextInput,
    VisibleLargeSeparator,
    button,
    green,
)
from core.exceptions import send_bad_operation, send_bad_request

__all__ = ["UnnamedPaginator"]

type _ItemsList      = list[Item[LayoutView]]
type _ItemsOrStrList = list[str | Item[LayoutView]]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Unnamed Paginator
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class _PageJumpModal(Modal, title = "Jump to Page"):
    def __init__(self, paginator : UnnamedPaginator) -> None:
        super().__init__()
        self.paginator = paginator

        max_digits = len(str(len(paginator.pages)))

        self._page_input = TextInput[Self](
            placeholder = "ex: 5",
            min_length  = 1,
            max_length  = max_digits,
        )
        self.page_input  = Label[Self](
            text        = "Enter a page number.",
            description = "Enter a positive integer greater than or equal to one.",
            component   = self._page_input,
        )
        self.add_item(self.page_input)

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        page = int(self._page_input.value) - 1

        # ⸻ You're already on this page!

        if page == self.paginator.current_page:
            await send_bad_request(
                interaction,
                title    = "jump to page",
                subtitle = "You are already viewing this page",
            )
            return
        try:

            # ⸻ Success..?

            if 0 <= page < len(self.paginator.pages):
                await self.paginator._turn(interaction, page)

            # ⸻ Must be within the bounds of 1 and the highest page!

            else:
                await send_bad_request(
                    interaction,
                    title    =  "jump to page",
                    subtitle = f"Please enter a page between 1 and {len(self.paginator.pages)}",
                )

        # ⸻ Must be a positive integer greater than or equal to 1!

        except ValueError:
            await send_bad_request(
                interaction,
                title    = "jump to page",
                subtitle = "Please enter a positive integer greater than or equal to one",
            )

        # ⸻ Unhandled error.

        except Exception:
            await send_bad_operation(interaction, title = "jump to page")
            raise


@final
class _PageRow(ActionRow["UnnamedPaginator"]):
    def __init__(self, paginator : UnnamedPaginator) -> None:
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
        await self.paginator._turn(interaction, 0)

    @button(label = "<")
    async def btn_backward(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator._turn(interaction, self.paginator.current_page - 1)

    @button(label = "1 / 1", style = green)
    async def btn_page(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await interaction.response.send_modal(_PageJumpModal(self.paginator))

    @button(label = ">")
    async def btn_forward(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator._turn(interaction, self.paginator.current_page + 1)

    @button(label = ">>")
    async def btn_last(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await self.paginator._turn(interaction, len(self.paginator.pages) - 1)


class UnnamedPaginator(LayoutView):
    """
    Paginate a list of data cleanly using buttons.

    Parameters
    ----------
    title : `str`
        The title of the paginator.
    data : ItemsOrStrList`
        The data to paginate.
    /
    *
    data_name : str
        The name of the data.
    per_page : int = 5
        The amount of data to display per page. Defaults to 5.
    color : Color | None = None
        The color of the container. Dependent on the `container` parameter.
    container : bool = False
        Whether the paginator should be in a Container.
    force : bool = False
        Whether multiple strings passed into data will be concatenated with newlines instead of TextDisplays.
    timeout : int | None = 600
        The amount of seconds to pass before timing out, disabling all buttons and selects. If None, the paginator will never time out.

    Raises
    ------
    ValueError
        You passed 'color' without passing 'container'
    """

    def __init__(
        self,
        title     : str,
        data      : _ItemsOrStrList,
        /,
        *,
        data_name : str,
        per_page  : int          = 5,
        color     : Color | None = None,
        container : bool         = False,
        force     : bool         = False,
        timeout   : int   | None = 600,
    ) -> None:
        super().__init__(timeout = timeout)
        self.message : Message | None = None

        self._title     : str             = title
        self._data      : _ItemsOrStrList = data
        self._data_name : str   | None    = data_name
        self._per_page  : int             = per_page
        self._color     : Color | None    = color
        self._container : bool            = container
        self._force     : bool            = force

        self.pages        : list[_ItemsOrStrList] = [
            data[i : i + per_page]
            for i in range(0, len(data), per_page)
        ] or [["No content available."]]
        self.current_page : int                   = 0
        self._page_row    : _PageRow | None       = _PageRow(self) if len(self.pages) >= 2 else None

        self._above_items : _ItemsList = []
        self._over_items  : _ItemsList = []
        self._under_items : _ItemsList = []
        self._below_items : _ItemsList = []

        # ⸻ color is dependent on container.

        if color and not container:
            error = "color is dependent on container"
            raise ValueError(error)

        # ⸻ Render.

        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # on_timeout
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @override
    async def on_timeout(self) -> None:

        # ⸻ timeout without self.message.

        if self.timeout and not self.message:
            warn(
                "timeout was passed but there is no message to edit.",
                category   = UserWarning,
                stacklevel = 2,
            )

        if self.timeout is not None:
            for item in self.walk_children():
                if isinstance(item, Button):
                    item.disabled = True

        if self.message:
            try:
                await self.message.edit(view = self)
            except NotFound:
                pass
            except HTTPException:
                with suppress(HTTPException):
                    await self.message.delete()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # _get_page_footer
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def _get_page_footer(self) -> str:
        return f"-# Page {self.current_page + 1} of {len(self.pages)} | {len(self._data)} {self._data_name}"

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_above
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_above(self, *items : Item[LayoutView]) -> None:
        """
        Add items above the paginator.

        Parameters
        ----------
        *items : Item[LayoutView]
            The items to add above the paginator.
        """
        self._above_items.extend(items)
        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_over
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_over(self, *items : Item[LayoutView]) -> None:
        """
        Add items over the title of the paginator.

        Parameters
        ----------
        *items : Item[LayoutView]
            The items to add over the title of the paginator.
        """
        self._over_items.extend(items)
        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_under
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_under(self, *items : Item[LayoutView]) -> None:
        """
        Add items under the footer of the paginator.

        Parameters
        ----------
        *items : Item[LayoutView]
            The items to add under the footer of the paginator.
        """
        self._under_items.extend(items)
        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # add_below
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def add_below(self, *items : Item[LayoutView]) -> None:
        """
        Add items below the paginator.

        Parameters
        ----------
        *items : Item[LayoutView]
            The items to add below the paginator.
        """
        self._below_items.extend(items)
        self._render()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # update_data
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def update_data(self, title : str, data : _ItemsOrStrList) -> None:
        """
        Update the Paginator's data then re-render it.

        Parameters
        ----------
        title : str
            The paginator's new title.
        data : ItemsOrStrList
            The paginator's new data.
        """
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

        self.append_items(self._above_items)

        page_items : _ItemsList = []

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

        items : _ItemsList = [
            *self._over_items,
            TextDisplay(self._title),
            VisibleLargeSeparator(),
            *page_items,
            VisibleLargeSeparator(),
            TextDisplay(self._get_page_footer()),
        ]

        if self._page_row:
            self._page_row.update_states()
            items.append(self._page_row)

        items.extend(self._under_items)

        # ⸻ Add all items to the container if chosen or directly to the view if not.

        if self._container:
            self.add_item(Container(*items, color = self._color))
        else:
            self.append_items(items)

        # ⸻ Add all items below.

        self.append_items(self._below_items)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # turn
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def _turn(self, interaction : Interaction, target : int) -> None:
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
