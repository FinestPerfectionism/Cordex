from typing import final

from discord import Member
from discord.app_commands import command, describe, guild_only
from discord.ext import commands

from bot import Cordex, Interaction
from core.help import help_description

from .info import run_member_info

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Member Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
@guild_only
class MemberCommands(
    commands.GroupCog,
    name        = "member",
    description = "Member commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /member info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(arguments = {"member" : "The user to view information for. Defaults to yourself."})
    @command(
        name        = "info",
        description = "View information for a member.",
    )
    @describe(member = "The user to view information for. Defaults to yourself.")
    async def cmd_member_info(self, interaction : Interaction, member : Member | None = None) -> None:
        await run_member_info(interaction, member)

async def setup(bot : Cordex) -> None:
    cog = MemberCommands(bot)
    await bot.add_cog(cog)
