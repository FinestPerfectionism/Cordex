from typing import Self, cast, final

from discord import Guild, Message
from discord.ext import commands
from discord.mentions import AllowedMentions

from bot import Cordex
from bot.types import GuildMessagable
from bot.ui import Container, LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_RED
from core.permissions import is_bot_owner
from core.utilities import format_now, format_table

from ._base import attachments_display, channel_display, clean_and_truncate

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Message Delete Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class MessageDeleteHandler(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    async def _get_log_channel(self, guild : Guild) -> GuildMessagable | None:
        async with self.bot.db.execute(
            t"SELECT config_value FROM GuildConfig WHERE guild_id = {guild.id} AND config_key = {"messages_delete_channel"}",
        ) as cursor:
            res = await cursor.fetchone()

        if not res:
            return None

        channel_id = cast("int | None", res[0])

        if channel_id is None:
            return None

        log_channel = guild.get_channel(channel_id)

        if not isinstance(log_channel, GuildMessagable):
            return None

        return log_channel

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

        # ⸻ Block non-guild messages.

        if guild is None or not isinstance(channel, GuildMessagable):
            return

        # ⸻ Block messages that do not belong to the current guild context.

        log_channel = await self._get_log_channel(guild)

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
                        (
                            "### Attachments\n"
                           f"{attachments_display(attachments)}"
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
