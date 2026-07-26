from typing import Self, final

from discord import AllowedMentions, Message
from discord.abc import Messageable
from discord.ext import commands
from discord.ui import TextDisplay
from discord.utils import escape_markdown, format_dt, utcnow

from bot import Cordex
from bot.ui import Container, LayoutView, VisibleLargeSeparator
from commands.bot_owner.eval import eval_message_ids
from constants import (
    COLOR_GREY,
    MAIN_GUILD_ID,
    MESSAGE_EDIT_LOG_CHANNEL_ID,
    WAPPLE_CHAIN_CHANNEL_ID,
)
from core.utilities import format_table

from . import (
    WAPPLE_PATTERN,
    channel_display,
    format_attachments,
    is_directorship_channel,
    truncate_text,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Message Edit Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class MessageEditHandler(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_message_edit")
    async def message_edit_handler(self, before : Message, after : Message) -> None:
        author  = before.author
        channel = after.channel

        # ⸻ Block the bot itself

        if author.bot or author == self.bot.user:
            return

        # ⸻ Block bots

        if author.bot:
            return

        # ⸻ Block non-guild messages or messages not in the main guild

        if before.guild is None or before.guild.id != MAIN_GUILD_ID:
            return

        # ⸻ Block non-wapple text in wapple channel

        if before.channel.id == WAPPLE_CHAIN_CHANNEL_ID and not WAPPLE_PATTERN.fullmatch((after.content or "").strip()):
            await after.delete()
            return

        # ⸻ Eval command editing

        if before.id in eval_message_ids:

            # ⸻ Remove our old reactions

            if self.bot.user is not None:
                for reaction in before.reactions:
                    if reaction.me:
                        await reaction.remove(self.bot.user)

            # ⸻ Reinvoke the command

            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)

            # ⸻ Remove our old response (done after the reinvocation since faster reevaluation is better)

            if (old_response_id := eval_message_ids.pop(before.id, None)) is not None:
                old_msg = await before.channel.fetch_message(old_response_id)
                await old_msg.delete()

            return

        # ⸻ Block nessage logging of directorship channels

        if is_directorship_channel(before.channel):
            return

        # ⸻ Edit message logging

        before_files = [a.url for a in before.attachments]
        after_files  = [a.url for a in after.attachments]

        if before.content == after.content and before_files == after_files:
            return

        log_channel = before.guild.get_channel(MESSAGE_EDIT_LOG_CHANNEL_ID)
        if not isinstance(log_channel, Messageable):
            return

        @final
        class _EditView(LayoutView):
            container = Container[Self](
                TextDisplay(f"# Message Edited | {format_dt(after.edited_at or utcnow(), style = "F")}"),
                TextDisplay(
                    format_table(
                        {
                            "Author"      : f"{author.mention} | {author.id}",
                            "Channel"     : f"{channel_display(after.channel)} | {channel.id}",
                            "Attachments" : format_attachments(after.attachments),
                        },
                    ),
                ),
                VisibleLargeSeparator(),
                TextDisplay(
                    (
                        f"### Before\n"
                        f"{truncate_text(escape_markdown(before.content) or "[No content, likely an embed or attachment]", max_length = 1024)}"
                    ),
                ),
                TextDisplay(
                    (
                        f"### After\n"
                        f"{truncate_text(escape_markdown(after.content) or "[No content, likely an embed or attachment]", max_length = 1024)}"
                    ),
                ),
                color = COLOR_GREY,
            )

        await log_channel.send(view = _EditView(), allowed_mentions = AllowedMentions.none())

        await self.bot.process_commands(after)

async def setup(bot : Cordex) -> None:
    cog = MessageEditHandler(bot)
    await bot.add_cog(cog)
