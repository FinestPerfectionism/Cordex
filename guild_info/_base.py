from logging import getLogger as get_logger
from typing import TYPE_CHECKING, cast

from discord import AllowedMentions, File, HTTPException, TextChannel, Thread
from discord.ui import ActionRow, Button, Container, LayoutView, TextDisplay
from discord.utils import format_dt, utcnow

from bot.ui import (
    ButtonSection,
    HiddenSmallSeparator,
    VisibleLargeSeparator,
    VisibleSmallSeparator,
    link,
)
from constants import STANDSTILL_EMOJI
from core.utilities import format_values

log = get_logger("Cordex")

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Guild Information Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# ensure_views
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def ensure_views(
    bot        : "Cordex",
    channel_id : int,
    views      : list[LayoutView],
    files      : list[list[File]] | None = None,
) -> None:
    log.info("Starting view ensurement for channel: %s", channel_id)
    channel = bot.get_channel(channel_id)

    if channel is None:
        channel = await bot.fetch_channel(channel_id)

    if not isinstance(channel, TextChannel | Thread):
        error = f"{channel_id} is not a text channel or thread."
        raise TypeError(error)

    cursor = await bot.db.execute(
        """
        SELECT message_id
        FROM guild_info
        WHERE channel_id = ?
        ORDER BY position
        """,
        [str(channel_id)],
    )

    rows = await cursor.fetchall()
    await cursor.close()

    message_ids : list[int] = [int(cast(int | str, row[0])) for row in rows]

    if len(message_ids) == len(views):
        for message_id in message_ids:
            try:
                await channel.fetch_message(message_id)
            except HTTPException:
                break
        else:
            message_count = 0

            async for _ in channel.history(limit = None):
                message_count += 1

            if message_count == len(views):
                log.info("View ensurement finished. No changes needed for channel: %s", channel_id)
                return

    async for message in channel.history(limit = None):
        try:
            await message.delete()
        except HTTPException:
            log.exception(
                "Failed to delete message %s in #%s.",
                message.id,
                channel.id,
            )

    new_message_ids : list[int] = []

    for index, view in enumerate(views):
        view_files : list[File] = files[index] if files is not None else []
        message                 = await channel.send(
            view             = view,
            files            = view_files,
            allowed_mentions = AllowedMentions.none(),
        )

        new_message_ids.append(message.id)

    await bot.db.execute(
        """
        DELETE FROM guild_info
        WHERE channel_id = ?
        """,
        [str(channel_id)],
    )

    await bot.db.executemany(
        """
        INSERT INTO guild_info (
            channel_id,
            position,
            message_id
        )
        VALUES (?, ?, ?)
        """,
        [
            (channel_id, position, message_id)
            for position, message_id in enumerate(new_message_ids)
        ],
    )

    await bot.db.commit()
    log.info("View alignment finished. Rebuilt views for channel: %s", channel_id)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# TOS Button
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class TOSButton(Button[LayoutView]):
    def __init__(self) -> None:
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
        note      : str                | None = None,
        authors   : list[str]          | None = None,
        button    : Button[LayoutView] | None = None,
    ) -> None:
        super().__init__(timeout = None)

        if note is None and authors is not None:
            note = (
                "-# All below is subject to change at any time based on Directorate decision or structural updates.\n"
               f"-# Assembled by the Directorate team. Primarily written by {format_values(authors)}.\n"
            )

        self.container      : Container[LayoutView]        = Container()
        self.last_added_row : ActionRow[LayoutView] | None = None

        if button is not None:
            self.container.add_item(
                ButtonSection(
                    f"# {title}",
                    button = button,
                ),
            )
            header_text = ""
        else:
            header_text = f"# {title}\n\n"

        self.container.add_item(
            TextDisplay(
                (
                    f"{header_text}"
                    f"{title} last updated {format_dt(utcnow(), style = "F")}.\n"
                    f"{note}"
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

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Info Support Section
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class InfoSupportSection(LayoutView):
    def __init__(
        self,
        *,
        title       : str,
        description : str,
        text        : str,
        note        : str,
        footer      : str,
        button      : Button[LayoutView],
    ) -> None:
        super().__init__(timeout = None)

        self.add_item(
            Container(
                ButtonSection(
                    f"# {title}",
                    button = TOSButton(),
                ),
                ButtonSection(
                    f"{description}.",
                    button = button,
                ),
                HiddenSmallSeparator(),
                VisibleSmallSeparator(),
                HiddenSmallSeparator(),
                TextDisplay(
                    (
                        f"{text}.\n\n"
                        f"**Note:** {note}.\n\n"
                        f"{footer}."
                    ),
                ),
            ),
        )
