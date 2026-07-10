from discord import Member
from discord.app_commands import command, describe, guild_only
from discord.ext import commands

from bot import Cordex, Interaction

from .info import run_user_info

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# User Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@guild_only
class UserCommands(
    commands.GroupCog,
    name        = "user",
    description = "User commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot : Cordex = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /user info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "info",
        description = "View information for a user.",
    )
    @describe(user = "The user to view information for. Defaults to yourself.")
    async def cmd_info(self, interaction : Interaction, user : Member | None = None):
        await run_user_info(interaction, user)

async def setup(bot : Cordex) -> None:
    cog = UserCommands(bot)
    await bot.add_cog(cog)
