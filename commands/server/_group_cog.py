from discord import Attachment, Role, User
from discord.abc import GuildChannel
from discord.app_commands import (
    Choice,
    Group,
    autocomplete,
    choices,
    command,
    describe,
    guild_only,
    rename,
)
from discord.ext import commands

from bot import Cordex, Interaction
from core.permissions import administrator_cmd, director_cmd
from core.state import load_partnership_data

from .channels import (
    run_server_channel_duplicate,
    run_server_channel_info,
    run_server_channel_sync,
)
from .configure import run_server_configure
from .info import run_server_info
from .partnerships import (
    run_server_partnership_add,
    run_server_partnership_remove,
    run_server_partnership_update,
)
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

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Server Name Autocomplete
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def server_name_autocomplete(self, _interaction : Interaction, current : str) -> list[Choice[str]]:
        data = await load_partnership_data(self.bot.db)
        return [
            Choice(name = p["server_name"], value = p["server_name"])
            for p in data["partnerships"] if current.lower() in p["server_name"].lower()
        ][:25]

    role        : Group = Group(
        name        = "role",
        description = "Server role commands",
    )
    channel     : Group = Group(
        name        = "channel",
        description = "Server channel commands",
    )
    partnership : Group = Group(
        name        = "partnership",
        description = "Server partnership commands",
    )

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

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server role info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @role.command(
        name        = "info",
        description = "View information for a role.",
    )
    @describe(role = "The role to view information for.")
    @administrator_cmd()
    async def cmd_server_role_info(
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
    async def cmd_server_role_members(
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
    async def cmd_server_role_permissions(
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
    async def cmd_server_role_permissionscompare(
        self,
        interaction : Interaction,
        role1       : Role,
        role2       : Role,
    ) -> None:
        await run_server_role_permissionscompare(interaction, role1, role2)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server channel info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @channel.command(
        name        = "info",
        description = "View information for a channel.",
    )
    @describe(channel = "The channel to view information for. Defaults to the current one.")
    @administrator_cmd()
    async def cmd_server_channel_info(
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
    async def cmd_server_channel_sync(
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
    async def cmd_server_channel_duplicate(
        self,
        interaction : Interaction,
        channel     : GuildChannel | None = None,
    ) -> None:
        await run_server_channel_duplicate(interaction, channel)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server partnership add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @partnership.command(name = "add", description = "Add a server partnership.")
    @describe(
        server_picture     = "The server's picture.",
        server_name        = "The server's name.",
        server_description = "The server's description.",
        server_owner       = "The server's owner.",
        server_link        = "The server's invite link. Must be a valid Discord invite of the form `https://discord.gg/example`.",
    )
    @director_cmd()
    @rename(
        server_picture     = "server-picture",
        server_name        = "server-name",
        server_description = "server-description",
        server_owner       = "server-owner",
        server_link        = "server-link",
    )
    async def cmd_server_partnerships_add(
        self,
        interaction        : Interaction,
        server_picture     : Attachment,
        server_name        : str,
        server_description : str,
        server_owner       : User,
        server_link        : str,
    ) -> None:
        await run_server_partnership_add(
            self.bot,
            interaction,
            server_name,
            server_picture,
            server_description,
            server_owner,
            server_link,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server partnership update
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @partnership.command(name = "update", description = "Update an existing server partnership.")
    @describe(
        server_name        = "The name of the server to update.",
        server_picture     = "The server's new picture.",
        new_server_name    = "The server's new name.",
        server_description = "The server's new description.",
        server_owner       = "The server's new owner.",
        server_link        = "The server's new invite link. Must be a valid Discord invite of the form `https://discord.gg/example`.",
    )
    @rename(
        server_name        = "server-name",
        server_picture     = "server-picture",
        new_server_name    = "new-server-name",
        server_description = "server-description",
        server_owner       = "server-owner",
        server_link        = "server-link",
    )
    @autocomplete(server_name = server_name_autocomplete)
    @director_cmd()
    async def cmd_server_partnerships_update(
        self,
        interaction        : Interaction,
        server_name        : str,
        server_picture     : Attachment | None = None,
        new_server_name    : str        | None = None,
        server_description : str        | None = None,
        server_owner       : User       | None = None,
        server_link        : str        | None = None,
    ) -> None:
        await run_server_partnership_update(
            self.bot,
            interaction,
            server_name,
            server_picture,
            new_server_name,
            server_description,
            server_owner,
            server_link,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /server partnership remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @partnership.command(name = "remove", description = "Remove a server partnership.")
    @describe(server_name = "The name of the server to remove.")
    @rename(server_name = "server-name")
    @autocomplete(server_name = server_name_autocomplete)
    @director_cmd()
    async def cmd_server_partnerships_remove(
        self,
        interaction : Interaction,
        server_name : str,
    ) -> None:
        await run_server_partnership_remove(
            self.bot,
            interaction,
            server_name,
        )

async def setup(bot : Cordex) -> None:
    cog = ServerCommands(bot)
    await bot.add_cog(cog)
