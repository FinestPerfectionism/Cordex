from discord.app_commands import command
from discord.ext import commands

from bot import Cordex, Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Help Command
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class HelpCommands(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot : Cordex = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /help Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    # @command(name = "help")
    # async def cmd_help(self, interaction : Interaction, *, _name : str | None = None) -> None:
    @command(name = "help")
    async def cmd_help(self, interaction : Interaction) -> None:
        await interaction.response.send_message(
            "This button does nothing right now. :[",
            ephemeral = True,
        )

async def setup(bot : Cordex) -> None:
    cog = HelpCommands(bot)
    await bot.add_cog(cog)
