from typing import Self, final

from discord import AllowedMentions, Message
from discord.abc import Messageable
from discord.ext import commands

from bot import Cordex
from bot.ui import Container, LayoutView, TextDisplay, VisibleLargeSeparator
from constants import (
    BOT_OWNER_ID,
    COLOR_RED,
    MAIN_GUILD_ID,
    MESSAGE_DELETE_LOG_CHANNEL_ID,
)
from core.utilities import format_now, format_table

from . import (
    channel_display,
    clean_and_truncate,
    format_attachments,
    is_directorship_channel,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Message Delete Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class MessageDeleteHandler(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_message_delete")
    async def message_delete_handler(self, message : Message) -> None:
        content     = message.content
        attachments = message.attachments
        author      = message.author
        channel     = message.channel
        guild       = message.guild

        # ⸻ Block bots and the bot itself.

        if author.bot or author == self.bot.user:
            return

        # ⸻ Block non-guild messages or messages not in the main guild

        if guild is None or guild.id != MAIN_GUILD_ID:
            return

        # ⸻ Block evaluations.

        if content.startswith(".eval") and author.id == BOT_OWNER_ID:
            return

        if is_directorship_channel(channel):
            return

        log_channel = guild.get_channel(MESSAGE_DELETE_LOG_CHANNEL_ID)
        if not isinstance(log_channel, Messageable):
            return

        @final
        class DeleteView(LayoutView):
            container = Container[Self](
                TextDisplay(f"# Message Deleted | {format_now("F")}"),
                TextDisplay(
                    format_table(
                        {
                            "Author"  : f"{author.mention} | {author.id}",
                            "Channel" : channel_display(channel),
                        },
                    ),
                ),
                color = COLOR_RED,
            )

            if attachments:
                container.add_items(
                    VisibleLargeSeparator(),
                    TextDisplay(
                        (
                            "### Attachments\n"
                           f"{format_attachments(attachments)}"
                        ),
                    ),
                )

            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    (
                        "### Content\n"
                       f"{clean_and_truncate((content) or "[No content, likely an embed or attachment]")}"
                    ),
                ),
            )

        await log_channel.send(view = DeleteView(), allowed_mentions = AllowedMentions.none())

async def setup(bot : Cordex) -> None:
    cog = MessageDeleteHandler(bot)
    await bot.add_cog(cog)
