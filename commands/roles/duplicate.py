from discord import Role

from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role duplicate Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_duplicate(
    interaction : Interaction,
    _role       : Role,
) -> None:
    await interaction.response.defer(ephemeral = True)

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    await interaction.followup.send(
        "This command does nothing right now. :[",
        ephemeral = True,
    )
