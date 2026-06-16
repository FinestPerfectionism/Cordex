from discord import Role
from discord.app_commands import Choice, choices, describe, rename
from discord.app_commands import command as app_command
from discord.ext import commands

from bot import Cordex, Interaction
from core.permissions import administrator_cmd

from .members import run_role_members
from .permissions import run_role_permissions
from .permissionscompare import run_role_permissionscompare

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Role Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class RoleCommands(
    commands.GroupCog,
    name        = "roles",
    description = "Administrators only — Role commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot : Cordex = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role members Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "members",
        description = "List members based on role possession and human/bot filtering.",
    )
    @describe(
        role          = "The role to view members or the lack thereof for.",
        role_filter   = "Whether to check who has or who doesn't have the role selectec.",
        person_filter = "The type of users to show. Leave empty for both.",
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
    @administrator_cmd()
    async def cmd_members(
        self,
        interaction   : Interaction,
        role          : Role,
        role_filter   : str,
        person_filter : str | None = None,
    ) -> None:
        _ = await run_role_members(interaction, role, role_filter, person_filter)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role permissions-compare Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "permissions-compare",
        description = "List all differing permissions for two selected roles.",
    )
    @rename(
        role1 = "role-1",
        role2 = "role-2",
    )
    @describe(
        role1 = "The first role to compare.",
        role2 = "The second role to compare.",
    )
    @administrator_cmd()
    async def cmd_permissionscompare(
        self,
        interaction : Interaction,
        role1       : Role,
        role2       : Role,
    ) -> None:
        _ = await run_role_permissionscompare(interaction, role1, role2)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role permissions Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "permissions",
        description = "List permissions for a selected role.",
    )
    @rename(perm_filter = "filter")
    @describe(
        role        = "The role to list permissions for.",
        perm_filter = "The permissions to show, or all permissions. Leave empty for both.",
    )
    @choices(
        perm_filter = [
            Choice(name = "Enabled",  value = "enabled"),
            Choice(name = "Disabled", value = "disabled"),
        ],
    )
    @administrator_cmd()
    async def cmd_permissions(
        self,
        interaction : Interaction,
        role        : Role,
        perm_filter : str | None = None,
    ) -> None:
        _ = await run_role_permissions(interaction, role, perm_filter)

async def setup(bot : Cordex) -> None:
    cog = RoleCommands(bot)
    await bot.add_cog(cog)
