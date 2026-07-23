from re import compile

from discord import TextChannel

from bot import Interaction, bot
from constants import PARTNERSHIPS_CHANNEL_ID
from core.responses import format_send

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Partnerships Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Discord Invite Regex
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

INVITE_REGEX = compile(r"^(https?://)?(www\.)?(discord\.gg|discord\.com/invite)/[A-Za-z0-9-]+$")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# get_channel
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def get_channel(interaction : Interaction) -> TextChannel | None:
    channel = bot.get_channel(PARTNERSHIPS_CHANNEL_ID)
    if not isinstance(channel, TextChannel):
        await format_send(
            interaction,
            msg_type = "error",
            title    = "update",
            subtitle = "The partnerships channel ID is missing or points to the wrong channel type.",
            footer   = "Bad configuration",
        )
        return None
    return channel
