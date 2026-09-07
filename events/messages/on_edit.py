from typing import Self, final

from discord import AllowedMentions, Message
from discord.ext import commands
from discord.utils import format_dt, utcnow

from bot import Cordex
from bot.types import GuildMessagable
from bot.ui import (
    Button,
    ButtonSection,
    Container,
    LayoutView,
    TextDisplay,
    VisibleLargeSeparator,
    link,
)
from constants import COLOR_GREY
from core.permissions import is_bot_owner
from core.utilities import format_table

from ._base import attachments_display, channel_display, clean_and_truncate

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Message Edit Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class MessageEditHandler(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_message_edit")
    async def listener_delete_onmessageedit(self, before : Message, after : Message) -> None:
        author  = before.author
        guild   = before.guild
        channel = before.channel

        before_content = before.content

        after_content     = after.content
        after_attachments = after.attachments

        # ⸻ Block bots and the bot itself.

        if author.bot or author == self.bot.user:
            return

        # ⸻ Block non-guild messages.

        if guild is None or not isinstance(channel, GuildMessagable):
            return

        # ⸻ Block messages that do not belong to the current guild context.

        log_channel = await self.bot.config(guild).get_messages_edit_logging_channel()

        if log_channel is None or log_channel.guild != guild:
            return

        # ⸻ Block evaluations.

        if after_content.startswith(".eval") and is_bot_owner(author):
            return

        # ⸻ Edit message logging.

        before_files = [attachment.url for attachment in before.attachments]
        after_files  = [attachment.url for attachment in after.attachments]

        if before_content == after_content and before_files == after_files:
            return

        @final
        class EditView(LayoutView):
            container = Container[Self](
                TextDisplay(f"# Message Edited | {format_dt(after.edited_at or utcnow(), style = "F")}"),
                ButtonSection(
                    format_table(
                        {
                            "Author"  : f"{author.mention} | {author.id}",
                            "Channel" : channel_display(channel),
                        },
                    ),
                    button = Button(label = "Jump to Message", style = link, url = after.jump_url),
                ),
                color = COLOR_GREY,
            )

            if after_attachments:
                container.add_items(
                    VisibleLargeSeparator(),
                    TextDisplay(
                        "### Attachments\n"
                       f"{attachments_display(after_attachments)}",
                    ),
                )

            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    "### Before\n"
                   f"{clean_and_truncate(before_content) or "[No content, likely an embed or attachment]"}",
                ),
                TextDisplay(
                    "### After\n"
                   f"{clean_and_truncate(after_content) or "[No content, likely an embed or attachment]"}",
                ),
            )

        await log_channel.send(
            view             = EditView(),
            allowed_mentions = AllowedMentions.none(),
        )

async def setup(bot : Cordex) -> None:
    cog = MessageEditHandler(bot)
    await bot.add_cog(cog)
