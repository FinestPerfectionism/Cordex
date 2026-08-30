from typing import TYPE_CHECKING, Self, cast, final

from discord import AllowedMentions, Guild, Message
from discord.ext import commands
from discord.utils import format_dt, utcnow

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
from commands.bot_owner.eval import eval_message_ids
from constants import COLOR_GREY
from core.permissions import is_bot_owner
from core.utilities import format_table

from ._base import attachments_display, channel_display, clean_and_truncate

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Message Edit Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class MessageEditHandler(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    async def _get_log_channel(self, guild : Guild) -> GuildMessagable | None:
        async with self.bot.db.execute(
            "SELECT config_value FROM GuildConfig WHERE guild_id = ? AND config_key = ?",
            (guild.id, "messages_edit_channel"),
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

    @commands.Cog.listener("on_message_edit")
    async def message_edit_handler(self, before : Message, after : Message) -> None:
        author  = before.author
        guild   = before.guild
        channel = before.channel

        before_content = before.content
        before_id      = before.id

        after_content     = after.content
        after_attachments = after.attachments

        # ⸻ Block bots and the bot itself.

        if author.bot or author == self.bot.user:
            return

        # ⸻ Block non-guild messages.

        if guild is None or not isinstance(channel, GuildMessagable):
            return

        # ⸻ Block messages that do not belong to the current guild context.

        log_channel = await self._get_log_channel(guild)

        if log_channel is None or log_channel.guild.id != guild.id:
            return

        # ⸻ Eval command editing.

        if before_id in eval_message_ids:

            # ⸻ Remove our old reactions.

            if self.bot.user is not None:
                for reaction in before.reactions:
                    if reaction.me:
                        await reaction.remove(self.bot.user)

            # ⸻ Reinvoke the command.

            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)

            # ⸻ Remove our old response (done after the reinvocation since faster reevaluation is better).

            old_response_id = eval_message_ids.pop(before_id, None)
            if old_response_id is not None:
                old_msg = await channel.fetch_message(old_response_id)
                await old_msg.delete()

            return

        # ⸻ Block evaluations.

        if after_content.startswith(".eval") and is_bot_owner(author):
            return

        # ⸻ Edit message logging.

        before_files = [a.url for a in before.attachments]
        after_files  = [a.url for a in after.attachments]

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
                        (
                            "### Attachments\n"
                           f"{attachments_display(after_attachments)}"
                        ),
                    ),
                )

            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    (
                        "### Before\n"
                       f"{clean_and_truncate(before_content) or "[No content, likely an embed or attachment]"}"
                    ),
                ),
                TextDisplay(
                    (
                        "### After\n"
                       f"{clean_and_truncate(after_content) or "[No content, likely an embed or attachment]"}"
                    ),
                ),
            )

        await log_channel.send(view = EditView(), allowed_mentions = AllowedMentions.none())

        await self.bot.process_commands(after)

async def setup(bot : Cordex) -> None:
    cog = MessageEditHandler(bot)
    await bot.add_cog(cog)
