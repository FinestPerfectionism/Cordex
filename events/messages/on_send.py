from re import compile
from typing import Self, final

from discord import AllowedMentions, MediaGalleryItem, Message
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

MESSAGE_LINK_PATTERN = compile(r"https://discord(?:app)?\.com/channels/(\d+|@me)/(\d+)/(\d+)")

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
        guild   = message.guild

        # ⸻ Block bots and the bot itself.

        if author.bot or author == self.bot.user:
            return

        # ⸻ Block non-guild messages.

        if guild is None:
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

# async def setup(bot : Cordex) -> None:
#     cog = MessageSendHandler(bot)
#     await bot.add_cog(cog)
