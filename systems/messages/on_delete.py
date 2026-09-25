from typing import Self, final

from discord import AllowedMentions, Message
from discord.ext import commands

from bot import Cordex
from bot.types import GuildMessagable
from bot.ui import Container, LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_RED
from core.utilities import format_now, format_table, is_bot_owner

from ._base import attachments_display, channel_display, clean_and_truncate

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Message Delete Logging
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class MessageDeleteLogging(commands.Cog):
    """Logs message deletion for guilds with it enabled."""

    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_message_delete")
    async def _listener_delete_messagedelete(self, message : Message) -> None:
        content     = message.content
        attachments = message.attachments
        author      = message.author
        channel     = message.channel
        guild       = message.guild

        # ⸻ Block bots and the bot itself.

        if author.bot or author == self.bot.user:
            return

        # ⸻ Block non-guild messages.

        if guild is None or not isinstance(channel, GuildMessagable):
            return

        # ⸻ Block messages that do not belong to the current guild context.

        log_channel = await self.bot.config(guild).get_messages_delete_logging_channel()

        if log_channel is None or log_channel.guild != guild:
            return

        # ⸻ Block evaluations.

        if content.startswith(".eval") and is_bot_owner(author):
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
                        "### Attachments\n"
                       f"{attachments_display(attachments)}",
                    ),
                )

            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    "### Content\n"
                   f"{clean_and_truncate(content or "[No content, likely an embed or attachment]")}",
                ),
            )

        await log_channel.send(
            view             = DeleteView(),
            allowed_mentions = AllowedMentions.none(),
        )


async def setup(bot : Cordex) -> None:
    cog = MessageDeleteLogging(bot)
    await bot.add_cog(cog)
