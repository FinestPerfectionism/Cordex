from discord.abc import GuildChannel

from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /channel permissions Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_channel_permissions(
    interaction  : Interaction,
    _channel     : GuildChannel | None = None,
    _perm_filter : str          | None = None,
) -> None:
    await interaction.response.defer(ephemeral = True)

    if not interaction.guild:
        return

    await interaction.followup.send(
        "This command does nothing right now. :[",
        ephemeral = True,
    )
