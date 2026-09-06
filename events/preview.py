import re
from typing import Self, final

from discord import AllowedMentions, Forbidden, MediaGalleryItem, Message
from discord.abc import Messageable
from discord.ext import commands

from bot import Cordex
from bot.ui import (
    Container,
    File,
    LayoutView,
    MediaGallery,
    TextDisplay,
    VisibleLargeSeparator,
)

MESSAGE_LINK_PATTERN = re.compile(r"https://discord(?:app)?\.com/channels/(\d+|@me)/(\d+)/(\d+)")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Preview Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class Preview(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def listener_preview_onmessage(self, message : Message) -> None:
        content = message.content
        author  = message.author

        # ⸻ Block bots and the bot itself.

        if author.bot or author == self.bot.user:
            return

        # ⸻ Provide a preview for message links.

        @final
        class PreviewView(LayoutView):
            def __init__(self, *, target : Message, link : str, names : list[str]) -> None:
                super().__init__()

                container = Container[Self](TextDisplay(f"{target.author.mention}: {link}"), VisibleLargeSeparator())

                if target.content:
                    container.add_text(target.content)

                if target.attachments:
                    gallery_items : list[MediaGalleryItem] = [
                        MediaGalleryItem(attachment.url)
                        for attachment in target.attachments
                        if attachment.content_type
                        and attachment.content_type.startswith(("image/", "video/"))
                    ]
                    file_items    : list[File[Self]]       = [
                        File(f"attachment://{name}")
                        for name in names
                    ]

                    if gallery_items:
                        container.add_item(MediaGallery(*gallery_items))

                    if file_items:
                        container.append_items(file_items)

                self.add_item(container)

        if match := MESSAGE_LINK_PATTERN.search(content):
            channel_id = int(match.group(2))
            message_id = int(match.group(3))

            target_channel = self.bot.get_channel(channel_id)

            if not isinstance(target_channel, Messageable):
                return

            try:
                target_message = await target_channel.fetch_message(message_id)
            except Forbidden:
                return

            # ⸻ Message has no content or attachments. Perhaps an embed?

            if not target_message.content and not target_message.attachments:
                return

            # ⸻ Convert non-media attachments to files for re-uploading.

            files = [
                await attachment.to_file()
                for attachment in target_message.attachments
                if attachment.content_type
                and not attachment.content_type.startswith(("image/", "video/"))
            ]

            names = [file.filename for file in files]

            await message.reply(
                files            = files,
                view             = PreviewView(target = target_message, link = content, names = names),
                mention_author   = False,
                allowed_mentions = AllowedMentions.none(),
            )

async def setup(bot : Cordex) -> None:
    cog = Preview(bot)
    await bot.add_cog(cog)
