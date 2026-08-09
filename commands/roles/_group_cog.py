from typing import final

from discord import Role
from discord.app_commands import Choice, choices, command, describe, guild_only, rename
from discord.ext import commands

from bot import Cordex, Interaction
from core.help import help_description
from core.permissions import administrator_cmd
from core.utilities import unimplemented

from .compare import run_role_compare
from .duplicate import run_role_duplicate
from .info import run_role_info
from .members import run_role_members
from .permissions import run_role_permissions

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Role Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
@guild_only
class RoleCommands(
    commands.GroupCog,
    name        = "role",
    description = "Role commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role duplicate Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(arguments = {"role" : "The role to duplicate."})
    @command(
        name        = "duplicate",
        description = "Duplicate a role.",
    )
    @describe(role = "The role to duplicate.")
    @administrator_cmd()
    @unimplemented()
    async def cmd_role_duplicate(
        self,
        interaction : Interaction,
        role        : Role,
    ) -> None:
        await run_role_duplicate(interaction, role)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(arguments = {"role" : "The role to view information for."})
    @command(
        name        = "info",
        description = "View information for a role.",
    )
    @describe(role = "The role to view information for.")
    async def cmd_role_info(
        self,
        interaction   : Interaction,
        role          : Role,
    ) -> None:
        await run_role_info(interaction, role)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role members Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(
        arguments = {
            "role"          : "The role to view members or the lack thereof for.",
            "role-filter"   : "Whether to check who has or who doesn't have the role selected. Defaults to \"member of\".",
            "person-filter" : "Whether to show humans or bots. Defaults to both.",
        },
    )
    @command(
        name        = "members",
        description = "List members based on role possession and human/bot filtering.",
    )
    @describe(
        role          = "The role to view members or the lack thereof for.",
        role_filter   = "Whether to check who has or who doesn't have the role selected. Defaults to \"member of\".",
        person_filter = "Whether to show humans or bots. Defaults to both.",
    )
    @rename(
        role_filter   = "role-filter",
        person_filter = "person-filter",
    )
    @choices(
        role_filter = [
            Choice(name = "Member of",       value = "whohas"),
            Choice(name = "Not a Member of", value = "whodoesnthave"),
        ],
        person_filter = [
            Choice(name = "Humans", value = "humans"),
            Choice(name = "Bots",   value = "bots"),
        ],
    )
    async def cmd_role_members(
        self,
        interaction   : Interaction,
        role          : Role,
        role_filter   : str | None = None,
        person_filter : str | None = None,
    ) -> None:
        await run_role_members(interaction, role, role_filter, person_filter)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role permissions Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(
        arguments = {
            "role"        : "The role to list permissions for.",
            "perm-filter" : "Whether to show enabled or disabled permissions. Defaults to both.",
        },
    )
    @command(
        name        = "permissions",
        description = "List permissions for a selected role.",
    )
    @rename(perm_filter = "filter")
    @describe(
        role        = "The role to list permissions for.",
        perm_filter = "Whether to show enabled or disabled permissions. Defaults to both.",
    )
    @choices(
        perm_filter = [
            Choice(name = "Enabled",  value = "enabled"),
            Choice(name = "Disabled", value = "disabled"),
        ],
    )
    @administrator_cmd()
    async def cmd_role_permissions(
        self,
        interaction : Interaction,
        role        : Role,
        perm_filter : str | None = None,
    ) -> None:
        await run_role_permissions(interaction, role, perm_filter)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role compare Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(
        arguments = {
            "role-1" : "The first role to compare.",
            "role-2" : "The second role to compare.",
        },
    )
    @command(
        name        = "compare",
        description = "List all differing permissions for two selected roles.",
    )
    @rename(
        role_1 = "role-1",
        role_2 = "role-2",
    )
    @describe(
        role_1 = "The first role to compare.",
        role_2 = "The second role to compare.",
    )
    @administrator_cmd()
    async def cmd_role_compare(
        self,
        interaction : Interaction,
        role_1      : Role,
        role_2      : Role,
    ) -> None:
        await run_role_compare(interaction, role_1, role_2)

async def setup(bot : Cordex) -> None:
    cog = RoleCommands(bot)
    await bot.add_cog(cog)
