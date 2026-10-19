from bot import Interaction
from bot.types import GuildMessagable
from commands.moderation._base import send_moderation_modal
from core.moderation import ActionType

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation lockdown remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_moderation_lockdown_remove(interaction : Interaction) -> None:
    """
    Remove a channel from lockdown.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    """
    channel = interaction.channel
    if not isinstance(channel, GuildMessagable):
        return

    await send_moderation_modal(interaction, ActionType.lockdown_remove, channel)
