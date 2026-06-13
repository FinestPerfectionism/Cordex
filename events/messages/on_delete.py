from typing import TYPE_CHECKING

import discord
from discord import AuditLogAction
from discord.ext import commands
from discord.utils import utcnow

from constants import COLOR_RED, MESSAGE_DELETE_LOG_CHANNEL_ID

from ._base import (
    channel_display,
    format_attachments,
    is_directorship_channel,
    truncate_text,
)

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Message Delete Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class MessageDeleteHandler(commands.Cog):
    def __init__(self, bot : "Cordex") -> None:
        super().__init__()
        self.bot : "Cordex" = bot

    @commands.Cog.listener("on_message_delete")
    async def message_delete_handler(self, message : discord.Message) -> None:
        if message.guild is None:
            return

        if is_directorship_channel(message.channel):
            return

        if message.author.bot:
            return

        log_channel = message.guild.get_channel(MESSAGE_DELETE_LOG_CHANNEL_ID)
        if not isinstance(log_channel, discord.abc.Messageable):
            return

        deleter = "Unknown"
        try:
            async for entry in message.guild.audit_logs(limit = 5, action = AuditLogAction.message_delete):
                if not isinstance(entry.target, discord.User | discord.Member):
                    continue
                if entry.target.id != message.author.id:
                    continue
                extra = entry.extra
                if extra is None:
                    continue

                if getattr(extra, "channel", None) != message.channel:
                    continue
                max_log_age_seconds = 5
                if (utcnow() - entry.created_at).total_seconds() > max_log_age_seconds:
                    continue
                if entry.user:
                    deleter = f"`{entry.user}`\n`{entry.user.id}`"
                break

        except (discord.Forbidden, discord.HTTPException):
            pass

        embed = discord.Embed(
            title     = "Message Deleted",
            color     = COLOR_RED,
            timestamp = utcnow(),
        )
        _ = embed.add_field(
            name   = "Author",
            value  = f"`{message.author}`\n`{message.author.id}`",
            inline = True,
        )
        _ = embed.add_field(
            name   = "Deleted By",
            value  = deleter,
            inline = True,
        )
        _ = embed.add_field(
            name   = "Channel",
            value  = channel_display(message.channel),
            inline = True,
        )
        content = message.content or "[No content, likely an embed or attachment]"
        _ = embed.add_field(
            name   = "Content",
            value  = truncate_text(content),
            inline = True,
        )
        _ = embed.add_field(
            name   = "Attachments",
            value  = format_attachments(message.attachments),
            inline = True,
        )
        _ = embed.set_footer(text = 'Please note that the "Deleted By" section guesses by checking the audit log, and may not always be accurate')
        _ = await log_channel.send(embed = embed)

async def setup(bot : "Cordex") -> None:
    cog = MessageDeleteHandler(bot)
    await bot.add_cog(cog)
