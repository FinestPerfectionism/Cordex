from discord import Role
from discord.abc import GuildChannel
from discord.app_commands import (
    Choice,
    Group,
    choices,
    command,
    describe,
    guild_only,
    rename,
)
from discord.ext import commands

from bot import Cordex, Interaction
from core.permissions import administrator_cmd, director_cmd

from .channels import (
    run_server_channel_info,
    run_server_channel_duplicate,
    run_server_channel_sync,
)
from .configure import run_server_configure
from .roles import (
    run_server_role_info,
    run_server_role_members,
    run_server_role_permissions,
    run_server_role_permissionscompare,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Server Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@guild_only
class ServerCommands(
    commands.GroupCog,
    name        = "server",
    description = "Staff only — server commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot : Cordex = bot

    role    : Group = Group(
        name        = "role",
        description = "Server role commands",
    )

    channel : Group = Group(
        name        = "channel",
        description = "Server channel commands",
    )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server role info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @role.command(
        name        = "info",
        description = "View information for a role.",
    )
    @describe(role = "The role to view information for.")
    @administrator_cmd()
    async def cmd_role_info(
        self,
        interaction   : Interaction,
        role          : Role,
    ) -> None:
        await run_server_role_info(interaction, role)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server role members Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @role.command(
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
    async def cmd_role_members(
        self,
        interaction   : Interaction,
        role          : Role,
        role_filter   : str | None = None,
        person_filter : str | None = None,
    ) -> None:
        await run_server_role_members(interaction, role, role_filter, person_filter)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server role permissions Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @role.command(
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
    async def cmd_role_permissions(
        self,
        interaction : Interaction,
        role        : Role,
        perm_filter : str | None = None,
    ) -> None:
        await run_server_role_permissions(interaction, role, perm_filter)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server role permissions-compare Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @role.command(
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
    async def cmd_role_permissionscompare(
        self,
        interaction : Interaction,
        role1       : Role,
        role2       : Role,
    ) -> None:
        await run_server_role_permissionscompare(interaction, role1, role2)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server configure Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "configure",
        description = "Configure guild settings.",
    )
    @director_cmd()
    async def cmd_configure(self, interaction : Interaction) -> None:
        await run_server_configure(interaction, self.bot)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server channel info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @channel.command(
        name        = "info",
        description = "View information for a channel.",
    )
    @describe(channel = "The channel to view information for. Defaults to the current one.")
    @administrator_cmd()
    async def cmd_channel_info(
        self,
        interaction : Interaction,
        channel     : GuildChannel | None = None,
    ) -> None:
        await run_server_channel_info(interaction, channel)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server channel sync Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @channel.command(
        name        = "sync",
        description = "Sync a channel's permissions to it's category.",
    )
    @describe(channel = "The channel to sync permissions for. Defaults to the current one.")
    @administrator_cmd()
    async def cmd_channel_sync(
        self,
        interaction : Interaction,
        channel     : GuildChannel | None = None,
    ) -> None:
        await run_server_channel_sync(interaction, channel)
    
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server channel duplicate Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @channel.command(
        name        = "duplicate",
        description = "Duplicate a channel or category.",
    )
    @describe(channel = "The channel to duplicate. Defaults to the current one.")
    @administrator_cmd()
    async def cmd_channel_duplicate(
        self,
        interaction : Interaction,
        channel     : GuildChannel | None = None,
    ) -> None:
        await run_server_channel_duplicate(interaction, channel)

async def setup(bot : Cordex) -> None:
    cog = ServerCommands(bot)
    await bot.add_cog(cog)
