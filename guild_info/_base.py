from discord.ui import ActionRow, Container, LayoutView, TextDisplay

from core.utilities import (
    HiddenSmallSeparator,
    VisibleLargeSeparator,
    VisibleSmallSeparator,
    format_values,
)


class InfoHeaderSection(LayoutView):
    def __init__(self, *, title : str, description : str, note : str | None = None) -> None:
        super().__init__()

        note_line = f"-# **Note:** {note}." if note else ""

        _ = self.add_item(
            Container(
                TextDisplay(

                        f"# Welcome to {title}!\n"
                        f"{description}.\n"
                        f"{note_line}",

                ),
            ),
        )

class InfoPrimarySection(LayoutView):
    def __init__(self, *, title : str, text : str | None = None, timestamp : int, writers : list[str]) -> None:
        super().__init__(timeout = None)

        self.container : Container[LayoutView] = Container(
            TextDisplay(

                   f"# {title}\n"
                   f"{title} last updated <t:{timestamp}:D>.\n"
                    "-# All below is subject to change at any time based on Directorate decision or structural updates.\n"
                   f"-# Assembled by the Directorate team. Primarily written by {format_values(writers)}.\n",

            ),
            HiddenSmallSeparator(),
            VisibleSmallSeparator(),
            HiddenSmallSeparator(),
        )

        if text is not None:
            _ = self.container.add_item(TextDisplay(text))

        _ = self.add_item(self.container)
        self.has_row : bool = False

    def add_text(self, text : str) -> None:
        if self.has_row:
            _ = self.container.add_item(VisibleLargeSeparator())
            self.has_row = False

        _ = self.container.add_item(TextDisplay(text))

    def add_row(self, row : ActionRow[LayoutView]) -> None:
        _ = self.container.add_item(VisibleLargeSeparator())
        _ = self.container.add_item(row)
        self.has_row = True

class InfoSecondarySection(LayoutView):
    def __init__(self, *, text : str | None = None) -> None:
        super().__init__(timeout = None)

        self.container : Container[LayoutView] = Container()

        if text is not None:
            _ = self.container.add_item(TextDisplay(text))

        _ = self.add_item(self.container)
        self.has_row : bool = False

    def add_text(self, text : str) -> None:
        if self.has_row:
            _ = self.container.add_item(VisibleLargeSeparator())
            self.has_row = False

        _ = self.container.add_item(TextDisplay(text))

    def add_row(self, row : ActionRow[LayoutView]) -> None:
        _ = self.container.add_item(VisibleLargeSeparator())
        _ = self.container.add_item(row)
        self.has_row = True
