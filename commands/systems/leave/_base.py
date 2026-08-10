from re import compile
from typing import Self

from bot.ui import ActionRow, LayoutView, TextDisplay, VisibleLargeSeparator
from core.responses import format_message

STAFF_NAME_PATTERN = compile(r"^(?:[LJS]\.\s(?:Director|Admin|Mod)|[SJ]A\/[SJ][MM])\s\|\s.+$")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Leave Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class WarningView(LayoutView):
    def __init__(self, *, subtitle : str, footer : str, row : ActionRow[LayoutView | Self]) -> None:
        super().__init__()
        self._footer  : str               = footer
        self._text    : str               = subtitle
        self._display : TextDisplay[Self] = TextDisplay[Self](
            format_message(
                msg_type = "warning",
                title    = "Warning,",
                subtitle = subtitle,
                footer   = footer,
                override = True,
            ),
        )

        self.add_items(
            self._display,
            VisibleLargeSeparator[Self](),
            row,
        )

    @property
    def text(self) -> str:
        return self._display.content

    @text.setter
    def text(self, value : str) -> None:
        self._display.content = format_message(
            msg_type = "warning",
            title    = "Warning,",
            subtitle = value,
            footer   = self._footer,
            override = True,
        )

    @property
    def footer(self) -> str:
        return self._footer

    @footer.setter
    def footer(self, value : str) -> None:
        self._display.content = format_message(
            msg_type = "warning",
            title    = "Warning,",
            subtitle = self._text,
            footer   = value,
            override = True,
        )
