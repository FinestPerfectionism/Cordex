import contextlib

import discord
from discord import Message
from discord.abc import Messageable
from discord.ext import commands

from bot import Cordex
from commands.bot_owner.misc import eval_message_ids
from constants import (
    COLOR_GREY,
    MESSAGE_EDIT_LOG_CHANNEL_ID,
    WAPPLE_CHAIN_CHANNEL_ID,
)

from ._base import (
    WAPPLE_PATTERN,
    channel_display,
    format_attachments,
    is_directorship_channel,
    truncate_text,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Message Edit Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class MessageEditHandler(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot : Cordex = bot

    @commands.Cog.listener("on_message_edit")
    async def message_edit_handler(self, before : Message, after : Message) -> None:
        if before.author.bot or before.guild is None:
            return

        if before.channel.id == WAPPLE_CHAIN_CHANNEL_ID:
            content = (after.content or "").strip()
            if not WAPPLE_PATTERN.fullmatch(content):
                with contextlib.suppress(discord.HTTPException):
                    await after.delete()
                return

        if before.id in eval_message_ids:
            await before.clear_reactions()
            
            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)
            
            old_res_id = eval_message_ids.pop(before.id, None)
            if old_res_id is not None:
                old_msg = await before.channel.fetch_message(old_res_id)
                await old_msg.delete()
                
            return

        if is_directorship_channel(before.channel):
            return

        before_files = [a.url for a in before.attachments]
        after_files  = [a.url for a in after.attachments]

        if before.content == after.content and before_files == after_files:
            return

        log_channel = before.guild.get_channel(MESSAGE_EDIT_LOG_CHANNEL_ID)
        if not isinstance(log_channel, Messageable):
            return

        embed = discord.Embed(
            title     = "Message Edited",
            color     = COLOR_GREY,
            timestamp = after.edited_at or discord.utils.utcnow(),
        )
        _ = embed.add_field(
            name   =  "Edited By",
            value  = f"`{before.author}`\n`{before.author.id}`",
            inline = True,
        )
        _ = embed.add_field(
            name   = "Channel",
            value  = channel_display(before.channel),
            inline = True,
        )
        before_text = before.content or "[No content]"
        after_text  = after.content  or "[No content]"
        _ = embed.add_field(
            name   = "Before",
            value  = truncate_text(before_text),
            inline = True,
        )
        _ = embed.add_field(
            name   = "After",
            value  = truncate_text(after_text),
            inline = True,
        )
        _ = embed.add_field(
            name   = "Attachments (After)",
            value  = format_attachments(after.attachments),
            inline = True,
        )
        _ = await log_channel.send(embed = embed)

        await self.bot.process_commands(after)

async def setup(bot : Cordex) -> None:
    cog = MessageEditHandler(bot)
    await bot.add_cog(cog)
