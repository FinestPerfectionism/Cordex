from typing import final

from discord.app_commands import command
from discord.ext import commands

from bot import Cordex, Interaction

from .about import run_about

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# About Command
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class AboutCommand(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /about Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "about",
        description = "View information about me.",
    )
    async def cmd_about(self, interaction : Interaction) -> None:
        await run_about(interaction)


async def setup(bot : Cordex) -> None:
    cog = AboutCommand(bot)
    await bot.add_cog(cog)
