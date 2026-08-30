from typing import final

from discord.app_commands import command, describe
from discord.ext import commands

from bot import Cordex, Interaction

from .help import run_help

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Help Command
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class HelpCommand(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /help Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "help",
        description = "Provides assistance into a command.",
    )
    @describe(name = "The name of the command to view information for. Defaults to information about the bot and a list of commands.")
    async def cmd_help(self, interaction : Interaction, name : str | None = None) -> None:
        await run_help(interaction, name)

async def setup(bot : Cordex) -> None:
    cog = HelpCommand(bot)
    await bot.add_cog(cog)
