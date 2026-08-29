from discord import Attachment, Thread
from discord.utils import escape_markdown

from bot.types import GuildMessagable
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

def channel_display(channel : GuildMessagable) -> str:
    if isinstance(channel, Thread):
        parent = channel.parent

        if parent is not None:
            return f"{parent.mention} {ARROW_EMOJI} {channel.mention} | {parent.id} {ARROW_EMOJI} {channel.id}"

    return f"{channel.mention} | {channel.id}"

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# attachments_display
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def attachments_display(attachments : list[Attachment]) -> str:
    return "\n".join(f"- {escape_markdown(f"{attachment.filename} | {attachment.url}")}" for attachment in attachments)
