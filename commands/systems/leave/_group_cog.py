from typing import final

from discord import Member
from discord.app_commands import Choice, choices, command, describe, guild_only
from discord.ext import commands

from bot import Cordex, Interaction
from core.help import help_description
from core.permissions import director_cmd, staff_cmd

from .add import run_leave_add
from .remove import run_leave_remove

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Leave Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
@guild_only
class LeaveCommands(
    commands.GroupCog,
    name        = "leave",
    description = "Staff only —— Leave commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /leave add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(
        arguments = {
            "target" : "The staff member to vacate. Defaults to yourself.",
            "type"   : 'The type of leave to apply. Defaults to "Soft Clean".',
        },
    )
    @command(
        name        = "add",
        description = "Vacate a staff member.",
    )
    @describe(
        target     = "The staff member to place on leave. Defaults to yourself.",
        leave_type = 'The type of leave to apply. Defaults to "Soft Clean".',
    )
    @choices(
        leave_type = [
            Choice(
                name  = "None",
                value = "none",
            ),
            Choice(
                name  = "Soft Clean",
                value = "soft_clean",
            ),
            Choice(
                name  = "Hard Clean",
                value = "hard_clean",
            ),
        ],
    )
    @director_cmd()
    async def cmd_leave_add(
        self,
        interaction : Interaction,
        target      : Member | None = None,
        leave_type  : str    | None = None,
    ) -> None:
        await run_leave_add(interaction, target, leave_type)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /leave remove Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(arguments = {"target" : "The staff member to remove from leave. Defaults to yourself."})
    @command(
        name        = "remove",
        description = "Un-vacate a staff member.",
    )
    @describe()
    @staff_cmd()
    async def cmd_leave_remove(self, interaction : Interaction, target : Member | None = None) -> None:
        await run_leave_remove(interaction, target)

async def setup(bot : Cordex) -> None:
    cog = LeaveCommands(bot)
    await bot.add_cog(cog)
