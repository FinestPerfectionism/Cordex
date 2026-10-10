from discord import Thread

from bot import Interaction
from bot.types import GuildMessagable, GuildMessagableChannel
from core.exceptions import send_bad_argument
from core.responses import MessageType, format_send

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /channel sync Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_channel_sync(
    interaction : Interaction,
    channel     : GuildMessagableChannel | None = None,
) -> None:
    """
    Sync a channel's permissions to it's category. Defaults to the current one.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    channel : `GuildMessagableChannel | None = None`
        The channel to sync permissions for. Defaults to the current one.
    """
    await interaction.response.defer(ephemeral = True)

    target = channel or interaction.channel

    if not isinstance(target, GuildMessagable):
        return

    if isinstance(target, Thread):
        await send_bad_argument(
            interaction,
            subtitle = {"channel" : "Threads cannot be synced."},
        )
        return

    if target.category:
        await target.edit(sync_permissions = True)
        await format_send(interaction, MessageType.success, title = "synced channel")
        return

    await send_bad_argument(interaction, subtitle = {"channel" : "Channel must be under a category."})
    return
