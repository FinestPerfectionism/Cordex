from discord import Attachment, ForumChannel, TextChannel, Thread
from discord.abc import GuildChannel, Messageable
from discord.utils import escape_markdown

from constants import ARROW_EMOJI
from core.utilities import truncate

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Messages Handling Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# clean_and_truncate
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def clean_and_truncate(text : str) -> str:
    return escape_markdown(truncate(text))

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# channel_display
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def channel_display(channel : Messageable | GuildChannel) -> str:
    if isinstance(channel, Thread):
        parent = channel.parent

        if isinstance(parent, ForumChannel):
            return f"{parent.mention} {ARROW_EMOJI} {channel.mention} | {parent.id} {ARROW_EMOJI} {channel.id}"
        if parent is not None:
            return f"{parent.mention} {ARROW_EMOJI} {channel.mention} | {parent.id} {ARROW_EMOJI} {channel.id}"

        return channel.mention

    if isinstance(channel, TextChannel):
        return f"{channel.mention} | {channel.id}"

    return "Unknown Channel"

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_attachments
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def format_attachments(attachments : list[Attachment]) -> str:
    return "\n".join(f"- {escape_markdown(f"{attachment.filename} | {attachment.url}")}" for attachment in attachments)
