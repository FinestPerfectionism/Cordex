from datetime import datetime
from discord.ui import ActionRow, Button, Container, LayoutView, TextDisplay
from discord.utils import format_dt

from bot.ui import ButtonSection, HiddenSmallSeparator, VisibleLargeSeparator, VisibleSmallSeparator, link
from constants import STANDSTILL_EMOJI
from core.utilities import format_values

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Guild Information Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# TOS Button
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class TOSButton(Button[LayoutView]):
    def __init__(self):
        super().__init__(
            url   = "https://discord.com/terms",
            style = link,
            label = "Discord Terms of Service",
            emoji = STANDSTILL_EMOJI,
        )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Info Header Section
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class InfoHeaderSection(LayoutView):
    def __init__(self, *, title : str, description : str, note : str | None = None) -> None:
        super().__init__()

        note_line = f"-# **Note:** {note}." if note else ""

        self.add_item(
            Container(
                TextDisplay(
                    (
                        f"# Welcome to {title}!\n"
                        f"{description}.\n"
                        f"{note_line}"
                    ),
                ),
            ),
        )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Info Primary Section
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class InfoPrimarySection(LayoutView):
    def __init__(
        self,
        *,
        title     : str,
        text      : str                | None = None,
        timestamp : datetime,
        authors   : list[str],
        button    : Button[LayoutView] | None = None,
    ) -> None:
        super().__init__(timeout = None)

        self.container      : Container[LayoutView]        = Container()
        self.last_added_row : ActionRow[LayoutView] | None = None

        title_line = ""

        if button is not None:
            self.container.add_item(
                ButtonSection(
                    title,
                    button = button,
                ),
            )
        else:
            title_line = f"# {title}\n"

        self.container.add_item(
            TextDisplay(
                (
                   f"{title_line}"
                   f"{title} last updated {format_dt(timestamp, style = "F")}.\n"
                    "-# All below is subject to change at any time based on Directorate decision or structural updates.\n"
                   f"-# Assembled by the Directorate team. Primarily written by {format_values(authors)}.\n"
                ),
            ),
        )

        self.container.add_item(HiddenSmallSeparator())
        self.container.add_item(VisibleSmallSeparator())
        self.container.add_item(HiddenSmallSeparator())
        
        if text is not None:
            self.container.add_item(TextDisplay(text))

        self.add_item(self.container)

    def add_text(self, text : str) -> None:
        if self.last_added_row is not None:
            self.container.add_item(VisibleLargeSeparator())
            self.last_added_row = None

        self.container.add_item(TextDisplay(text))

    def add_row(self, row : ActionRow[LayoutView]) -> None:
        if len(self.container.children) > 0 and self.last_added_row is None:
            self.container.add_item(VisibleLargeSeparator())

        self.container.add_item(row)
        self.last_added_row = row

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Info Secondary Section
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class InfoSecondarySection(LayoutView):
    def __init__(self, *, text : str | None = None) -> None:
        super().__init__(timeout = None)

        self.container      : Container[LayoutView]        = Container()
        self.last_added_row : ActionRow[LayoutView] | None = None

        if text is not None:
            self.container.add_item(TextDisplay(text))
        
        self.add_item(self.container)

    def add_text(self, text : str) -> None:
        if self.last_added_row is not None:
            self.container.add_item(VisibleLargeSeparator())
            self.last_added_row = None

        self.container.add_item(TextDisplay(text))

    def add_row(self, row : ActionRow[LayoutView]) -> None:
        if len(self.container.children) > 0 and self.last_added_row is None:
            self.container.add_item(VisibleLargeSeparator())

        self.container.add_item(row)
        self.last_added_row = row
