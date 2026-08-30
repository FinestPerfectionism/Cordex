

from discord.abc import GuildChannel

from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /channel duplicate Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_channel_duplicate(
    interaction : Interaction,
    _channel    : GuildChannel | None = None,
    *,
    _bare       : bool                = False,
) -> None:
    await interaction.response.defer(ephemeral = True)

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    await interaction.followup.send(
        "This command does nothing right now. :[",
        ephemeral = True,
    )
