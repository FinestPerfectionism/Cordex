

from discord.abc import GuildChannel

from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /channel compare Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_channel_compare(
    interaction : Interaction,
    _channel_1  : GuildChannel | None = None,
    _channel_2  : GuildChannel | None = None,
) -> None:
    await interaction.response.defer(ephemeral = True)

    if not interaction.guild:
        return

    await interaction.followup.send(
        "This command does nothing right now. :[",
        ephemeral = True,
    )
