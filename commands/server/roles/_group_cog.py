from typing import TYPE_CHECKING

import discord
from discord.app_commands import command as app_command, describe, rename, choices, Choice, guild_only
from discord.ext import commands

from bot import Interaction
from core.permissions import administrator_cmd

from .members import run_role_members
from .permissions import run_role_permissions
from .permissionscompare import run_role_permissionscompare

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Role Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class RoleCommands(
    commands.GroupCog,
    name        = "roles",
    description = "Administrators only — Role commands.",
):
    def __init__(self, bot : "Cordex") -> None:
        super().__init__()
        self.bot : "Cordex" = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role members Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "members",
        description = "List members based on role possession and human/bot filtering.",
    )
    @describe(
        role          = "Select a role.",
        role_filter   = "Select whether to check who has or who doesn't have the role.",
        person_filter = "Select whether to list humans, bots, or both.",
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
            Choice(name = "Both",   value = "both"),
        ],
    )
    @guild_only()
    @administrator_cmd()
    async def cmd_members(
        self,
        interaction   : Interaction,
        role          : discord.Role,
        role_filter   : Choice[str],
        person_filter : Choice[str],
    ) -> None:
        _ = run_role_members(interaction, role, role_filter, person_filter)

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
    @guild_only()
    @administrator_cmd()
    async def cmd_permissionscompare(
        self,
        interaction : Interaction,
        role1       : discord.Role,
        role2       : discord.Role,
    ) -> None:
        _ = run_role_permissionscompare(interaction, role1, role2)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role permissions Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "permissions",
        description = "List all permissions for a selected role.",
    )
    @rename(perm_filter = "filter")
    @describe(
        role        = "The role to list permissions for.",
        perm_filter = "Whether to show enabled, disabled, or all permissions.",
    )
    @choices(
        perm_filter = [
            Choice(name = "All",      value = "all"),
            Choice(name = "Enabled",  value = "enabled"),
            Choice(name = "Disabled", value = "disabled"),
        ],
    )
    @guild_only()
    @administrator_cmd()
    async def cmd_permissions(
        self,
        interaction : Interaction,
        role        : discord.Role,
        perm_filter : str = "all",
    ) -> None:
        _ = run_role_permissions(interaction, role, perm_filter)

async def setup(bot : "Cordex") -> None:
    cog = RoleCommands(bot)
    await bot.add_cog(cog)
