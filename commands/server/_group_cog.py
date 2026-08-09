from typing import final

from discord.app_commands import command, guild_only
from discord.ext import commands

from bot import Cordex, Interaction
from core.permissions import director_cmd

from .configure import run_server_configure
from .info import run_server_info

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Server Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
@guild_only
class ServerCommands(
    commands.GroupCog,
    name        = "server",
    description = "Server commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server configure Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "configure",
        description = "Configure guild settings.",
    )
    @director_cmd()
    async def cmd_server_configure(self, interaction : Interaction) -> None:
        await run_server_configure(interaction, self.bot)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "info",
        description = "View information for this guild.",
    )
    async def cmd_server_info(self, interaction : Interaction) -> None:
        await run_server_info(interaction)

async def setup(bot : Cordex) -> None:
    cog = ServerCommands(bot)
    await bot.add_cog(cog)
