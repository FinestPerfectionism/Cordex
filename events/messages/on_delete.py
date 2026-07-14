from discord import AuditLogAction, Embed, Member, Message, User
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

class MessageDeleteHandler(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot : Cordex = bot

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

        deleter = "Unknown"
        async for entry in message.guild.audit_logs(limit = 5, action = AuditLogAction.message_delete):
            if not isinstance(entry.target, User | Member):
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

        embed = Embed(
            title     = "Message Deleted",
            color     = COLOR_RED,
            timestamp = utcnow(),
        )
        embed.add_field(
            name   = "Author",
            value  = f"`{message.author}`\n`{message.author.id}`",
            inline = True,
        )
        embed.add_field(
            name   = "Deleted By",
            value  = deleter,
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
        embed.set_footer(text = 'Please note that the "Deleted By" section guesses by checking the audit log, and may not always be accurate')
        await log_channel.send(embed = embed)

async def setup(bot : Cordex) -> None:
    cog = MessageDeleteHandler(bot)
    await bot.add_cog(cog)
