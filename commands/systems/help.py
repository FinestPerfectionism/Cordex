from discord.app_commands import command
from discord.ext import commands

from bot import Cordex, Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Help Command
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class HelpCommand(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot : Cordex = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /help Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "help",
        description = "Provides assistance into a command. Defaults to information about the bot and a list of commands.",
    )
    async def cmd_help(self, interaction : Interaction, name : str | None = None) -> None:
        await interaction.response.send_message(
            "This command does nothing right now. :[",
            ephemeral = True,
        )

async def setup(bot : Cordex) -> None:
    cog = HelpCommand(bot)
    await bot.add_cog(cog)
