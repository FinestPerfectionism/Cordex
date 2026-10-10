from bot import Interaction
from bot.types import GuildMessagableChannel
from core.exceptions import send_bad_argument

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /channel compare Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_channel_compare(
    interaction : Interaction,
    channel_1  : GuildMessagableChannel | None = None,
    channel_2  : GuildMessagableChannel | None = None,
) -> None:
    """
    List all differing permissions for two selected channels.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    channel_1 : `GuildMessagableChannel | None = None`
        The first channel to compare. Defaults to the current one.
    channel_2 : `GuildMessagableChannel | None = None`
        The second channel to compare. Defaults to the current one.
    """
    await interaction.response.defer(ephemeral = True)

    if not interaction.guild:
        return

    if not channel_1 and not channel_2:
        await send_bad_argument(
            interaction,
            subtitle = {("channel-1", "channel-2") :  "At least one channel must be selected."},
        )

    await interaction.followup.send(
        "This command does nothing right now. :[",
        ephemeral = True,
    )
