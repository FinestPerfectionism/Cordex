from typing import final

from discord import Embed, Message
from discord.abc import Messageable
from discord.ext import commands
from discord.utils import utcnow

from bot import Cordex
from constants import COLOR_RED, MAIN_GUILD_ID, MESSAGE_DELETE_LOG_CHANNEL_ID

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

        embed = Embed(
            title     = "Message Deleted",
            color     = COLOR_RED,
            timestamp = utcnow(),
        )
        embed.add_field(
            name   =  "Author",
            value  = (
                f"`{message.author}`\n"
                f"`{message.author.id}`"
            ),
            inline = True,
        )
        embed.add_field(
            name   = "Channel",
            value  = channel_display(message.channel),
            inline = True,
        )
        content = message.content or "[No content, likely an embed or attachment]"
        embed.add_field(
            name   = "Content",
            value  = truncate_text(content),
            inline = True,
        )
        embed.add_field(
            name   = "Attachments",
            value  = format_attachments(message.attachments),
            inline = True,
        )
        await log_channel.send(embed = embed)

async def setup(bot : Cordex) -> None:
    cog = MessageDeleteHandler(bot)
    await bot.add_cog(cog)
