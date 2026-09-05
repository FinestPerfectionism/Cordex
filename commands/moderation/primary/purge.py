from bot import Interaction
from bot.types import GuildMessagable

from ._base import send_moderation_modal

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation purge Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_mod_primary_purge(interaction : Interaction) -> None:
    if not isinstance(interaction.channel, GuildMessagable):
        return

    await send_moderation_modal(interaction, "Purge", interaction.channel)
