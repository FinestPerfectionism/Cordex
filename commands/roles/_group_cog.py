from typing import final

from discord import Role
from discord.app_commands import Choice, choices, command, describe, guild_only, rename
from discord.ext import commands

from bot import Cordex, Interaction
from core.utilities import unimplemented

from .compare import run_role_compare
from .duplicate import run_role_duplicate
from .info import run_role_info
from .members import PersonFilter, RoleFilter, run_role_members
from .permissions import PermissionsFilter, run_role_permissions

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

    @command(
        name        = "duplicate",
        description = "Duplicate a role.",
    )
    @describe(role = "The role to duplicate.")
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
            Choice(name = "Member of",       value = "In"),
            Choice(name = "Not a Member of", value = "Not In"),
        ],
        person_filter = [
            Choice(name = "Humans", value = "Humans"),
            Choice(name = "Bots",   value = "Bots"),
        ],
    )
    async def cmd_role_members(
        self,
        interaction   : Interaction,
        role          : Role,
        role_filter   : RoleFilter   = "In",
        person_filter : PersonFilter = "Both",
    ) -> None:
        await run_role_members(interaction, role, role_filter, person_filter)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role permissions Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "permissions",
        description = "List permissions for a selected role.",
    )
    @rename(permissions_filter = "filter")
    @describe(
        role               = "The role to list permissions for.",
        permissions_filter = "Whether to show enabled or disabled permissions. Defaults to both.",
    )
    @choices(
        permissions_filter = [
            Choice(name = "Enabled",  value = "Enabled"),
            Choice(name = "Disabled", value = "Disabled"),
        ],
    )
    async def cmd_role_permissions(
        self,
        interaction        : Interaction,
        role               : Role,
        permissions_filter : PermissionsFilter = "Both",
    ) -> None:
        await run_role_permissions(interaction, role, permissions_filter)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /role compare Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

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
