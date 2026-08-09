from typing import Self

from bot.ui import ActionRow, LayoutView, TextDisplay, VisibleLargeSeparator
from core.responses import format_message

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Leave Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class WarningView(LayoutView):
    def __init__(self, *, subtitle : str, footer : str, row : ActionRow[LayoutView | Self]) -> None:
        super().__init__()
        self.add_items(
            TextDisplay[Self](
                format_message(
                    msg_type = "warning",
                    title    = "Warning,",
                    subtitle = subtitle,
                    footer   = footer,
                    override = True,
                ),
            ),
            VisibleLargeSeparator[Self](),
            row,
        )
