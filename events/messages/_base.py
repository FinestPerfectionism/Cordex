from re import Pattern, compile, escape

from discord import (
    Attachment,
    ForumChannel,
    StageChannel,
    TextChannel,
    Thread,
    VoiceChannel,
)
from discord.abc import GuildChannel, Messageable
from discord.utils import escape_markdown

from constants import DIRECTORSHIP_CATEGORY_ID

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Messages Handling Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Wapple Stuff
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

WAPPLE_EMOJIS : list[str] = [
    "<:Wapple:1474915842071335098>",
    "<:WappleYellow:1474916545158189108>",
    "<:WappleGreen:1474916731532087569>",
    "<:WappleBlue:1474916471984623842>",
    "<:WappleHartwellWhite:1474916613232001117>",
    "<:applebruh:1478244953892192357>",
    "<:ex:1476672300467093626>",
    "<:susapple:1483533565005402144>",
]

WAPPLE_PATTERN : Pattern[str] = compile(rf"^({'|'.join(map(escape, WAPPLE_EMOJIS))}| )+$")

def is_valid_wapple_chain(content : str) -> bool:
    return bool(WAPPLE_PATTERN.fullmatch(content.strip()))

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# truncate_text
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def truncate_text(text : str, max_length : int = 1024) -> str:
    return (escape_markdown(text)[:max_length - 3] + "...") if len(text) > max_length else text

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# is_directorship_channel
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def is_directorship_channel(channel : Messageable) -> bool:
    return (
        isinstance(channel, TextChannel | VoiceChannel | StageChannel)
        and channel.category_id == DIRECTORSHIP_CATEGORY_ID
    ) or (
        isinstance(channel, Thread)
        and getattr(channel.parent, "category_id", None) == DIRECTORSHIP_CATEGORY_ID
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# channel_display
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def channel_display(channel : Messageable | GuildChannel) -> str:
    if isinstance(channel, Thread):
        parent = channel.parent

        if isinstance(parent, ForumChannel):
            return f"{parent.mention} / {channel.mention}"
        if parent is not None:
            return f"{parent.mention} / {channel.mention}"

        return channel.mention

    if isinstance(channel, TextChannel):
        return channel.mention

    return "Unknown Channel"

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_attachments
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def format_attachments(attachments : list[Attachment]) -> str:
    if not attachments:
        return "None"
    return "\n".join(f"- {a.filename} ({a.url})" for a in attachments)
