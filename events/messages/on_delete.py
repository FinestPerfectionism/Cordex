from typing import Self, final

from discord import AllowedMentions, Message
from discord.abc import Messageable
from discord.ext import commands
from discord.ui import TextDisplay
from discord.utils import escape_markdown, format_dt, utcnow

from bot import Cordex
from bot.ui import Container, LayoutView, VisibleLargeSeparator
from constants import COLOR_RED, MAIN_GUILD_ID, MESSAGE_DELETE_LOG_CHANNEL_ID
from core.utilities import format_table

from . import (
    channel_display,
    format_attachments,
    is_directorship_channel,
    truncate_text,
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
        content = message.content
        author  = message.author

        # ⸻ Block the bot itself

        if author.bot or author == self.bot.user:
            return

        # ⸻ Block bots

        if author.bot:
            return

        # ⸻ Block non-guild messages or messages not in the main guild

        if message.guild is None or message.guild.id != MAIN_GUILD_ID:
            return

        if is_directorship_channel(message.channel):
            return

        log_channel = message.guild.get_channel(MESSAGE_DELETE_LOG_CHANNEL_ID)
        if not isinstance(log_channel, Messageable):
            return

        @final
        class _DeleteView(LayoutView):
            container = Container[Self](
                TextDisplay(f"# Message Deleted | {format_dt(message.edited_at or utcnow(), style = "F")}"),
                TextDisplay(
                    format_table(
                        {
                            "Author"      : f"{author.mention} | {author.id}",
                            "Channel"     : f"{channel_display(message.channel)} | {message.channel.id}",
                            "Attachments" : format_attachments(message.attachments),
                        },
                    ),
                ),
                VisibleLargeSeparator(),
                TextDisplay(truncate_text(escape_markdown(content) or "[No content, likely an embed or attachment]")),
                color = COLOR_RED,
            )

        await log_channel.send(view = _DeleteView(), allowed_mentions = AllowedMentions.none())

async def setup(bot : Cordex) -> None:
    cog = MessageDeleteHandler(bot)
    await bot.add_cog(cog)
