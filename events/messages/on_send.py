from re import compile
from typing import Self, final

from discord import AllowedMentions, MediaGalleryItem, Message, Thread
from discord.abc import Messageable
from discord.ext import commands

from bot import Cordex
from bot.ui import (
    Container,
    LayoutView,
    MediaGallery,
    TextDisplay,
    VisibleLargeSeparator,
)
from constants import (
    DIRECTOR_TASKS_CHANNEL_ID,
    DIRECTORS_ROLE_ID,
    MAIN_GUILD_ID,
    WAPPLE_CHAIN_CHANNEL_ID,
)

from . import WAPPLE_PATTERN

MESSAGE_LINK_PATTERN = compile(r"https://discord(?:app)?\.com/channels/(\d+|@me)/(\d+)/(\d+)")

FACTOIDS = {
    "bump" : (
        "# Please bump __both__ bots.\n"
        "We really appreciate bumping! If you are going to bump, please bump **both** <@735147814878969968> and <@1159147139960676422> (and <@1222548162741538938> too if it's available).\n"
        "### Why?\n"
        "The bots have a cooldown of one bump per 2 (24 for Discadia) hours. We try to sync the timer on each. Bumping both at once ensures that this happens *and* gets our server more recognition."
    ),
}

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Message Send Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class MessageSendHandler(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def message_send_handler(self, message : Message) -> None:
        content = message.content
        author  = message.author
        channel = message.channel
        guild   = message.guild

        # ⸻ Block bots and the bot itself.

        if author.bot or author == self.bot.user:
            return

        # ⸻ Block non-guild messages or messages not in the main guild.

        if guild is None or guild.id != MAIN_GUILD_ID:
            return

        # ⸻ Provide a preview for message links.

        @final
        class Preview(LayoutView):
            def __init__(self, *, target : Message, link : str) -> None:
                super().__init__()

                container = Container[Self](TextDisplay(f"{target.author.mention}: {link}"), VisibleLargeSeparator())

                if target.content:
                    container.add_text(target.content)

                if target.attachments:
                    items = [
                        MediaGalleryItem(attachment.url)
                        for attachment in target.attachments
                        if attachment.content_type
                        and attachment.content_type.startswith(("image/", "video/"))
                    ]

                    if items:
                        container.add_item(MediaGallery(*items))

                self.add_item(container)

        match = MESSAGE_LINK_PATTERN.search(content)
        if match:
            channel_id = int(match.group(2))
            message_id = int(match.group(3))

            target_channel = await self.bot.fetch_channel(channel_id)

            if not isinstance(target_channel, Messageable):
                return

            target_message = await target_channel.fetch_message(message_id)

            if not target_message.content and not target_message.attachments:
                return

            await message.reply(
                view             = Preview(target = target_message, link = content),
                mention_author   = False,
                allowed_mentions = AllowedMentions.none(),
            )

        # ⸻ Block non-wapple text in wapple channel.

        if channel.id == WAPPLE_CHAIN_CHANNEL_ID and not WAPPLE_PATTERN.fullmatch(content.strip()):
            await message.delete()
            return

        # ⸻ Factoids.

        if content.startswith("?") and " " not in content[1:] and guild.id == MAIN_GUILD_ID:
            key = content[1:].lower()

            if key in FACTOIDS:
                async with channel.typing():
                    await channel.send(FACTOIDS[key])
                    return

        # ⸻ Mention directors upon thread creation.

        if isinstance(channel, Thread):
            thread = channel
            if message.id == thread.id and thread.parent_id == DIRECTOR_TASKS_CHANNEL_ID:
                await thread.send(f"<@&{DIRECTORS_ROLE_ID}>")

async def setup(bot : Cordex) -> None:
    cog = MessageSendHandler(bot)
    await bot.add_cog(cog)
