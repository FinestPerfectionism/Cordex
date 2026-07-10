from discord.app_commands import command, describe
from discord.ext import commands

from bot import Cordex, Interaction
from core.permissions import administrator_cmd

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Info Command
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class InfoCommands(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot : Cordex = bot

    # async def view_autocomplete(_interaction : Interaction, current : str) -> list[Choice[str]]:
    #     return [][:25]

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "info",
        description = "Manage guild information.",
    )
    @describe()
    # @autocomplete(view = view_autocomplete)
    @administrator_cmd()
    # async def cmd_configure(self, interaction : Interaction, view : str | None) -> None:
    async def cmd_configure(self, interaction : Interaction) -> None:
        await interaction.response.send_message(
            "This command does nothing right now. :[",
            ephemeral = True,
        )

async def setup(bot : Cordex) -> None:
    cog = InfoCommands(bot)
    await bot.add_cog(cog)
