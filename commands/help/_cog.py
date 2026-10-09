from typing import final

from discord.app_commands import Choice, Group, command, describe, rename
from discord.ext import commands

from bot import Cordex, Interaction
from core.state import unrestrictable

from .help import run_help

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Help Command
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class HelpCommand(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /help Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @unrestrictable
    @command(
        name        = "help",
        description = "Receive helpful information for a command.",
    )
    @rename(command_name = "command-name")
    @describe(command_name = "The name of the command to view information for.")
    async def cmd_help(self, interaction : Interaction, command_name : str) -> None:
        await run_help(interaction, command_name)

    @cmd_help.autocomplete("command_name")
    async def autocomplete_cmdhelp(self, interaction : Interaction, current : str) -> list[Choice[str]]:
        return [
            Choice(name = f"/{cmd.qualified_name}", value = cmd.qualified_name)
            for cmd in interaction.client.tree.walk_commands()
            if not isinstance(cmd, Group) and
            current.lower() in cmd.qualified_name.lower()
        ]


async def setup(bot : Cordex) -> None:
    cog = HelpCommand(bot)
    await bot.add_cog(cog)
